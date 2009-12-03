"""
"""

from amuse.support.data import values
from amuse.support.units import si

import numpy

class BasicUniqueKeyGenerator(object):
    
    def __init__(self):
        self.lowest_unique_key = 1
    
    def next(self):
        new_key = self.lowest_unique_key
        self.lowest_unique_key += 1
        return new_key
        
    def next_set_of_keys(self, length):
        from_key = self.lowest_unique_key
        to_key = from_key + lenght;
        self.lowest_unique_key += length
        return numpy.arrange(from_key, to_key)
        
UniqueKeyGenerator = BasicUniqueKeyGenerator()

class AttributeValues(object):
    __slots__ = ["attribute", "values", "unit", "model_times"]
    
    def __init__(self, attribute, unit, values = None,  model_times = None, length = None):
        self.attribute = attribute
        self.unit = unit
        self.model_times = model_times
        if values is None:
            self.values = numpy.zeros(length)
        else:
            self.values = values
        
    def copy(self):
        return AttributeValues(self.attribute, self.unit, self.values.copy(), self.model_times)
        
class AttributeList(object):
    
    def __init__(self, particle_keys, attributes = [], lists_of_values = [], units = [], model_times = None):
        
        if len(lists_of_values) != len(attributes):
            raise Exception(
                "you need to provide the same number of value list as attributes, found {0} attributes and {1} list of values".format(
                    len(attributes), len(lists_of_values)
                )
            )
        if len(attributes) != len(units):
             raise Exception(
                "you need to provide the same number of value list as attributes, found {0} attributes and {1} list of values".format(
                    len(attributes), len(units)
                )
            )
        if len(lists_of_values) > 0 and len(particle_keys) != len(lists_of_values[0]):
            raise Exception(
                "you need to provide the same number of values as particles, found {0} values and {1} particles".format(
                    len(lists_of_values[0]), len(particle_keys)
                )
            )
        
        
        model_times = self._convert_model_times(model_times, len(particle_keys))
        
        self.mapping_from_attribute_to_values_and_unit = {}
        for attribute, values, unit in zip(attributes, lists_of_values, units):
            self.mapping_from_attribute_to_values_and_unit[attribute] = AttributeValues(
                attribute,
                unit,
                values,
                model_times
            )
        
        self.particle_keys = numpy.array(particle_keys)
        self.reindex()
        
    def copy(self):
        copy = AttributeList([])
        copy.mapping_from_particle_to_index = self.mapping_from_particle_to_index.copy()
        copy.particle_keys = self.particle_keys.copy()
        for attribute, attribute_values in self.mapping_from_attribute_to_values_and_unit.iteritems():
            copy.mapping_from_attribute_to_values_and_unit[attribute] = attribute_values.copy()
        return copy
        
    def get_value_of(self, particle_key, attribute):
        if not attribute in self.mapping_from_attribute_to_values_and_unit:
            raise AttributeError("particle does not have a "+attribute)
        
        attribute_values = self.mapping_from_attribute_to_values_and_unit[attribute]
        
        index = self.mapping_from_particle_to_index[particle_key]
        
        return attribute_values.unit.new_quantity(attribute_values.values[index])
        
    def get_values_of_attributes_of_particle(self, particle_key, attributes):
        
        index = self.mapping_from_particle_to_index[particle_key]
        result = []
        for attribute in attribute:
            if not attribute in self.mapping_from_attribute_to_values_and_unit:
                raise AttributeError("particle does not have a "+attribute)
            
            attribute_values = self.mapping_from_attribute_to_values_and_unit[attribute]
            
            result.append(attribute_values.values[index] | attribute_values.unit)
        return result
        
    
    def set_value_of(self, particle_key, attribute, quantity):
        index = self.mapping_from_particle_to_index[particle_key]
            
        if index is None:
            raise Exception("particle with key '{0}' is not in this set".format(particle_key))
            
        attribute_values = self.get_attributevalues_for(attribute, quantity.unit)
             
        value_to_set = quantity.value_in(attribute_values.unit)
        attribute_values.values[index] = value_to_set
        
            
    def iter_values_of_particle(self, particle_key):
        index = self.mapping_from_particle_to_index[particle_key]
        for attribute in self.mapping_from_attribute_to_values_and_unit:
            attribute_values = self.mapping_from_attribute_to_values_and_unit[attribute]
            yield attribute, (attribute_values.values[index] | attribute_values.unit)
    
    
            
    def iter_values_of(self, attribute):
        if not attribute in self.mapping_from_attribute_to_values_and_unit:
            return
            
        attribute_values = self.mapping_from_attribute_to_values_and_unit[attribute]
        values = attribute_values.values
        unit = attribute_values.unit
        particles = self.particle_keys
        
        for index in range(len(self.particle_keys)):
            yield particles[i], (values[i] | unit)
            
    def iter_particles_as_views(self):
        class ParticleView(object):
            __slots__=['key', 'index', 'version']
            pass
        
        class AttributeViewProperty(object):
            __slots__ = ['attribute', 'values','unit']
            def __init__(self, list, attribute):
                self.attribute = attribute
                self.values = list.mapping_from_attribute_to_values_and_unit[attribute].values
                self.unit = list.mapping_from_attribute_to_values_and_unit[attribute].unit
            
            def __get__(self, instance, owner):
                return  values.ScalarQuantity(self.values[instance.index] , self.unit)
                
            def __set__(self, instance, value):
                self.values[instance.index] = value.value_in(self.unit)
                
        for attribute in self.mapping_from_attribute_to_values_and_unit:
            setattr(
                ParticleView, 
                attribute, 
                AttributeViewProperty(self, attribute)
            )
            
        index = 0
        for index in range(len(self.particle_keys)):
            p = ParticleView()
            p.index = index
            yield p
            index += 1
            
            
    def iter_particles(self):
        for particle_key in self.particle_keys:
            yield particle_key
    
    def get_indices_of(self, particles):
        mapping_from_particle_to_index = self.mapping_from_particle_to_index 
        result = numpy.zeros(len(particles),dtype='int32')
        #result = [mapping_from_particle_to_index[id(particle)] for particle in particles]
        
        index = 0
        for index, particle_key in enumerate(particles):
            result[index] = mapping_from_particle_to_index[particle_key]
            index += 1
        return result
    
    def get_values_of_particles_in_units(self, particles, attributes, target_units):
        indices = self.get_indices_of(particles)
        results = []
        for attribute, target_unit in zip(attributes, target_units):
            
             attribute_values = self.mapping_from_attribute_to_values_and_unit[attribute]
             value_of_unit_in_target_unit = attribute_values.unit.value_in(target_unit )
             selected_values = attribute_values.values.take(indices)
             if value_of_unit_in_target_unit != 1.0:
                selected_values *= value_of_unit_in_target_unit
             results.append(selected_values)
        
        return results
        
    def get_values_of_all_particles_in_units(self, attributes, target_units):
        results = []
        for attribute, target_unit in zip(attributes, target_units):
             attribute_values = self.mapping_from_attribute_to_values_and_unit[attribute]
             value_of_unit_in_target_unit = attribute_values.unit.value_in(target_unit )
             selected_values = attribute_values.values
             if value_of_unit_in_target_unit != 1.0:
                selected_values = selected_values * value_of_unit_in_target_unit
             results.append(selected_values)
        
        return results
    
    def _convert_model_times(self, model_times, length):
        if not model_times is None and isinstance(model_times, values.ScalarQuantity):
            return model_times.unit.new_quantity(numpy.linspace(model_times.number, model_times.number, length) )
        else:
            return model_times
    
    def set_values_of_particles_in_units(self, particles, attributes, list_of_values_to_set, source_units, model_times = None):
        indices = self.get_indices_of(particles)
        
        model_times = self._convert_model_times(model_times, len(particles))
        
        previous_model_times = None
        results = []
        for attribute, values_to_set, source_unit in zip(attributes, list_of_values_to_set, source_units):
            selected_values = values_to_set
            
            if attribute in self.mapping_from_attribute_to_values_and_unit:
                attribute_values = self.mapping_from_attribute_to_values_and_unit[attribute]
            else:
                attribute_values = AttributeValues(
                   attribute,
                   source_unit,
                   length = len(self.particle_keys)
                )
                self.mapping_from_attribute_to_values_and_unit[attribute] = attribute_values
                 
            value_of_source_unit_in_list_unit = source_unit.value_in(attribute_values.unit)
            if value_of_source_unit_in_list_unit != 1.0:
                selected_values *= value_of_source_unit_in_list_unit 
             
            attribute_values.values.put(indices, selected_values)
            if not model_times is None:
                if not previous_model_times is attribute_values.model_times:
                    attribute_values.model_times.put(indices, model_times)
                    previous_model_times = attribute_values.model_times
            
        return results
        
             
    def merge_into(self, others):
        source_attributes = []
        source_units = []
        source_valeus = []
        for attribute in self.mapping_from_attribute_to_values_and_unit:
            attribute_values = self.mapping_from_attribute_to_values_and_unit[attribute]
            source_attributes.append(attribute_values.attribute)
            source_values.append(attribute_values.values)
            source_units.append(attribute_values.unit)
            
                
        other.set_values_of_particles_in_units(self.particle_keys, source_attributes, source_values, source_units)
        
    def remove_particles(self, particles):
        indices = self.get_indices_of(particles)
        
        mapping_from_attribute_to_values_and_unit = self.mapping_from_attribute_to_values_and_unit.copy()
        for attribute, attribute_values in mapping_from_attribute_to_values_and_unit.iteritems():
            attribute_values.values = numpy.delete(attribute_values.values,indices)
        
        self.particle_keys = numpy.delete(self.particle_keys,indices)
        self.reindex()
        
    def reindex(self):
        d = {}
        index = 0
        for particle_key in self.particle_keys:
            d[particle_key] = index
            index += 1
          
        self.mapping_from_particle_to_index = d
        
    def get_attribute_as_vector(self, particle_key, names_of_the_scalar_attributes):
        index = self.mapping_from_particle_to_index[particle_key]
        vector = []
        for i, attribute in enumerate(names_of_the_scalar_attributes):
            attribute_values = self.mapping_from_attribute_to_values_and_unit[attribute]
            vector.append(attribute_values.values[index])
            unit_of_the_vector = attribute_values.unit
        return vector | unit_of_the_vector
        
    def get_attributevalues_for(self, attribute, unit):
        if attribute in self.mapping_from_attribute_to_values_and_unit:
            attribute_values = self.mapping_from_attribute_to_values_and_unit[attribute]
        else:
            attribute_values = AttributeValues(
                attribute,
                unit,
                length = len(self.particle_keys)
            )
            self.mapping_from_attribute_to_values_and_unit[attribute] = attribute_values
        return attribute_values
        
    def set_attribute_as_vector(self, particle_key, names_of_the_scalar_attributes, quantity):
        index = self.mapping_from_particle_to_index[particle_key]
        vector = []
        for i, attribute  in enumerate(names_of_the_scalar_attributes):
            attribute_values = self.get_attributevalues_for(attribute, quantity.unit)
        
            value_to_set = quantity[i].value_in(attribute_values.unit)
            attribute_values.values[index] = value_to_set
            
    def attributes(self):
        return set(self.mapping_from_attribute_to_values_and_unit.keys())
    
    def __str__(self):
        attributes = sorted(self.attributes())
        
        columns = map(lambda x : [x], attributes)
        columns.insert(0,['id'])
        
        for index, attribute in enumerate(attributes):
            attribute_values = self.mapping_from_attribute_to_values_and_unit[attribute]
            column = columns[index + 1]
            column.append(str(attribute_values.unit))
            column.append('========')
            if len(attribute_values.values) > 40:
                values_to_show = list(attribute_values.values[:20])
                values_to_show.append(attribute_values.values[-20:])
            else:
                values_to_show = attribute_values.values
            
            for value in values_to_show:
                column.append(str(value))
            column.append('========')
            
        column = columns[0]
        column.append("-")
        column.append('========')
        if len(self.particle_keys) > 40:
            values_to_show = list(self.particle_keys[:20])
            values_to_show.append(self.particle_keys[-20:])
        else:
            values_to_show = self.particle_keys
                    
        for value in values_to_show:
            column.append(str(value))
            
        column.append('========')
            
        rows = []
        for i in range(len(columns[0])):
            row = [x[i] for x in columns]
            rows.append(row)
            
        lines = map(lambda  x : '\t'.join(x), rows)
        return '\n'.join(lines)
        
    def get_attribute_as_quantity(self, attribute):
        if not attribute in self.mapping_from_attribute_to_values_and_unit:
            raise AttributeError("unknown attribute '{0}'".format(attribute))
        
        attribute_values = self.mapping_from_attribute_to_values_and_unit[attribute]
        
        return attribute_values.unit.new_quantity(attribute_values.values)
        
    def set_attribute_as_quantity(self, attribute, quantity):
        if not isinstance(quantity, values.VectorQuantity):
            raise AttributeError("can only set a vector of values")
        
        if not len(quantity) == len(self.particle_keys):
            raise AttributeError("vector of values must have the same length as the particles in the system")
            
        if not (
            isinstance(quantity._number[0], int) or isinstance(quantity._number[0], float)
            ):
            raise AttributeError("values must be ints or floats")
            
        attribute_values = self.get_attributevalues_for(attribute, quantity.unit)
        attribute_values.values = numpy.array(quantity._number)
        attribute_values.unit = quantity.unit
        
        
        
        
    def get_attributes_as_vector_quantities(self, attributes):
        for attribute in attributes:
            if not attribute in self.mapping_from_attribute_to_values_and_unit:
                raise AttributeError("unknown attribute '{0}'".format(attribute))
        
        unit_of_the_values = None
        results = []
        for attribute in attributes:
            attribute_values = self.mapping_from_attribute_to_values_and_unit[attribute]
            if unit_of_the_values is None:
                unit_of_the_values = attribute_values.unit
                results.append(attribute_values.values)
            else:
                conversion_factor = attribute_values.unit.value_in(unit_of_the_values)
                if conversion_factor != 1.0:
                    results.append(attribute_values.values * conversion_factor)
                else:                    
                    results.append(attribute_values.values)
        
        results = numpy.dstack(results)[0]
        return unit_of_the_values.new_quantity(results)
        
    def set_model_time(self, value): 
        model_times = self._convert_model_times(value, len(self.particle_keys))
        for attribute_values in self.mapping_from_attribute_to_values_and_unit.values():
            attribute_values.model_times = model_times
    
class Particles(object):
    class ScalarProperty(object):
        
        def  __init__(self, attribute_name):
            self.attribute_name = attribute_name
        
        def __get__(self, instance, owner):
            if instance == None:
                return self
            else:
                return instance.attributelist.get_attribute_as_quantity(self.attribute_name)
        
        def __set__(self, instance, value):
            if instance == None:
                return self
            else:
                return instance.attributelist.set_attribute_as_quantity(self.attribute_name, value)
                
    class VectorProperty(object):
        
        def  __init__(self, attribute_names):
            self.attribute_names = attribute_names
        
        def __get__(self, instance, owner):
            if instance == None:
                return self
            else:
                return instance.attributelist.get_attributes_as_vector_quantities(self.attribute_names)
                
    class ModelTimeProperty(object):
        
        def __get__(self, instance, owner):
            if instance == None:
                return self
            else:
                raise Exception("TBD")
                
            
        def __set__(self, instance, value):
            if instance == None:
                return self
            else:
                instance.attributelist.set_model_time(value)
        
    
    """A set of particle objects"""
    def __init__(self, size = 0):
        self.particle_keys = [Particle(i+1, self) for i in range(size)]
        self.attributelist = AttributeList(self.particle_keys)
        self.previous = None
    
        
    def __iter__(self):
        return self.attributelist.iter_particles()

    def __getitem__(self, index):
        return self.particle_keys[index]
        
    def __len__(self):
        return len(self.particle_keys)
        
    def savepoint(self):
        instance = type(self)()
        instance.particle_keys = self.particle_keys
        instance.attributelist = self.attributelist.copy()
        instance.previous = self.previous
        self.previous = instance
        
    def iter_history(self):
        current = self
        while not current is None:
            yield current
            current = current.previous
    
    @property
    def history(self):
        return reversed(list(self.iter_history()))
        
    def get_timeline_of_attribute(self, particle_key, attribute):
        timeline = []
        for x in self.history:
            timeline.append((None, x.attributelist.get_value_of(particle_key, attribute)))
        return timeline

    model_time = ModelTimeProperty()
            
    
            
        
class Stars(Particles):
    
    mass = Particles.ScalarProperty("mass")
    
    radius = Particles.ScalarProperty("radius")
    
    x = Particles.ScalarProperty("x")
    y = Particles.ScalarProperty("y")
    z = Particles.ScalarProperty("z")
    
    vx = Particles.ScalarProperty("vx")
    vy = Particles.ScalarProperty("vy")
    vz = Particles.ScalarProperty("vz")
    
    position = Particles.VectorProperty(["x","y","z"])
    velocity = Particles.VectorProperty(["vx","vy","vz"])
    
    
    def center_of_mass(self):
        masses, x_values, y_values, z_values = self.attributelist.get_values_of_all_particles_in_units(["mass","x","y","z"],[si.kg, si.m, si.m, si.m])
        total_mass = numpy.sum(masses)
        massx = numpy.sum(masses * x_values)
        massy = numpy.sum(masses * y_values)
        massz = numpy.sum(masses * z_values)
        position = numpy.array([massx, massy, massz])

        return values.new_quantity(position / total_mass, si.m)
    
    
    def center_of_mass_velocity(self):
        masses, x_values, y_values, z_values = self.attributelist.get_values_of_all_particles_in_units(["mass","vx","vy","vz"],[si.kg, si.m / si.s, si.m / si.s, si.m / si.s])
        total_mass = numpy.sum(masses)
        massx = numpy.sum(masses * x_values)
        massy = numpy.sum(masses * y_values)
        massz = numpy.sum(masses * z_values)
        position = numpy.array([massx, massy, massz])

        return values.new_quantity(position / total_mass, si.m / si.s)
        
        
        
            
        
            
class VectorAttribute(object):
    def __init__(self, names_of_the_scalar_components):
        self.names_of_the_scalar_components = names_of_the_scalar_components
        
    def __get__(self, instance, owner):
        if instance is None:
            return self
        else:
            return instance.set.attributelist.get_attribute_as_vector(instance, self.names_of_the_scalar_components)
    
    
    def __set__(self, instance, quantity):
        instance.set.attributelist.set_attribute_as_vector(instance, self.names_of_the_scalar_components, quantity)
            
class Particle(object):
    """A physical object or a physical region simulated as a 
    physical object (cload particle).
    
    All attributes defined on a particle are specific for 
    that particle (for example mass or position). A particle contains 
    a set of attributes, some attributes are *generic* and applicaple
    for multiple modules. Other attributes are *specific* and are 
    only applicable for a single module.
    """
    __slots__ = ["id", "attributes", "set"]
    
    position = VectorAttribute(("x","y","z"))
    velocity = VectorAttribute(("vx","vy","vz"))
    
    def __init__(self, id = -1, set = None, **keyword_arguments):
        object.__setattr__(self, "id", id)
        object.__setattr__(self, "attributes", {})
        object.__setattr__(self, "set", set)
        
        for attribute_name in keyword_arguments:
            attribute_value = keyword_arguments[attribute_name]
            setattr(self, attribute_name, attribute_value)
            
    def __setattr__(self, name_of_the_attribute, new_value_for_the_attribute):
        if name_of_the_attribute == 'position':
            type(self).position.__set__(self, new_value_for_the_attribute)
            return
        if name_of_the_attribute == 'velocity':
            type(self).velocity.__set__(self, new_value_for_the_attribute)
            return
            
        if isinstance(new_value_for_the_attribute, values.Quantity):
            self.set.attributelist.set_value_of(self, name_of_the_attribute, new_value_for_the_attribute)
        else:
            raise Exception("attribute "+name_of_the_attribute+" does not have a valid value, values must have a unit")
    
    def __getattr__(self, name_of_the_attribute):
         return self.set.attributelist.get_value_of(self, name_of_the_attribute)
         
                
    def __str__(self):
        output = 'Particle '
        output += str(self.id)
        output += ''
        output += '\n'
        for name, value in self.set.attributelist.iter_values_of_particle(self):
            output += name
            output += ': {'
            output += str(value)
            output += '}, '
            output += '\n'
        return output
        
    def set_value_of_attribute(self, attribute, value, time = None):
        getattr(self, attribute).set_value_at_time(time, values[index])
        
    def set_default(self, attribute, quantity):
        if not attribute in self.set.attributelist.attributes():
            self.set.attributelist.set_value_of(self, attribute, quantity)
            
class Star(Particle):
    pass
