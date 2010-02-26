from amuse.support.data import parameters
from amuse.support.data.core import Particles, ParticleInformationChannel, Particle
from amuse.support.data.core import AttributeStorage
import numpy

from amuse.support.units import nbody_system
from amuse.support.core import late

import inspect

class ParticleMappingMethod(object):
    def __init__(self, method, mapping = (), attribute_names = None):
        self.method = method
        self.mapping = mapping
        
        if attribute_names is None:
            self._attribute_names = []
        else:
            self._attribute_names = attribute_names
            
        self.from_parameter_name_to_attribute_name = {}
        self.from_attribute_name_to_parameter_name = {}
        
        for parameter_name, attribute_name in self.mapping:
            from_parameter_name_to_attribute_name[parameter_name] = attribute_name
            from_attribute_name_to_parameter_name[attribute_name] = parameter_name
            self._attribute_names.append(attribute_name)
     
    
    @late
    def name_of_the_indexing_parameter(self):
        return 'index_of_the_particle'
        
    @late
    def method_is_legacy(self):
        return hasattr(self.method, 'specification')
        
        
    @late
    def method_is_code(self):
        return hasattr(self.method, 'method_input_argument_names')
    
    
    @late
    def legacy_specification(self):
        if self.method_is_code:
            return self.method.legacy_specification
        elif self.method_is_legacy:
            return self.method.specification
        else:
            return None
    
    @late
    def method_input_argument_names(self):
        if self.method_is_code:
            return self.method.method_input_argument_names
        elif self.method_is_legacy:
            return map(lambda x : x.name , self.method.specification.input_parameters)
        else:
            args = inspect.getargspec(self.method).args
            if args:
                if args[0] == 'self' or args[0] == 'cls':
                    return args[1:]
            return args
            
    @late
    def method_output_argument_names(self):
        if self.method_is_code:
            return self.method.method_output_argument_names
        elif self.method_is_legacy:
            return map(lambda x : x.name , self.method.specification.output_parameters)
        else:
            return ()
            

class ParticleGetAttributesMethod(ParticleMappingMethod):
    
    def __init__(self, method, mapping=(), attribute_names = None):
        ParticleMappingMethod.__init__(self, method, mapping, attribute_names)

    @late
    def attribute_names(self):
        result = []
        
        if len(self.method_output_argument_names) > 0:
            for x in self.method_output_argument_names:
                if x == self.name_of_the_indexing_parameter:
                    continue
                if x in self.from_parameter_name_to_attribute_name:
                    result.append(self.from_parameter_name_to_attribute_name[x])
                else:
                    result.append(x)
            return result
        else:
            return self._attribute_names
            
        
    def intersection(self, attributes):
        result = set([])
        names = set(self.attribute_names)
        for x in attributes:
            if x in names:
                result.add(x)
        return result
    
    def apply(self, indices, attributes_to_return):
        
        if len(indices) > 1: 
            if self.method_is_legacy and not self.method.specification.can_handle_array:
                raise Exception(
                    "getter method {0} cannot handle arrays".format(self.method)
                )
            elif self.method_is_code:
                if not self.method.legacy_specification is None:
                    if not self.method.legacy_specification.can_handle_array:
                        raise Exception(
                            "getter method {0} cannot handle arrays".format(self.method)
                        )
                
        return_value = self.method(indices)
        if len(self.attribute_names) == 1:
            return_value = (return_value,)
        set_of_attributes_to_return = set(attributes_to_return)
        
        result = {}
        for value, attribute in zip(return_value, self.attribute_names):
            if attribute in set_of_attributes_to_return:
                result[attribute] = value
                
        return result
    
class ParticleSetAttributesMethod(ParticleMappingMethod):
    
    def __init__(self, method, mapping=(), attribute_names = None):
        ParticleMappingMethod.__init__(self, method, mapping, attribute_names)
    

    @late
    def attribute_names(self):
        result = []
        for x in self.method_input_argument_names:
            if x == self.name_of_the_indexing_parameter:
                continue

            if x in self.from_parameter_name_to_attribute_name:
                result.append(self.from_parameter_name_to_attribute_name[x])
            else:
                result.append(x)
        return result
    
    @late
    def names_to_index(self):
        result = {}
        for index, name in enumerate(self.attribute_names):
            result[name] = index
        return result
        
    def intersection(self, attributes):
        result = set([])
        names = set(self.attribute_names)
        for x in attributes:
            if x in names:
                result.add(x)
        if len(result) != len(names):
            return set([])
        return result
        
    
    def apply(self, indices, attributes = [], values = []):

        list_arguments = self.convert_attributes_and_values_to_list_arguments(attributes, values)
        list_arguments.insert(0, indices)
        self.method(*list_arguments)
    
    
    def convert_attributes_and_values_to_list_arguments(self, attributes, values):
        list_arguments = [0] * (len(self.attribute_names))
        
        names_to_index = self.names_to_index
        for attribute, quantity in zip(attributes, values):
            if attribute in names_to_index:
                index = names_to_index[attribute]
                list_arguments[index] = quantity
        
        return list_arguments


class NewParticleMethod(ParticleSetAttributesMethod):
    
    def __init__(self,  method,  mapping=(), attribute_names = None):
        ParticleSetAttributesMethod.__init__(self, method,mapping, attribute_names)

    def apply(self, attributes = [], values = []):
        
        list_arguments = self.convert_attributes_and_values_to_list_arguments(attributes, values)
        
        indices = self.method(*list_arguments)
        
        return indices
        
class ParticleQueryMethod(object):
    def __init__(self, method, names = (), public_name = None):
        self.method = method
        self.name_of_the_out_parameters = names
        self.public_name = public_name

    def apply(self, particles):
            
        indices = self.method()
        
        keys = particles._private.attribute_storage._get_keys_for_indices_in_the_code(indices)
        
        return particles._subset(keys)
    

                

class InCodeAttributeStorage(AttributeStorage):
       
    def __init__(self, 
            code_interface, 
            new_particle_method, 
            delete_particle_method, 
            number_of_particles_method, 
            setters,
            getters,
            name_of_the_index):
        
        self.code_interface = code_interface
        
        self.mapping_from_particle_key_to_index_in_the_code = {}
        self.mapping_from_index_in_the_code_to_particle_key = {}
        self.particle_keys = []
        
        self._get_number_of_particles = number_of_particles_method
        self._delete_particle = delete_particle_method
        self.new_particle_method = new_particle_method
        self.getters = getters
        self.setters = setters
        
        self.attributes = set([])
        for x in self.getters:
            self.attributes |= set(x.attribute_names)
        for x in self.setters:
            self.attributes |= set(x.attribute_names)
        
        for x in self.getters:
            x.name_of_the_indexing_parameter = name_of_the_index

        for x in self.setters:
            x.name_of_the_indexing_parameter = name_of_the_index
                    
    def __len__(self):
        return self._get_number_of_particles()
            
    def select_getters_for(self, attributes):
        set_of_attributes = set(attributes)
        result = []
        for particle_method in self.getters:
            provided_attributes = particle_method.intersection(set_of_attributes)
            if provided_attributes:
                result.append(particle_method)
                set_of_attributes -= provided_attributes
            
        if set_of_attributes:
            raise Exception("Do not have attributes {0}".format(sorted(set_of_attributes)))
        return result
        
    
    def select_setters_for(self, attributes):
        set_of_attributes = set(attributes)
        result = []
        for particle_method in self.setters:
            provided_attributes = particle_method.intersection(set_of_attributes)
            if provided_attributes:
                result.append(particle_method)
                set_of_attributes -= provided_attributes
                
        if set_of_attributes:
            raise Exception("Cannot set attributes {0}".format(sorted(set_of_attributes)))
            
        return result
        
            
    def _set_particles(self, keys, attributes = [], values = []):
        
        indices = self.new_particle_method.apply( attributes, values)
        
        
        if len(self.particle_keys) > 0:
            self.particle_keys = numpy.concatenate((self.particle_keys, numpy.array(list(keys))))
        else:
            self.particle_keys = numpy.array(keys)

        index = 0
        for key in keys:
            self.mapping_from_particle_key_to_index_in_the_code[key] = indices[index]
            self.mapping_from_index_in_the_code_to_particle_key[indices[index]] = key
            index = index + 1
            
        
        
    def get_indices_of(self, keys):
        indices_in_the_code = []
        if keys is None:
            keys = self.particle_keys
            
        for particle_key in keys:
            indices_in_the_code.append(self.mapping_from_particle_key_to_index_in_the_code[particle_key])
            
        return indices_in_the_code
        
   
    def get_key_indices_of(self, keys):
        result = []
        if keys is None:
            keys = self.particle_keys
        
        keys_set = set(keys)
        for index in range(len(self.particle_keys)):
           key = self.particle_keys[index]
           if key in keys_set:
               result.append(index)
          
        return result
         
    def _get_values(self, keys, attributes):
        indices_in_the_code = self.get_indices_of(keys)
        
        mapping_from_attribute_to_result = {}
        
        for getter in self.select_getters_for(attributes):
            result = getter.apply(indices_in_the_code, attributes)
            mapping_from_attribute_to_result.update(result)
            
        results = []
        for attribute in attributes:
            results.append(mapping_from_attribute_to_result[attribute])
        return results
        
    def _set_values(self, keys, attributes, values):
        indices_in_the_code = self.get_indices_of(keys)
    
        for setter in self.select_setters_for(attributes):
            setter.apply(indices_in_the_code, attributes, values)
    
    def _remove_particles(self, keys):
        indices_in_the_code = self.get_indices_of(keys)
        
        self.delete_particle_method(indices_in_the_code)
        
        d = self.mapping_from_particle_key_to_index_in_the_code
        for key in keys:
            del d[key]
        
        for i in indices_in_the_code:
            del self.mapping_from_index_in_the_code_to_particle_key[i]
        
         
        indices_to_delete = self.get_key_indices_of(keys)
        self.particle_keys =  numpy.delete(self.particle_keys, indices_to_delete)
            
    def _get_attributes(self):
        return self.attributes
    
    def _state_attributes(self):
        return self._get_attributes()
        
    def _get_keys(self):
        return self.particle_keys

    def _has_key(self, key):
        return key in self.mapping_from_particle_key_to_index_in_the_code
        
    def _get_keys_for_indices_in_the_code(self, indices):
        result = []
        for i in indices:
            result.append(self.mapping_from_index_in_the_code_to_particle_key[i])
        return result
    
