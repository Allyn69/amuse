from amuse.support.data import values
from amuse.support.data.values import Quantity, new_quantity
from amuse.support.units import constants
from amuse.support.units import units
from amuse.support.core import CompositeDictionary

import numpy
import random
import inspect

class BasicUniqueKeyGenerator(object):
    
    def __init__(self):
        self.lowest_unique_key = 1
    
    def next(self):
        new_key = self.lowest_unique_key
        self.lowest_unique_key += 1
        return new_key
        
    def next_set_of_keys(self, length):
        if length == 0:
            return  []
            
        from_key = self.lowest_unique_key
        to_key = from_key + length;
        self.lowest_unique_key += length
        return numpy.arange(from_key, to_key)
        

class RandomNumberUniqueKeyGenerator(object):
    DEFAULT_NUMBER_OF_BITS = 64
    
    def __init__(self, number_of_bits = DEFAULT_NUMBER_OF_BITS):
        if number_of_bits > 64:
            raise Exception("number of bits is larger than 64, this is currently unsupported!")
        self.number_of_bits = number_of_bits
        
    def next(self):
        return numpy.array([random.getrandbits(self.number_of_bits)], dtype='uint64')[0]
        
    def next_set_of_keys(self, length):
        if length == 0:
            return  []
        return numpy.array([random.getrandbits(self.number_of_bits) for i in range(length)], dtype='uint64')
        
UniqueKeyGenerator = RandomNumberUniqueKeyGenerator()

class AttributeValues(object):
    __slots__ = ["attribute", "values", "unit", "model_times"]
    
    def __init__(self, attribute, unit, values = None,  model_times = None, length = None):
        self.attribute = attribute
        self.unit = unit
        self.model_times = model_times
        if values is None:
            self.values = numpy.zeros(length, dtype = self.unit.dtype)
        else:
            self.values = values
        
    def copy(self):
        return AttributeValues(self.attribute, self.unit, self.values.copy(), self.model_times)


class AttributeStorage(object):
    
    def _set_particles(self, keys, attributes = [], values = []):
        pass
        
    def _remove_particles(self, keys):
        pass
        
    def _get_values(self, particles, attributes):
        pass
        
    def _set_values(self, particles, attributes, list_of_values_to_set):
        pass
        
    def _set_particles(self, keys, attributes = [], values = []):
        pass
        
    def _get_attributes(self):
        pass
    
    def _has_key(self, key):
        return False
        
    def _get_keys(self):
        return []
        
    def __len__(self):
        return 0
        
class InMemoryAttributeStorage(AttributeStorage):
    
    def __init__(self):
        self.model_times = None
        self.mapping_from_attribute_to_values_and_unit = {}
        self.mapping_from_particle_to_index = {}
        self.particle_keys = []

    def _set_particles(self, keys, attributes = [], values = []):
        if len(values) != len(attributes):
            raise Exception(
                "you need to provide the same number of value list as attributes, found {0} attributes and {1} list of values".format(
                    len(attributes), len(values)
                )
            )
        if len(values) > 0 and len(keys) != len(values[0]):
            raise Exception(
                "you need to provide the same number of values as particles, found {0} values and {1} particles".format(
                    len(values[0]), len(keys)
                )
            )
        
        if len(self.particle_keys) > 0:
            self.append_to_storage(keys, attributes, values)
        else:
            self.setup_storage(keys, attributes, values)
            
    def setup_storage(self, keys, attributes, values):
        self.mapping_from_attribute_to_values_and_unit = {}
        for attribute, quantity in zip(attributes, values):
            self.mapping_from_attribute_to_values_and_unit[attribute] = AttributeValues(
                attribute,
                quantity.unit,
                quantity.number,
                None
            )
         
        self.particle_keys = numpy.array(keys, dtype='uint64')

        self.reindex()
    
    def append_to_storage(self, keys, attributes, values):
        for attribute, values_to_set in zip(attributes, values):
            if attribute in self.mapping_from_attribute_to_values_and_unit:
                attribute_values = self.mapping_from_attribute_to_values_and_unit[attribute]
            else:
                attribute_values = AttributeValues(
                    attribute,
                    values_to_set.unit,
                    length = len(self.particle_keys)
                )
            
                self.mapping_from_attribute_to_values_and_unit[attribute] = attribute_values
            values_in_the_right_units = values_to_set.value_in(attribute_values.unit)
            attribute_values.values = numpy.concatenate((attribute_values.values, values_in_the_right_units))
        
        old_length = len(self.particle_keys)
        for attribute_values in self.mapping_from_attribute_to_values_and_unit.values():
            zeros_for_concatenation = numpy.zeros(len(keys), dtype=attribute_values.unit.dtype)
            if len(attribute_values.values) == old_length:
                attribute_values.values = numpy.concatenate((attribute_values.values, zeros_for_concatenation))
        
                
        index = len(self.particle_keys)

        self.particle_keys = numpy.concatenate((self.particle_keys,  numpy.array(list(keys), dtype='uint64')))

        for particle_key in keys:
            self.mapping_from_particle_to_index[particle_key] = index
            index += 1
            
    def _get_values(self, particles, attributes):
        indices = self.get_indices_of(particles)
            
        results = []
        for attribute in attributes:
             attribute_values = self.mapping_from_attribute_to_values_and_unit[attribute]
             if indices is None:
                 selected_values = attribute_values.values
             else:
                 selected_values = attribute_values.values.take(indices)
             results.append(attribute_values.unit.new_quantity(selected_values))
        
        return results
        
    def _set_values(self, particles, attributes, list_of_values_to_set, model_times = None):
        indices = self.get_indices_of(particles)
        
        model_times = self._convert_model_times(model_times, len(indices))
        
        previous_model_times = None
        if list_of_values_to_set is None:
            for attribute in attributes:
                if attribute in self.mapping_from_attribute_to_values_and_unit:
                    attribute_values = self.mapping_from_attribute_to_values_and_unit[attribute]
                else:
                    raise Exception("unknown attribute '{0}'".format(attribute))
                     
                selected_values = numpy.zeros(len(indices), dtype=attribute_values.values.dtype)
                
                attribute_values.values.put(indices, selected_values)
            return
            
        for attribute, values_to_set in zip(attributes, list_of_values_to_set):
            if attribute in self.mapping_from_attribute_to_values_and_unit:
                attribute_values = self.mapping_from_attribute_to_values_and_unit[attribute]
            else:
                attribute_values = AttributeValues(
                   attribute,
                   values_to_set.unit,
                   length = len(self.particle_keys)
                )
                self.mapping_from_attribute_to_values_and_unit[attribute] = attribute_values
                 
            selected_values = values_to_set.value_in(attribute_values.unit)
            attribute_values.values.put(indices, selected_values)
            if not model_times is None:
                if not previous_model_times is attribute_values.model_times:
                    attribute_values.model_times.put(indices, model_times)
                    previous_model_times = attribute_values.model_times
            
    
    
    def _get_attributes(self):
        return sorted(self.mapping_from_attribute_to_values_and_unit.keys())
    
    
    def _has_key(self, key):
        return key in self.mapping_from_particle_to_index
        
    def _get_keys(self):
        return self.particle_keys
        
    def __len__(self):
        return len(self.particle_keys)
        
    def copy(self):
        copy = InMemoryAttributeStorage()
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
            
   
    def get_indices_of(self, particles):
        if particles is None:
            return numpy.arange(0,len(self.particle_keys))
            
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
             if indices is None:
                 selected_values = attribute_values.values
             else:
                 selected_values = attribute_values.values.take(indices)
             if value_of_unit_in_target_unit != 1.0:
                selected_values *= value_of_unit_in_target_unit
             results.append(selected_values)
        
        return results
        
    
            
    def _convert_model_times(self, model_times, length):
        if not model_times is None and isinstance(model_times, values.ScalarQuantity):
            return model_times.unit.new_quantity(numpy.linspace(model_times.number, model_times.number, length) )
        else:
            return model_times
    
    def set_values_of_particles_in_units(self, particles, attributes, list_of_values_to_set, source_units, model_times = None):
        indices = self.get_indices_of(particles)
        
        model_times = self._convert_model_times(model_times, len(indices))
        
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
        
    def _remove_particles(self, keys):
        indices = self.get_indices_of(keys)
        
        for attribute, attribute_values in self.mapping_from_attribute_to_values_and_unit.iteritems():
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

    def attributes(self):
        return set(self.mapping_from_attribute_to_values_and_unit.keys())
    
    def _state_attributes(self):
        return self.attributes()
        
    def set_model_time(self, value): 
        model_times = self._convert_model_times(value, len(self.particle_keys))
        for attribute_values in self.mapping_from_attribute_to_values_and_unit.values():
            attribute_values.model_times = model_times


class DerivedAttribute(object):

    def get_value_for_particles(self, particles):
        return None
    
    def set_value_for_particles(self, particles, value):
        raise Exception("cannot set value of attribute '{0}'")

    def get_value_for_particle(self, particles, key):
        return None

    def set_value_for_particle(self, particles, key, value):
        raise Exception("cannot set value of attribute '{0}'")

class VectorAttribute(DerivedAttribute):
    
    def  __init__(self, attribute_names):
        self.attribute_names = attribute_names
    
    def get_values_for_particles(self, instance):
        values = instance._get_values(instance._get_keys(), self.attribute_names)
          
        unit_of_the_values = None
        results = []
        for quantity in values:
            if unit_of_the_values is None:
                unit_of_the_values = quantity.unit
            results.append(quantity.value_in(unit_of_the_values))
            
        results = numpy.dstack(results)[0]
        return unit_of_the_values.new_quantity(results)

    def set_values_for_particles(self, instance, value):
        vectors = value.number
        split = numpy.hsplit(vectors,len(self.attribute_names))
        list_of_values = []
        for i in range(len(self.attribute_names)):
            values = value.unit.new_quantity(split[i].reshape(len(split[i])))
            list_of_values.append(values)
            
        instance._set_values(instance._get_keys(), self.attribute_names, list_of_values)
    
    def get_value_for_particle(self, instance,  key):
        values = instance._get_values([key], self.attribute_names)
          
        unit_of_the_values = None
        results = []
        for quantity in values:
            if unit_of_the_values is None:
                unit_of_the_values = quantity.unit
            results.append(quantity.value_in(unit_of_the_values))
            
        results = numpy.dstack(results)[0]
        return unit_of_the_values.new_quantity(results[0])

    def set_value_for_particle(self, instance, key, vector):
        list_of_values = []
        for quantity in vector:
            list_of_values.append(quantity.as_vector_with_length(1))
        instance._set_values([key], self.attribute_names, list_of_values)


    
class CalculatedAttribute(DerivedAttribute):
    
    def  __init__(self, function, attribute_names = None):
        self.function = function
        if attribute_names is None:
            arguments, varargs, kwargs, defaults = inspect.getargspec(function)
            self.attribute_names = arguments 
        else:
            self.attribute_names = attribute_names
    
    def get_values_for_particles(self, instance):
        values = instance._get_values(instance._get_keys(), self.attribute_names)
        return self.function(*values)
    
    def get_value_for_particle(self, instance,  key):
        values = instance._get_values([key], self.attribute_names)
        return self.function(*values)[0]
        

class FunctionAttribute(DerivedAttribute):
    class BoundParticlesFunctionAttribute(object):
        def  __init__(self, function, particles):
            self.function = function
            self.particles = particles
            
        def __call__(self, *list_arguments, **keyword_arguments):
            return self.function(self.particles, *list_arguments, **keyword_arguments)
    
    class BoundParticleFunctionAttribute(object):
        def  __init__(self, function, particles, key):
            self.function = function
            self.particles = particles
            self.key = key
            
        def __call__(self, *list_arguments, **keyword_arguments):
            return self.function(self.particles._get_particle(self.key), *list_arguments, **keyword_arguments)
        
    
    def  __init__(self, particles_function = None, particle_function = None):
        self.particles_function = particles_function
        self.particle_function = particle_function
        
    def get_values_for_particles(self, particles):
        return self.BoundParticlesFunctionAttribute(self.particles_function, particles)
            
   
    def get_value_for_particle(self, particles, key):
        return self.BoundParticleFunctionAttribute(self.particle_function, particles, key)

        
            


class AbstractParticleSet(object):
    """
    Abstract superclass of all sets of particles. 
    This class defines common code for all particle sets.
    
    Particle sets define dynamic attributes. Attributes
    can be set and retrieved on the particles using common python
    syntax. These attributes can only have values with units.
    
    >>> particles = Particles(2)
    >>> particles.mass = [10.0, 20.0] | units.kg
    >>> particles.mass
    quantity<[10.0, 20.0] kg>
    
    >>> particles.mass = 1.0 | units.kg
    >>> particles.mass
    quantity<[1.0, 1.0] kg>
    
    Particle sets can be iterated over. 
    
    >>> particles = Particles(2)
    >>> particles.mass = [10.0, 20.0] | units.kg
    >>> for particle in particles:
    ...     print particle.mass
    ...
    10.0 kg
    20.0 kg
    
    
    Particle sets can be indexed.
    
    >>> particles = Particles(3)
    >>> particles.x = [10.0, 20.0, 30.0] | units.m
    >>> particles[1].x
    quantity<20.0 m>
    
    
    Particle sets can be copied.
    
    >>> particles = Particles(3)
    >>> particles.x = [10.0, 20.0, 30.0] | units.m
    >>> copy = particles.copy()
    >>> particles.x = 2.0 | units.m
    >>> particles.x
    quantity<[2.0, 2.0, 2.0] m>
    >>> copy.x
    quantity<[10.0, 20.0, 30.0] m>
    
    Particle sets can have instance based or global vector attributes.
    A particle set stores a list of scalar values for each attribute.
    Some attributes are more naturally accessed as lists 
    of vector values. Once defined, a particle set can
    convert the scalar values of 2 or more attributes into one
    vector attribute.
    
    >>> particles = Particles(2)
    >>> particles.x = [1.0 , 2.0] | units.m
    >>> particles.y = [3.0 , 4.0] | units.m
    >>> particles.z = [5.0 , 6.0] | units.m
    >>> particles.add_vector_attribute("p", ["x","y","z"])
    >>> particles.p
    quantity<[[ 1.  3.  5.], [ 2.  4.  6.]] m>
    >>> particles.p[0]
    quantity<[1.0, 3.0, 5.0] m>
    >>> particles.position # "position" is a global vector attribute, coupled to x,y,z
    quantity<[[ 1.  3.  5.], [ 2.  4.  6.]] m>
    
    


    """
    GLOBAL_DERIVED_ATTRIBUTES = {}
    
    
    class PrivateProperties(object):
        """
        Defined for superclasses to store private properties.
        A particle-set has ```__setattr__``` defined.
        The ```__setattr__``` function will set all attributes
        of the particles in the set to the specified value(s).
        To be able to define attributes on the set itself we
        use an instance of this class, attributes can be defined as::
        
            self._private.new_attribute = 'new value'
        
        Subclass implementers do not need to
        use the ```object.__setattr__``` syntax.
        
        For documentation about the __setattr__ call please
        see the ```python data model``` documentation on the python
        website.
        """
        pass
        
    def __init__(self, original = None):
        if original is None:
            object.__setattr__(self, "_derived_attributes", CompositeDictionary(self.GLOBAL_DERIVED_ATTRIBUTES))
        else:
            object.__setattr__(self, "_derived_attributes", original._derived_attributes)
        object.__setattr__(self, "_private", self.PrivateProperties())
    
    
    def __getattr__(self, name_of_the_attribute):
        if name_of_the_attribute == 'key':
            return self._get_keys()
        elif name_of_the_attribute in self._derived_attributes:
            return self._derived_attributes[name_of_the_attribute].get_values_for_particles(self)
        else:
            return self._convert_to_particles(self._get_values(self._get_keys(), [name_of_the_attribute])[0])
    
    def __setattr__(self, name_of_the_attribute, value):
        if name_of_the_attribute in self._derived_attributes:
            self._derived_attributes[name_of_the_attribute].set_values_for_particles(self, value)
        else:
            self._set_values(self._get_keys(), [name_of_the_attribute], [self._convert_from_particles(value)])
    
    def _get_value_of_attribute(self, key, attribute):
        if attribute in self._derived_attributes:
            return self._derived_attributes[attribute].get_value_for_particle(self, key)
        else:
            return self._convert_to_particles(self._get_values([key], [attribute])[0])[0]
        
    def _set_value_of_attribute(self, key, attribute, value):
        if attribute in self._derived_attributes:
            return self._derived_attributes[attribute].set_value_for_particle(self, key, value)
        else:
            return self._set_values([key], [attribute], value.as_vector_with_length(1))
            
    def _convert_to_particles(self, x):
        if x.unit.iskey():
            return self._subset(x.number)
        else:
            return x
        
    def _convert_from_particles(self, x):
        if isinstance(x, Quantity):
            return x 
        else:
            return new_quantity( map(lambda y : (-1 if y is None else y.key) , x) , units.object_key)
        
    #
    # Particle storage interface
    #
    
    def _get_values(self, keys, attributes):
        pass
    
    def _set_values(self, keys, attributes, values):
        pass
        
    def _set_particles(self, keys, attributes, values):
        pass
        
    def _remove_particles(self, keys):
        pass
    
    def _get_keys(self):
        return []
        
    def _has_key(self):
        return False
    
    def _get_attributes(self):
        return []
    
    def _get_state_attributes(self):
        return []
    
    def _real_particles(self):
        return self
        
    #
    #
    #
    
    def _values_of_particle(self, key):
        attributes = self._get_attributes()
        keys = [key]
        values = self._get_values(keys, attributes)
        
        for attribute, val in zip(attributes, values):
            yield attribute, val[0]
    
    def add_vector_attribute(self, name_of_the_attribute, name_of_the_components):
        """
        Define a vector attribute, coupling two or more scalar attributes into
        one vector attribute. 
        
        :argument name_of_the_attribute: Name to reference the vector attribute by. 
        :argument name_of_the_components: List of strings, each string a name of a scalar attribute.
        
        >>> particles = Particles(2)
        >>> particles.vx = [1.0 , 2.0] | units.m / units.s
        >>> particles.vy = [3.0 , 4.0] | units.m / units.s
        >>> particles.add_vector_attribute("v", ["vx","vy"])
        >>> particles.v
        quantity<[[ 1.  3.], [ 2.  4.]] m / s>
        
        """
        
        self._derived_attributes[name_of_the_attribute] = VectorAttribute(name_of_the_components)
    
    @classmethod
    def add_global_vector_attribute(cls, name_of_the_attribute, name_of_the_components):
        """
        Define a *global* vector attribute, coupling two or more scalar attributes into
        one vector attribute. The vector will be defined for all particle sets
        created after calling this function.
        
        :argument name_of_the_attribute: Name to reference the vector attribute by. 
        :argument name_of_the_components: List of strings, each string a name of a scalar attribute.
        
        
        >>> particles = Particles(2)
        >>> Particles.add_global_vector_attribute('vel', ['vx','vy'])
        >>> particles.vx = [1.0 , 2.0] | units.m / units.s
        >>> particles.vy = [3.0 , 4.0] | units.m / units.s
        >>> particles.vel
        quantity<[[ 1.  3.], [ 2.  4.]] m / s>
        
        """
        cls.GLOBAL_DERIVED_ATTRIBUTES[name_of_the_attribute] = VectorAttribute(name_of_the_components)
    
    
    def add_calculated_attribute(self, name_of_the_attribute, function, attributes_names = None):
        """
        Define a read-only calculated attribute, values for the attribute are
        calculated using the given function. The functions argument 
        names are interperted as attribute names. For example, if
        the given function is::
        
            def norm(x, y):
                return (x*x + y*y).sqrt()
                
        The attributes "x" and "y" will be retrieved from the particles
        and send to the "norm" function.
        
        The calculated values are not stored on the particles. Values
        are recalculated every time this attribute is accessed.
        
        :argument name_of_the_attribute: Name to reference the attribute by. 
        :argument function: Function to call, when attribute is accessed
          
        
        >>> particles = Particles(2)
        >>> particles.x = [1.0 , 2.0] | units.m 
        >>> particles.y = [3.0 , 4.0] | units.m
        >>> particles.add_calculated_attribute("xy", lambda x, y : x * y)
        >>> print particles.xy
        [3.0, 8.0] m**2
        >>> particles[0].x = 4.0 | units.m
        >>> print particles.xy
        [12.0, 8.0] m**2
        >>> print particles[1].xy
        8.0 m**2
        
        """
        
        self._derived_attributes[name_of_the_attribute] = CalculatedAttribute(function, attributes_names)
    
    
    @classmethod
    def add_global_calculated_attribute(cls, name_of_the_attribute, function, attributes_names = None):
        """
        Define a *global* vector attribute, coupling two or more scalar attributes into
        one vector attribute. The vector will be defined for all particle sets
        created after calling this function.
        
        :argument name_of_the_attribute: Name to reference the vector attribute by. 
        :argument function: Name of the function to call. 
        :argument attributes_names: List of strings, each string a name of a scalar attribute, if None uses argument names.
        
        
        >>> Particles.add_global_calculated_attribute("xy", lambda x, y : x * y)
        >>> particles = Particles(2)
        >>> particles.x = [1.0 , 2.0] | units.m 
        >>> particles.y = [3.0 , 4.0] | units.m
        >>> print particles.xy
        [3.0, 8.0] m**2
        
        """
        cls.GLOBAL_DERIVED_ATTRIBUTES[name_of_the_attribute] = CalculatedAttribute(function, attributes_names)
    
    
    def add_function_attribute(self, name_of_the_attribute, function, function_for_particle = None):
        """
        Define a function attribute, adding a function to the particles
        
        :argument name_of_the_attribute: Name to reference the vector attribute by. 
        :argument function: A function, first argument will be the particles.
        
        >>> particles = Particles(2)
        >>> particles.x = [1.0 , 2.0] | units.m
        >>> def sumx(p):
        ...   return p.x.sum()
        ...
        >>> particles.add_function_attribute("sum_of_x", sumx)
        >>> particles.sum_of_x()
        quantity<3.0 m>

        
        """
        
        self._derived_attributes[name_of_the_attribute] = FunctionAttribute(function, function_for_particle)
        
    
    @classmethod
    def add_global_function_attribute(cls, name_of_the_attribute, function, function_for_particle = None):
        """
        Define a function attribute, adding a function to the particles
        
        :argument name_of_the_attribute: Name to reference the attribute by. 
        :argument function: A function, first argument will be the particles.
        
        >>> def sumx(p):
        ...   return p.x.sum()
        ...
        >>> Particles.add_global_function_attribute("sum_of_x", sumx)
        >>> particles = Particles(2)
        >>> particles.x = [4.0 , 2.0] | units.m
        >>> particles.sum_of_x()
        quantity<6.0 m>

        
        """
        
        cls.GLOBAL_DERIVED_ATTRIBUTES[name_of_the_attribute] = FunctionAttribute(function, function_for_particle)
        
    
    def add_particle_function_attribute(self, name_of_the_attribute, function):
        """
        Define a function working on one particle
        
        :argument name_of_the_attribute: Name to reference the attribute by. 
        :argument function: A function, first argument will be the particle.
        
        >>> def xsquared(p):
        ...   return p.x * p.x
        ...
        >>> particles = Particles(2)
        >>> particles.add_particle_function_attribute("xsquared", xsquared)
        >>> particles.x = [4.0 , 2.0] | units.m
        >>> particles[0].xsquared()
        quantity<16.0 m**2>
        """
        self._derived_attributes[name_of_the_attribute] = FunctionAttribute(None, function)
        
    #
    # public API
    #
    def __iter__(self):
        index = 0
        for key in self._get_keys():
            p = Particle(key, self._real_particles())
            yield p
            index += 1

    def __getitem__(self, index):
        if isinstance(index, slice):
            return ParticlesSubset(self, self._get_keys()[index])
        else:
            return Particle(self._get_keys()[index], self._real_particles())
        
    def __len__(self):
        return len(self._get_keys())
        
    def __str__(self):
        """
        Display string of a particle set.
        
        >>> p0 = Particle(10)
        >>> p1 = Particle(11)
        >>> particles = Particles()
        >>> particles.add_particle(p0) # doctest:+ELLIPSIS
        <amuse.support.data.core.Particle object at ...>
        >>> particles.add_particle(p1) # doctest:+ELLIPSIS
        <amuse.support.data.core.Particle object at ...>
        >>> particles.x = [4.0 , 3.0] | units.m
        >>> particles.y = [5.0 , 2.0] | units.km
        >>> print particles 
                         key            x            y
                           -            m           km
        ====================  ===========  ===========
                          10    4.000e+00    5.000e+00
                          11    3.000e+00    2.000e+00
        ====================  ===========  ===========

        """
        attributes = sorted(self._get_attributes())
                
        format_float = '{0: >11.3e}'.format
        format_str20 = '{0: >20s}'.format
        format_str11 = '{0: >11s}'.format

        columns = map(lambda x : [format_str11(x)], attributes)
        columns.insert(0,[format_str20('key')])
        
        all_values = self._get_values(self._get_keys(), attributes)
        for index, quantity in enumerate(all_values):
            column = columns[index + 1]
            column.append(format_str11(str(quantity.unit)))
            column.append('=' * 11)
            if len(quantity) > 40:
                values_to_show = list(map(format_float,quantity.number[:20]))
                values_to_show.append(format_str11('...'))
                values_to_show.extend(map(format_float,quantity.number[-20:]))
            else:
                values_to_show = map(format_float,quantity.number)
            
            column.extend(values_to_show)
            column.append('=' * 11)
            
        column = columns[0]
        column.append(format_str20("-"))
        column.append('=' * 20)
        particle_keys = self._get_keys()
        if len(particle_keys) > 40:
            values_to_show = list(map(format_str20, particle_keys[:20]))
            values_to_show.append(format_str20('...'))
            values_to_show.extend(map(format_str20, particle_keys[-20:]))
        else:
            values_to_show = map(format_str20,particle_keys)
                    
        column.extend(values_to_show)
            
        column.append('=' * 20)
        
        rows = []
        for i in range(len(columns[0])):
        
            row = [x[i] for x in columns]
            rows.append(row)
            
        lines = map(lambda  x : '  '.join(x), rows)
        return '\n'.join(lines)        
        
    
        
    def _particles_factory(self):
        return type(self._real_particles())

    def _get_particle(self, key):
        if self._has_key(key):
            return Particle(key, self._real_particles())
        else:
            return None
        
    def copy(self):
        """
        Creates a new in memory particle set and copies
        all attributes and values into this set. The history
        of the set is not copied over.
        """
        attributes = self._get_attributes()
        keys = self._get_keys()
        values = self._get_values(keys, attributes)
        result = self._particles_factory()()
        result._set_particles(keys, attributes, values)
        object.__setattr__(result, "_derived_attributes", CompositeDictionary(self._derived_attributes))
       
        return result
    
    def copy_values_of_attribute_to(self, attribute_name, particles):
        """
        Copy values of one attribute from this set to the 
        other set. Will only copy values for the particles
        in both sets. See also :meth:`synchronize_to`.
        
        If you need to do this a lot, setup a dedicated
        channel.
        
        >>> particles1 = Particles(2)
        >>> particles1.x = [1.0, 2.0] | units.m
        >>> particles2 = particles1.copy()
        >>> print particles2.x
        [1.0, 2.0] m
        >>> p3 = particles1.add_particle(Particle())
        >>> particles1.x = [3.0, 4.0, 5.0] | units.m
        >>> particles1.copy_values_of_attribute_to("x", particles2)
        >>> print particles2.x
        [3.0, 4.0] m
        
        """
        channel = self.new_channel_to(particles)
        channel.copy_attributes([attribute_name])
    
    def new_channel_to(self, other):
        return ParticleInformationChannel(self, other)
        
    def __add__(self, particles):
        """
        Returns a particle subset, composed of the given
        particle(s) and this particle set. Attribute values are
        not stored by the subset. The subset provides a view
        on two or more sets of particles.
        
        :parameter particles: (set of) particle(s) to be added to self.
        
        >>> particles = Particles(4)
        >>> particles1 = particles[:2]
        >>> particles1.x = [1.0, 2.0] | units.m
        >>> particles2 = particles[2:]
        >>> particles2.x = [3.0, 4.0] | units.m
        >>> set = particles1 + particles2
        >>> set  # doctest:+ELLIPSIS
        <amuse.support.data.core.ParticlesSubset object at 0x...>
        >>> print len(set)
        4
        >>> print set.x
        [1.0, 2.0, 3.0, 4.0] m
        """
        return self.add(particles, creat_super=False)
    
    def add(self, particles, creat_super=False):
        """
        Returns a particle subset, composed of the given
        particle(s) and this particle set. Attribute values are
        not stored by the subset. The subset provides a view
        on two or more sets of particles.
        Optionally returns a superset (useful when particles come 
        from separate particles sets).
        
        :parameter particles: (set of) particle(s) to be added to self.
        
        >>> particles1 = Particles(2)
        >>> particles1.x = [1.0, 2.0] | units.m
        >>> particles2 = Particles(2)
        >>> particles2.x = [3.0, 4.0] | units.m
        >>> superset = particles1.add(particles2, creat_super=True)
        >>> superset  # doctest:+ELLIPSIS
        <amuse.support.data.core.ParticlesSuperset object at 0x...>
        >>> print len(superset)
        4
        >>> print superset.x
        [1.0, 2.0, 3.0, 4.0] m
        """
        if isinstance(particles, Particle):
            particles = particles.as_set()
        if creat_super:
            new_set = ParticlesSuperset([self, particles])
        else:
            original_particles_set = self._real_particles()
            if set(original_particles_set.key)!=set(particles._real_particles().key):
                raise Exception("Can't create new subset from particles belonging to "
                    "separate particle sets. Try creating a superset instead.")
            keys = [] ; keys.extend(self.key) ; keys.extend(particles.key)
            new_set = ParticlesSubset(original_particles_set, keys)
        if new_set.has_duplicates():
            raise Exception("Unable to add a particle, because it was already part of this set.")
        return new_set

    def __iadd__(self, particles):
        """
        Does the same as __add__, with in-place syntax:
        particles1 += particles2
        instead of:
        particles1 = particles1 + particles2
        """
        return self.__add__(particles)
    
    def __sub__(self, particles):
        """
        Returns a subset of the set without the given particle(s)
        Attribute values are not stored by the subset. The subset 
        provides a view on two or more sets of particles.
        
        :parameter particles: (set of) particle(s) to be subtracted from self.
        
        >>> particles = Particles(4)
        >>> particles.x = [1.0, 2.0, 3.0, 4.0] | units.m
        >>> junk = particles[2:]
        >>> set = particles - junk
        >>> set  # doctest:+ELLIPSIS
        <amuse.support.data.core.ParticlesSubset object at 0x...>
        >>> print len(set)
        2
        >>> print set.x
        [1.0, 2.0] m
        >>> print particles.x
        [1.0, 2.0, 3.0, 4.0] m
        """
        if isinstance(particles, Particle):
            particles = particles.as_set()
        new_keys = [] ; new_keys.extend(self._get_keys())
        subtract_keys = particles._get_keys()
        for key in subtract_keys:
            if key in new_keys:
                new_keys.remove(key)
            else:
                raise Exception("Unable to subtract a particle, because "
                    "it is not part of this set.")
        return self._subset(new_keys)
    
    def sub(self, particles):
        """
        Does the same as __sub__, with syntax:
        set = particles.sub(junk)
        instead of:
        set = particles - junk
        """
        return self.__sub__(particles)
    
    def __isub__(self, particles):
        """
        Does the same as __sub__, with in-place syntax:
        particles -= junk
        instead of:
        particles = particles - junk
        """
        return self.__sub__(particles)
    
    def add_particles(self, particles):
        """
        Adds particles from the supplied set to this set. Attributes
        and values are copied over. 
        
        .. note::
            For performance reasons the particles
            are not checked for duplicates. When the same particle 
            is part of both sets errors may occur.
        
        :parameter particles: set of particles to copy values from
        
        >>> particles1 = Particles(2)
        >>> particles1.x = [1.0, 2.0] | units.m
        >>> particles2 = Particles(2)
        >>> particles2.x = [3.0, 4.0] | units.m
        >>> particles1.add_particles(particles2)  # doctest:+ELLIPSIS
        <amuse.support.data.core.ParticlesSubset object at 0x...>
        >>> print len(particles1)
        4
        >>> print particles1.x
        [1.0, 2.0, 3.0, 4.0] m
        """
        attributes = particles._get_attributes()
        keys = particles._get_keys()
        values = particles._get_values(keys, attributes)
        values = map(self._convert_from_particles, values)
        self._set_particles(keys, attributes, values)
        return ParticlesSubset(self._real_particles(), keys)
    
    
    def add_particle(self, particle):
        """
        Add one particle to the set. 
        
        :parameter particle: particle to add
        
        >>> particles = Particles()
        >>> print len(particles)
        0
        >>> particle = Particle()
        >>> particle.x = 1.0 | units.m
        >>> particles.add_particle(particle)  # doctest:+ELLIPSIS
        <amuse.support.data.core.Particle object at ...>
        >>> print len(particles)
        1
        >>> print particles.x
        [1.0] m
        
        """
        return self.add_particles(particle.as_set())[0]
        
    
    def remove_particles(self, particles):
        """
        Removes particles from the supplied set from this set.
        
        :parameter particles: set of particles to remove from this set
        
        >>> particles1 = Particles(2)
        >>> particles1.x = [1.0, 2.0] | units.m
        >>> particles2 = Particles()
        >>> particles2.add_particle(particles1[0]) # doctest:+ELLIPSIS
        <amuse.support.data.core.Particle object at ...>
        >>> particles1.remove_particles(particles2)
        >>> print len(particles1)
        1
        >>> print particles1.x
        [2.0] m
        """
        keys = particles._get_keys()
        self._remove_particles(keys)
        
    
    def remove_particle(self, particle):
        """
        Removes a particle from this set.
        
        Result is undefined if particle is not part of the set
        
        :parameter particle: particle to remove from this set
        
        >>> particles1 = Particles(2)
        >>> particles1.x = [1.0, 2.0] | units.m
        >>> particles1.remove_particle(particles1[0])
        >>> print len(particles1)
        1
        >>> print particles1.x
        [2.0] m
        """
        self.remove_particles(particle.as_set())
        
    def synchronize_to(self, other_particles):
        """
        Synchronize the particles of this set
        with the contents of the provided set.
        After this call the proveded set will have
        the same particles as the given set. This call
        will check if particles have been removed or
        added it will not copy values of existing particles
        over.
        
        :parameter other_particles: particle set wich has to be updated
        
        >>> particles = Particles(2)
        >>> particles.x = [1.0, 2.0] | units.m
        >>> copy = particles.copy()
        >>> new_particle = Particle()
        >>> new_particle.x = 3.0 | units.m
        >>> particles.add_particle(new_particle)# doctest:+ELLIPSIS
        <amuse.support.data.core.Particle object at ...>
        >>> print particles.x
        [1.0, 2.0, 3.0] m
        >>> print copy.x
        [1.0, 2.0] m
        >>> particles.synchronize_to(copy)
        >>> print copy.x
        [1.0, 2.0, 3.0] m
        
        """
        other_keys = set(other_particles._get_keys())
        my_keys = set(self._get_keys())
        added_keys = my_keys - other_keys
        removed_keys = other_keys - my_keys
        
        added_keys = list(added_keys)
        if added_keys:
            attributes = self._get_attributes()
            values = self._get_values(added_keys, attributes)
            other_particles._set_particles(added_keys, attributes, values)
        
        removed_keys = list(removed_keys)
        if removed_keys:
            other_particles._remove_particles(removed_keys)
        
    def copy_values_of_state_attributes_to(self, particles):
        channel = self.new_channel_to(particles)
        channel.copy_attributes(self._get_state_attributes())   
    
    def to_set(self):
        """
        Returns a subset view on this set. The subset
        will contain all particles of this set.
        
        >>> particles = Particles(3)
        >>> particles.x = [1.0, 2.0, 3.0] | units.m
        >>> subset = particles.to_set()
        >>> print subset.x
        [1.0, 2.0, 3.0] m
        >>> print particles.x
        [1.0, 2.0, 3.0] m
        """
        return self._subset(self._get_keys())
    
    
    def select(self, selection_function, attributes):
        """
        Returns a subset view on this set. The subset
        will contain all particles for which the selection
        function returned True. The selection function 
        is called with scalar quantities defined by
        the attributes parameter
        
        >>> particles = Particles(3)
        >>> particles.mass = [10.0, 20.0, 30.0] | units.kg
        >>> particles.x = [1.0, 2.0, 3.0] | units.m
        >>> subset = particles.select(lambda x : x > 15.0 | units.kg, ["mass"])
        >>> print subset.mass
        [20.0, 30.0] kg
        >>> print subset.x
        [2.0, 3.0] m
        
        """
        keys = self._get_keys()
        #values = self._get_values(keys, attributes) #fast but no vectors
        values = map(lambda x: getattr(self, x), attributes)
        selected_keys = []
        for index in range(len(keys)):
            key = keys[index]
            arguments = [None] * len(attributes)
            for attr_index, attribute in enumerate(attributes):
                arguments[attr_index] = values[attr_index][index]
            if selection_function(*arguments):
                selected_keys.append(key)
        return self._subset(selected_keys)
        
    def select_array(self, selection_function, attributes = ()):
        """
        Returns a subset view on this set. The subset
        will contain all particles for which the selection
        function returned True. The selection function 
        is called with a vector quantities containing all
        the values for the attributes parameter.
        
        This function can be faster than the select function
        as it works on entire arrays. The selection_function
        is called once.
        
        >>> particles = Particles(3)
        >>> particles.mass = [10.0, 20.0, 30.0] | units.kg
        >>> particles.x = [1.0, 2.0, 3.0] | units.m
        >>> subset = particles.select_array(lambda x : x > 15.0 | units.kg, ["mass"])
        >>> print subset.mass
        [20.0, 30.0] kg
        >>> print subset.x
        [2.0, 3.0] m
        
        
        >>> particles = Particles(1000)
        >>> particles.x = units.m.new_quantity(numpy.arange(1,1000))
        >>> subset = particles.select_array(lambda x : x > (500 | units.m), ("x",) )
        >>> print len(subset)
        499
        """
        keys = self._get_keys()
        #values = self._get_values(keys, attributes) #fast but no vectors
        values = map(lambda x: getattr(self, x), attributes)
        
        selections = selection_function(*values)
        selected_keys =  numpy.compress(selections, keys)
        
        return self._subset(selected_keys)
    
    def difference(self, other):
        """
        Returns a new subset containing the difference between
        this set and the provided set.
        
        >>> particles = Particles(3)
        >>> particles.mass = [10.0, 20.0, 30.0] | units.kg
        >>> particles.x = [1.0, 2.0, 3.0] | units.m
        >>> subset = particles.select(lambda x : x > 15.0 | units.kg, ["mass"])
        >>> less_than_15kg = particles.difference(subset)
        >>> len(subset)
        2
        >>> len(less_than_15kg)
        1
        
        """
        return self.to_set().difference(other)
        
    def has_duplicates(self):
        """
        Returns True when a set contains a particle with the
        same key more than once. Particles with the same
        key are interpreted as the same particles.
        
        >>> particles = Particles()
        >>> p1 = particles.add_particle(Particle(1))
        >>> p2 = particles.add_particle(Particle(2))
        >>> particles.has_duplicates()
        False
        >>> p3 = particles.add_particle(Particle(1))
        >>> particles.has_duplicates()
        True
        >>> p3 == p1
        True
        """
        return len(self) != len(set(self._get_keys()))
    
    
    def as_subset_in(self, other):
        selected_keys = filter(lambda x : other._has_key(x), self._get_keys())
        return other._subset(selected_keys)
        
    def _subset(self, keys):
        return ParticlesSubset(self._real_particles(), keys)
        
        
    def __dir__(self):
        """
        Utility function for introspection of paricle objects
        
        >>> particles = Particles(3)
        >>> particles.mass = [10.0, 20.0, 30.0] | units.kg
        >>> particles.x = [1.0, 2.0, 3.0] | units.m
        >>> print 'mass' in dir(particles)
        True
        >>> print 'x' in dir(particles)
        True
        
        """
        result = []
        result.extend(dir(type(self)))
        result.extend(self._attributes_for_dir())
        return result

    
    def _attributes_for_dir(self):
        result = []
        result.extend(self._get_attributes())
        result.extend(self._derived_attributes.keys())
        return result
        
    
    def all_attributes(self):
        result = []
        result.append('key')
        result.extend(self._attributes_for_dir())
        return result
        
    def stored_attributes(self):
        return list(self._get_attributes())
        

    def is_empty(self):
        return self.__len__()==0
        
class Particles(AbstractParticleSet):
    """
    A set of particles. Attributes and values are stored in
    a private storage model. This storage model can store
    the values in the python memory space, in the memory space
    of the code or in a HDF5 file. By default the storage
    model is in memory.
    
    
    
    """
    def __init__(self, size = 0, storage = None, keys = None):
        AbstractParticleSet.__init__(self)
        
        if storage is None:
            self._private.attribute_storage = InMemoryAttributeStorage()
        else:
            self._private.attribute_storage = storage
    
        if size > 0:
            if keys is None:
                particle_keys = UniqueKeyGenerator.next_set_of_keys(size)
            else:
                particle_keys = keys
            self._set_particles(particle_keys)
            
        self._private.previous = None
        self._private.timestamp = None
        
    def savepoint(self, timestamp=None):
        instance = type(self)()
        instance._private.attribute_storage = self._private.attribute_storage.copy()
        instance._private.timestamp = timestamp
        instance._private.previous = self._private.previous
        self._private.previous = instance
        return instance
    
    def get_timestamp(self):
        return self._private.timestamp
        
    def iter_history(self):
        current = self
        while not current is None:
            yield current
            current = current._private.previous
            
    
    def get_state_at_timestamp(self, timestamp):
        previous_timestamp = None
        states_and_distances = []
        for state in self.iter_history():
            timestamp_of_state = state.get_timestamp()
            if timestamp_of_state is None:
                continue
            distance = abs(timestamp_of_state - timestamp)
            states_and_distances.append((state, distance,))
        
        if len(states_and_distances) == 0:
            raise Exception("You asked for a state at timestamp '{0}', but the set does not have any saved states so this state cannot be returned")
            
        accompanying_state, min_distance = states_and_distances[0]
        for state, distance  in states_and_distances:
            if distance < min_distance:
                min_distance = distance
                accompanying_state = state
        
        return accompanying_state
            
    def previous_state(self):
        return self._private.previous
        
    @property
    def history(self):
        return reversed(list(self.iter_history()))
        
    def get_timeline_of_attribute(self, particle_key, attribute):
        timeline = []
        for x in self.history:
            if x._has_key(particle_key):
                timeline.append((x._private.timestamp, x._get_value_of_attribute(particle_key, attribute)))
        return timeline
                    
                    
            
    def _set_particles(self, keys, attributes = [], values = []):
        
        self._private.attribute_storage._set_particles(keys, attributes, values)
        
    def _remove_particles(self, keys):
        self._private.attribute_storage._remove_particles(keys)
    
    def _get_values(self, keys, attributes):
        
        result = self._private.attribute_storage._get_values(keys, attributes)
        return result
                
        
    def _set_values(self, keys, attributes, values):
        
        self._private.attribute_storage._set_values(keys, attributes, values)
    
    def _get_attributes(self):
        return self._private.attribute_storage._get_attributes()
        
    def _get_state_attributes(self):
        return self._private.attribute_storage._state_attributes()
        
        
    def _get_keys(self):
        return self._private.attribute_storage._get_keys()
        
    def _has_key(self, key):
        return self._private.attribute_storage._has_key(key)
        
    
    

class ParticlesSuperset(AbstractParticleSet):
    """A superset of particles. Attribute values are not
    stored by the superset. The superset provides a view
    on two or more sets of particles. 
    
    Superset objects are not supposed to be created
    directly. Instead use the ``union`` methods.
    
    >>> p1 = Particles(3)
    >>> p1.mass = [10.0, 20.0, 30.0] | units.kg
    >>> p2 = Particles(3)
    >>> p2.mass = [40.0, 50.0, 60.0] | units.kg
    >>> p = ParticlesSuperset([p1, p2])
    >>> print len(p)
    6
    >>> print p.mass
    [10.0, 20.0, 30.0, 40.0, 50.0, 60.0] kg
    >>> p[4].mass = 70 | units.kg
    >>> print p.mass
    [10.0, 20.0, 30.0, 40.0, 70.0, 60.0] kg
    >>> p2[1].mass
    quantity<70.0 kg>
    >>> cp = p.copy()
    >>> print len(cp)
    6
    >>> print cp.mass
    [10.0, 20.0, 30.0, 40.0, 70.0, 60.0] kg
    """
    
    def __init__(self, particle_sets):
        AbstractParticleSet.__init__(self)
        
        self._private.particle_sets = particle_sets
              
    
    def __len__(self):
        result = 0
        for set in self._private.particle_sets:
            result += len(set)
            
        return result
    
    
    def _particles_factory(self):
        return Particles
        
    def __getitem__(self, index):
        offset = 0
        for set in self._private.particle_sets:
            length = len(set)
            if index < (offset+length):
                return set[index - offset]
            offset += length
    
    def _split_keys_over_sets(self, keys):
        split_sets = [ [] for x in self._private.particle_sets ]
        split_indices = [ [] for x in self._private.particle_sets ]
        
        
        if keys is None:
            offset = 0
            
            for setindex, set in enumerate(self._private.particle_sets):
                split_sets[setindex].extend(set._get_keys())
                split_indices[setindex].extend(range(offset, offset + len(set)))
                offset = offset + len(set)
                
        else:
            for index, key in enumerate(keys):
                for setindex, set in enumerate(self._private.particle_sets):
                    if set._has_key(key):
                        split_sets[setindex].append(key)
                        split_indices[setindex].append(index)
        
        return split_sets, split_indices
                    
        
    def _set_particles(self, keys, attributes = [], values = []):
        raise Exception("Cannot add particles to a superset")
        
    def _remove_particles(self, keys):
        split_sets, split_indices = self._split_keys_over_sets(keys)
        for split_keys, set in zip(split_sets, self._private.particle_sets):
            set._remove_particles(split_keys)
    
    def _get_values(self, keys, attributes):
        split_sets, split_indices = self._split_keys_over_sets(keys)
        
        indices_and_values = []
        
        for keys_for_set, indices_for_set, set in zip(split_sets, split_indices, self._private.particle_sets):
            values_for_set = set._get_values(keys_for_set, attributes)
            indices_and_values.append( (indices_for_set,values_for_set) )
        
        if keys is None:
            resultlength = len(self)
        else:
            resultlength = len(keys)
            
        values = [None] * len(attributes)
        units = [None] * len(attributes)
        for indices, values_for_set in indices_and_values:
            for valueindex, quantity in enumerate(values_for_set):
                resultvalue = values[valueindex]
                if resultvalue is None:
                    resultvalue = numpy.zeros(resultlength ,dtype=quantity.number.dtype)
                    values[valueindex] = resultvalue
                    
                    units[valueindex] = quantity.unit
                    
                resultunit = units[valueindex]
                
                numpy.put(resultvalue, indices, quantity.value_in(resultunit))
                
            
        return map(lambda u,v : u.new_quantity(v), units, values)
        
    def _set_values(self, keys, attributes, values):
        split_sets, split_indices = self._split_keys_over_sets(keys)
        
        for keys_for_set, indices_for_set, set in zip(split_sets, split_indices, self._private.particle_sets):
            quantities = [None] * len(attributes)
            for valueindex, quantity in enumerate(values_for_set):
                numbers = numpy.take(quantity.number, indices_for_set)
                quantities[valueindex] = quantity.unit.new_quantity(numbers)
            
            set._set_values(keys_for_set, attributes, quantities)
    
    def _get_attributes(self):
        for set in self._private.particle_sets:
            return set._get_attributes()
        
    def _get_keys(self):
        result = []
        
        for set in self._private.particle_sets:
            result.extend(set._get_keys())
            
        return result
        
    def _has_key(self, key):
        for set in self._private.particle_sets:
            if set._has_key(key):
                return True
        return False
    
    def _get_state_attributes(self):
        for set in self._private.particle_sets:
            return set._get_state_attributes()
        
        
    def _real_particles(self):
        return self



class ParticlesSubset(AbstractParticleSet):
    """A subset of particles. Attribute values are not
    stored by the subset. The subset provides a limited view
    to the particles. 
    
    Particle subset objects are not supposed to be created
    directly. Instead use the ``to_set`` or ``select`` methods.

    """
    
    def __init__(self, particles, keys):
        AbstractParticleSet.__init__(self, particles)
        
        self._private.particles = particles
        self._private.keys = numpy.array(keys, dtype='uint64')
        self._private.set_of_keys = set(keys)
              
        
    def __getitem__(self, index):
        key = self._get_keys()[index]
        if key == 0 or key >= (2**64 - 1):
            return None
        else:
            return Particle(self._get_keys()[index], self._real_particles())
            
    def _set_particles(self, keys, attributes = [], values = []):
        """
        Adds particles from to the subset, also
        adds the particles to the superset
        """
        self._private.keys = numpy.concatenate((self.keys,  numpy.array(keys,dtype='uint64')))
        self._private.set_of_keys += set(keys)
        self._private.particles._set_particles(keys, attributes, values)
        
    def _remove_particles(self, keys):
        """
        Removes particles from the subset, does not remove particles
        from the super set
        """
        set_to_remove = set(keys)
        self._private.set_of_keys -= set_to_remove
        index = 0
        indices = []
        for x in self._private.keys:
            if x in set_to_remove:
                indices.append(index)
            index += 1
        self._private.keys =  numpy.delete(self._private.keys,indices)
    
    def _get_values(self, keys, attributes):
        return self._private.particles._get_values(keys, attributes)
        
    def _set_values(self, keys, attributes, values):
        self._private.particles._set_values(keys, attributes, values)
    
    def _get_attributes(self):
        return self._private.particles._get_attributes()
        
    def _get_keys(self):
        return self._private.keys
        
    def _has_key(self, key):
        return key in self._private.set_of_keys
    
    def _get_state_attributes(self):
        return self._private.particles._get_state_attributes(self)
            
        
        
    def _real_particles(self):
        return self._private.particles
        
    def difference(self, other):
        new_set_of_keys = self._private.set_of_keys.difference(other.to_set()._private.set_of_keys)
        return ParticlesSubset(self._private.particles, list(new_set_of_keys))
        
    def union(self, other):
        """
        Returns a new subset containing the union between
        this set and the provided set.
        
        >>> particles = Particles(3)
        >>> particles.mass = [10.0, 20.0, 30.0] | units.kg
        >>> subset1 = particles.select(lambda x : x > 25.0 | units.kg, ["mass"])
        >>> subset2 = particles.select(lambda x : x < 15.0 | units.kg, ["mass"])
        >>> union = subset1.union(subset2)
        >>> len(union)
        2
        >>> sorted(union.mass.value_in(units.kg))
        [10.0, 30.0]
        """
        
        new_set_of_keys = self._private.set_of_keys.union(other.to_set()._private.set_of_keys)
        return ParticlesSubset(self._private.particles, list(new_set_of_keys))
    
    def to_set(self):
        return self



class ParticlesWithUnitsConverted(AbstractParticleSet):
    """
    A view on a particle sets. Used when to convert
    values between incompatible sets of units. For example to
    convert from si units to nbody units.
    
    The converter must have implement the ConverterInterface.
    
    >>> from amuse.support.units import nbody_system
    >>> particles_nbody = Particles(2)
    >>> particles_nbody.x = [10.0 , 20.0] | nbody_system.length
    >>> convert_nbody = nbody_system.nbody_to_si(10 | units.kg , 5 | units.m )
    >>> particles_si = ParticlesWithUnitsConverted(
    ...     particles_nbody,
    ...     convert_nbody.as_converter_from_si_to_nbody())
    ...
    >>> print particles_nbody.x
    [10.0, 20.0] nbody length
    >>> print particles_si.x
    [50.0, 100.0] m
    >>> particles_si.x = [200.0, 400.0] | units.m
    >>> print particles_nbody.x
    [40.0, 80.0] nbody length

    
    """
    
    class ConverterInterface(object):
        """
        Interface definition for the converter.
        
        source
            The source quantity is in the units of the user of a
            ParticlesWithUnitsConverted object
        target
            The target quantity must be in the units of the
            internal particles set.
        
        """
        def from_source_to_target(quantity):
            """
            Converts the quantity from the source units
            to the target units.
            
            :parameter quantity: quantity to convert
            """
            return quantity
            
        
        def from_target_to_source(quantity):
            """
            Converts the quantity from the target units
            to the source units.
            
            :parameter quantity: quantity to convert
            """
            return quantity
            
        
    def __init__(self, particles, converter):
        AbstractParticleSet.__init__(self, particles)
        
        self._private.particles = particles
        self._private.converter = converter
              
    
    def copy(self):
        copiedParticles =  self._private.particles.copy()
        return ParticlesWithUnitsConverted(copiedParticles, self._private.converter)
        
    def _set_particles(self, keys, attributes = [], values = []):
        converted_values = []
        for quantity in values:
            converted_quantity = self._private.converter.from_source_to_target(quantity)
            converted_values.append(converted_quantity)
        self._private.particles._set_particles(keys, attributes, converted_values)
        
    def _remove_particles(self, keys):
        self._private.particles._remove_particles(keys)
        
    def _get_values(self, keys, attributes):
        values = self._private.particles._get_values(keys, attributes)
        converted_values = []
        for quantity in values:
            converted_quantity = self._private.converter.from_target_to_source(quantity)
            converted_values.append(converted_quantity)
        return converted_values
        
    def _set_values(self, keys, attributes, values):
        converted_values = []
        for quantity in values:
            converted_quantity = self._private.converter.from_source_to_target(quantity)
            converted_values.append(converted_quantity)
        self._private.particles._set_values(keys, attributes, converted_values)
    
    def _get_attributes(self):
        return self._private.particles._get_attributes()
        
    def _get_state_attributes(self):
        return self._private.particles._get_state_attributes()
        
    def _get_keys(self):
        return self._private.particles._get_keys()
        
    def _has_key(self, key):
        return self._private.particles._has_key(key)
        
    def to_set(self):
        return ParticlesSubset(self, self._get_keys())
    
            

class ParticleInformationChannel(object):
    
    def __init__(self, from_particles, to_particles):
        self.from_particles = from_particles
        self.to_particles = to_particles
        self._reindex()
        
    def _reindex(self):
        self.keys = self.intersecting_keys()
        #speed-up:
        #self.from_indices = self.from_particles._get_indices_of(self.keys)
        #self.to_indices = self.to_particles._get_indices_of(self.keys)
    
    def intersecting_keys(self):
        from_keys = self.from_particles._get_keys()
        return filter(lambda x : self.to_particles._has_key(x), from_keys)
        
    def copy_attributes(self, attributes):
        self._reindex()
        data = self.from_particles._get_values(self.keys, attributes)
        self.to_particles._set_values(self.keys, attributes, data)
    
    def copy(self):
        self._reindex()
        self.copy_attributes(self.from_particles._get_attributes())
    

        
class Stars(Particles):

    def __init__(self, size = 0):
        Particles.__init__(self, size)

class Particle(object):
    """A physical object or a physical region simulated as a 
    physical object (cloud particle).
    
    All attributes defined on a particle are specific for 
    that particle (for example mass or position). A particle contains 
    a set of attributes, some attributes are *generic* and applicable
    for multiple modules. Other attributes are *specific* and are 
    only applicable for a single module.
    
    
    """
    __slots__ = ["key", "particles_set"]
    
    
    
    def __init__(self, key = None, particles_set = None, **keyword_arguments):
        if particles_set is None:
            if key == None:
                particles_set = Particles(1)
                key = particles_set._get_keys()[0]
            else:
                particles_set = Particles(1, keys = [key])
                
        object.__setattr__(self, "key", key)
        object.__setattr__(self, "particles_set", particles_set)
        
        for attribute_name in keyword_arguments:
            attribute_value = keyword_arguments[attribute_name]
            setattr(self, attribute_name, attribute_value)
            
    def __setattr__(self, name_of_the_attribute, new_value_for_the_attribute):
       
        if isinstance(new_value_for_the_attribute, values.Quantity):
            self.particles_set._set_value_of_attribute(self.key, name_of_the_attribute, new_value_for_the_attribute)
        elif isinstance(new_value_for_the_attribute, Particle):
            self.particles_set._set_value_of_attribute(
                self.key, 
                name_of_the_attribute, 
                new_value_for_the_attribute.key | units.object_key
            )
        else:
            raise Exception("attribute "+name_of_the_attribute+" does not have a valid value, values must have a unit")
    
    def __getattr__(self, name_of_the_attribute):
         return self.particles_set._get_value_of_attribute(self.key, name_of_the_attribute)
    
    def children(self):
        return self.particles_set.select(lambda x : x == self, ["parent"])
    
    def descendents(self):
        result = self.children()
        stack = list(result)
        while len(stack) > 0:
            current = stack.pop()
            children = current.children()
            result = result.union(children)
            stack.extend(children)
        return result
        
    def add_child(self, child):
        if self.particles_set != child.particles_set:
            raise Exception("The parent and child particles should be in the same set")
        
        child.parent = self
                
    def add(self, particles):
        """
        Returns a particle subset, composed of the given
        particle(s) and this particle. Attribute values are
        not stored by the subset. The subset provides a view
        on the particles.
        
        :parameter particles: particle(s) to be added to self.
        
        >>> particles = Particles(2)
        >>> particle1 = particles[0]
        >>> particle1.x = 1.0 | units.m
        >>> particle2 = particles[1]
        >>> particle2.x = 2.0 | units.m
        >>> set = particle2.add(particle1)
        >>> set  # doctest:+ELLIPSIS
        <amuse.support.data.core.ParticlesSubset object at 0x...>
        >>> print len(set)
        2
        >>> print set.x
        [1.0, 2.0] m
        """
        if isinstance(particles, Particle):
            particles = particles.as_set()
        return particles.add(self)
    
    def __add__(self, particles):
        """
        Does the same as add, with syntax:
        set = particle1 + particle2
        instead of:
        set = particle1.add(particle2)
        """
        return self.add(particles)
    
    def sub(self, particles):
        """
        Raises an exception: cannot subtract particle(s) 
        from a particle.
        """
        raise Exception("Cannot subtract particle(s) from a particle.")
    
    def __sub__(self, particles):
        """
        Does the same as sub, with syntax:
        set = particle1 - particle2
        instead of:
        set = particle1.sub(particle2)
        """
        return self.sub(particles)
    
    def __str__(self):
        """
        Display string for a particle
        
        >>> p = Particle(10)
        >>> p.x = 10.2 | units.m
        >>> p.mass = 5 | units.kg
        >>> print p
        Particle(10, mass=5.0 kg, x=10.2 m)
        """
        output = 'Particle('
        output += str(self.key)
        for name, value in self.particles_set._values_of_particle(self.key):
            output += ', '
            output += name
            output += '='
            output += str(value)
        output += ')'
        return output
        
    
    def __dir__(self):
        result = []
        result.extend(dir(type(self)))
        result.extend(self.particles_set._attributes_for_dir())
        return result
        
    def __eq__(self, other):
        return isinstance(other, type(self)) and other.key == self.key
        
        
    def set_default(self, attribute, quantity):
        if not attribute in self.particles_set._get_attributes():
            self.particles_set._set_value_of_attribute(self, attribute, quantity)
            
    def get_timeline_of_attribute(self, attribute):
        return self.particles_set.get_timeline_of_attribute(self.key, attribute)
        
    def as_set(self):
        """
        Returns a subset view on the set containing this particle. The
        subset view includes this particle and no other particles.
        
        >>> particles = Particles(2)
        >>> particles.x = [1.0, 2.0] | units.m
        >>> particle2 = particles[1]
        >>> print particle2.x
        2.0 m
        >>> particles_with_one_particle = particle2.as_set()
        >>> len(particles_with_one_particle)
        1
        >>> print particles_with_one_particle.x
        [2.0] m
        """
        return ParticlesSubset(self.particles_set, [self.key])
        
def center_of_mass(particles):
    masses = particles.mass
    x_values = particles.x
    y_values = particles.y
    z_values = particles.z
    
    total_mass = masses.sum()
    massx = (masses * x_values).sum()
    massy = (masses * y_values).sum()
    massz = (masses * z_values).sum()

    return values.VectorQuantity.new_from_scalar_quantities(
        massx/total_mass,
        massy/total_mass,
        massz/total_mass
    )

def center_of_mass_velocity(particles):
    masses = particles.mass
    x_values = particles.vx
    y_values = particles.vy
    z_values = particles.vz
    
    total_mass = masses.sum()
    massx = (masses * x_values).sum()
    massy = (masses * y_values).sum()
    massz = (masses * z_values).sum()

    return values.VectorQuantity.new_from_scalar_quantities(
        massx/total_mass,
        massy/total_mass,
        massz/total_mass
    )
    
def kinetic_energy(particles):
    mass = particles.mass
    vx = particles.vx
    vy = particles.vy
    vz = particles.vz
    v_squared = (vx * vx) + (vy * vy) + (vz * vz)
    m_v_squared = mass * v_squared
    return 0.5 * m_v_squared.sum()
    

def potential_energy(particles, smoothing_length_squared = 0 | units.m * units.m):
    mass = particles.mass
    x_vector = particles.x
    y_vector = particles.y
    z_vector = particles.z
    
    sum_of_energies = 0 | units.J
    
    for i in range(len(particles)):
       x = x_vector[i]
       y = y_vector[i]
       z = z_vector[i]
       dx = x - x_vector[i+1:]
       dy = y - y_vector[i+1:]
       dz = z - z_vector[i+1:]
       dr_squared = (dx * dx) + (dy * dy) + (dz * dz)
       dr = (dr_squared+smoothing_length_squared).sqrt()
       m_m = mass[i] * mass[i+1:]
       
       energy_of_this_particle = (m_m / dr).sum()
       sum_of_energies +=  -1 * constants.G * energy_of_this_particle
        
    return sum_of_energies


AbstractParticleSet.add_global_function_attribute("center_of_mass", center_of_mass)
AbstractParticleSet.add_global_function_attribute("center_of_mass_velocity", center_of_mass_velocity)
AbstractParticleSet.add_global_function_attribute("kinetic_energy", kinetic_energy)
AbstractParticleSet.add_global_function_attribute("potential_energy", potential_energy)

AbstractParticleSet.add_global_vector_attribute("position", ["x","y","z"])
AbstractParticleSet.add_global_vector_attribute("velocity", ["vx","vy","vz"])

def particle_specific_kinetic_energy(part):
  return 0.5*(part.velocity**2).sum()

def particle_potential(part, smoothing_length_squared=0. | units.m**2):
  particles=part.particles_set.to_set()
  particles.remove_particle(part)
  dx = part.x - particles.x
  dy = part.y - particles.y
  dz = part.z - particles.z 
  dr_squared = (dx * dx) + (dy * dy) + (dz * dz)
  dr = (dr_squared+smoothing_length_squared).sqrt()
  return - constants.G * (particles.mass / dr).sum()

AbstractParticleSet.add_global_function_attribute("specific_kinetic_energy", \
 None, particle_specific_kinetic_energy)
AbstractParticleSet.add_global_function_attribute("potential", \
 None, particle_potential)
