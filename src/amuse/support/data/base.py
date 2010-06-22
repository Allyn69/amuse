from amuse.support.data import values
from amuse.support.data.values import Quantity, new_quantity, zero
from amuse.support.units import constants
from amuse.support.units import units
from amuse.support.core import CompositeDictionary

from amuse.support.data.base import *

import numpy
import random
import inspect


class KeyGenerator(object):
    
    def next(self):
        pass
        
    def next_set_of_keys(self, length):
        pass
        
class BasicUniqueKeyGenerator(KeyGenerator):
    
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
        

class RandomNumberUniqueKeyGenerator(KeyGenerator):
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



class AttributeStorage(object):
    """
    Abstract base class of particle storage models.
    """
    
    def _add_particles(self, keys, attributes = [], values = []):
        pass
        
    def _remove_particles(self, keys):
        pass
        
    def _get_values(self, particles, attributes):
        pass
        
    def _set_values(self, particles, attributes, list_of_values_to_set):
        pass
        
    def _get_attribute_names(self):
        pass
    
    def _has_key(self, key):
        return False
        
    def _get_keys(self):
        return []
        
    def __len__(self):
        return 0


class DerivedAttribute(object):
    """
    Abstract base class for calculated properties and 
    methods on sets.
    """
    def get_values_for_entities(self, particles):
        return None
    
    def set_values_for_entities(self, particles, value):
        raise Exception("cannot set value of attribute '{0}'")

    def get_value_for_entity(self, particles, key):
        return None

    def set_value_for_entity(self, particles, key, value):
        raise Exception("cannot set value of attribute '{0}'")

class VectorAttribute(DerivedAttribute):
    """
    Combine multiple attributes into a vecter attribute
    """
    def  __init__(self, attribute_names):
        self.attribute_names = attribute_names
    
    def get_values_for_entities(self, instance):
        values = instance._get_values(instance._get_keys(), self.attribute_names)
          
        unit_of_the_values = None
        results = []
        for quantity in values:
            if unit_of_the_values is None:
                unit_of_the_values = quantity.unit
            results.append(quantity.value_in(unit_of_the_values))
            
        results = numpy.dstack(results)[0]
        return unit_of_the_values.new_quantity(results)

    def set_values_for_entities(self, instance, value):
        vectors = value.number
        split = numpy.hsplit(vectors,len(self.attribute_names))
        list_of_values = []
        for i in range(len(self.attribute_names)):
            values = value.unit.new_quantity(split[i].reshape(len(split[i])))
            list_of_values.append(values)
            
        instance._set_values(instance._get_keys(), self.attribute_names, list_of_values)
    
    def get_value_for_entity(self, instance,  key):
        values = instance._get_values_for_entity(key, self.attribute_names)
          
        unit_of_the_values = None
        results = []
        for quantity in values:
            if unit_of_the_values is None:
                unit_of_the_values = quantity.unit
            results.append(quantity.value_in(unit_of_the_values))
            
        return unit_of_the_values.new_quantity(results)

    def set_value_for_entity(self, instance, key, vector):
        list_of_values = []
        for quantity in vector:
            list_of_values.append(quantity)
        instance._set_values_for_entity(key, self.attribute_names, list_of_values)


    
class CalculatedAttribute(DerivedAttribute):
    """
    Calculate the value of an attribute based
    on existing attributes.
    """
    def  __init__(self, function, attribute_names = None):
        self.function = function
        if attribute_names is None:
            arguments, varargs, kwargs, defaults = inspect.getargspec(function)
            self.attribute_names = arguments 
        else:
            self.attribute_names = attribute_names
    
    def get_values_for_entities(self, instance):
        values = instance._get_values(instance._get_keys(), self.attribute_names)
        return self.function(*values)
    
    def get_value_for_entity(self, instance,  key):
        values = instance._get_values_for_entity(key, self.attribute_names)
        return self.function(*values)
        

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
            return self.function(self.particles, self.particles._get_particle(self.key), *list_arguments, **keyword_arguments)
        
    
    def  __init__(self, particles_function = None, particle_function = None):
        self.particles_function = particles_function
        self.particle_function = particle_function
        
    def get_values_for_entities(self, particles):
        return self.BoundParticlesFunctionAttribute(self.particles_function, particles)
            
   
    def get_value_for_entity(self, particles, key):
        return self.BoundParticleFunctionAttribute(self.particle_function, particles, key)

        
class AbstractSet(object):
    """
    Abstract superclass of all sets of particles and grids. 
    """
    GLOBAL_DERIVED_ATTRIBUTES = {}
    
    
    class PrivateProperties(object):
        """
        Defined for superclasses to store private properties.
        Every set has :meth:`__setattr__` defined.
        
        The :meth:`__setattr__` function will set all attributes
        of the entities in the set to the specified value(s).
        
        To be able to define attributes on the set itself we
        use an instance of this class, attributes can be 
        defined as::
        
            self._private.new_attribute = 'new value'
        
        Subclass implementers do not need to
        use the :meth:`object.__setattr__` syntax.
        
        For documentation about the :meth:`~object.__setattr__`
        call please see the 
        `python data model <http://docs.python.org/reference/datamodel.html>`_ 
        documentation on the python website.
        """
        pass
        
    def __init__(self, original = None):
        if original is None:
            derived_attributes = self.GLOBAL_DERIVED_ATTRIBUTES
        else:
            derived_attributes = original._derived_attributes
            
        object.__setattr__(self, "_derived_attributes", CompositeDictionary(derived_attributes))
        object.__setattr__(self, "_private", self.PrivateProperties())
    
    
    def __getattr__(self, name_of_the_attribute):
        if name_of_the_attribute == 'key':
            return self._get_keys()
        elif name_of_the_attribute in self._derived_attributes:
            return self._derived_attributes[name_of_the_attribute].get_values_for_entities(self)
        else:
            if name_of_the_attribute in self._get_attribute_names():
                return self._convert_to_entities_or_quantities(
                    self._get_values(self._get_keys(), [name_of_the_attribute])[0]
                )
            else:
                raise AttributeError("You tried to access attribute '{0}'"
                    " but this attribute is not defined for this set.".format(name_of_the_attribute))
    
    def check_attribute(self, name_of_the_attribute, value):
        if not isinstance(value, Quantity):
            raise AttributeError("Can only assign quantities or other particles to an attribute.")
            
    def __setattr__(self, name_of_the_attribute, value):
        self.check_attribute(name_of_the_attribute, value)
        if name_of_the_attribute in self._derived_attributes:
            self._derived_attributes[name_of_the_attribute].set_values_for_entities(self, value)
        else:
            self._set_values(self._get_keys(), [name_of_the_attribute], [self._convert_from_entities_or_quantities(value)])
    
    def _get_value_of_attribute(self, key, attribute):
        if attribute in self._derived_attributes:
            return self._derived_attributes[attribute].get_value_for_entity(self, key)
        else:
            return self._convert_to_entities_or_quantities(self._get_values([key], [attribute])[0])[0]
    
    def _get_values_for_entity(self, key, attributes):
        return [x[0] for x in self._get_values([key], attributes)]
        
    def _set_values_for_entity(self, key, attributes, values):
        return self._set_values([key], attributes, [x.as_vector_with_length(1) for x in values])
    
    def _set_value_of_attribute(self, key, attribute, value):
        if attribute in self._derived_attributes:
            return self._derived_attributes[attribute].set_value_for_entity(self, key, value)
        else:
            return self._set_values([key], [attribute], value.as_vector_with_length(1))
            
    def _convert_to_entities_or_quantities(self, x):
        if x.unit.iskey():
            return self._subset(x.number)
        else:
            return x
        
    def _convert_from_entities_or_quantities(self, x):
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
        
    def _add_particles(self, keys, attributes, values):
        pass
        
    def _remove_particles(self, keys):
        pass
    
    def _get_keys(self):
        return []
        
    def _has_key(self):
        return False
    
    def _get_attribute_names(self):
        return []
    
    def _get_state_attributes(self):
        return []
    
    def _original_set(self):
        return self
    
    def add_vector_attribute(self, name_of_the_attribute, name_of_the_components):
        self._derived_attributes[name_of_the_attribute] = VectorAttribute(name_of_the_components)
    
    @classmethod
    def add_global_vector_attribute(cls, name_of_the_attribute, name_of_the_components):
        """
        Define a *global* vector attribute, coupling two or more scalar attributes into
        one vector attribute. The vector will be defined for all particle sets
        created after calling this function.
        
        :argument name_of_the_attribute: Name to reference the vector attribute by. 
        :argument name_of_the_components: List of strings, each string a name of a scalar attribute.
        
        >>> from amuse.support.data.core import Particles
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
          
        
        >>> from amuse.support.data.core import Particles
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
        
        
        >>> from amuse.support.data.core import Particles
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
        
        >>> from amuse.support.data.core import Particles
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
        
        >>> from amuse.support.data.core import Particles
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
        
        >>> from amuse.support.data.core import Particles
        >>> def xsquared(set, p):
        ...   return p.x * p.x
        ...
        >>> particles = Particles(2)
        >>> particles.add_particle_function_attribute("xsquared", xsquared)
        >>> particles.x = [4.0 , 2.0] | units.m
        >>> particles[0].xsquared()
        quantity<16.0 m**2>
        """
        self._derived_attributes[name_of_the_attribute] = FunctionAttribute(None, function)
        
    def __len__(self):
        return len(self._get_keys())
        
    def _set_factory(self):
        return type(self._original_set())

    def copy(self):
        """
        Creates a new in memory particle set and copies
        all attributes and values into this set. The history
        of the set is not copied over.
        """
        attributes = self._get_attribute_names()
        keys = self._get_keys()
        values = self._get_values(keys, attributes)
        result = self._set_factory()()
        result._add_particles(keys, attributes, values)
        object.__setattr__(result, "_derived_attributes", CompositeDictionary(self._derived_attributes))
       
        return result
        
    def copy_to_memory(self):
        attributes = self._get_attribute_names()
        keys = self._get_keys()
        values = self._get_values(keys, attributes)
        result = Particles()
        result._add_particles(keys, attributes, values)
        object.__setattr__(result, "_derived_attributes", CompositeDictionary(self._derived_attributes))
       
        return result
    
    def copy_values_of_attribute_to(self, attribute_name, particles):
        """
        Copy values of one attribute from this set to the 
        other set. Will only copy values for the particles
        in both sets. See also :meth:`synchronize_to`.
        
        If you need to do this a lot, setup a dedicated
        channel.
        
        >>> from amuse.support.data.core import Particles,Particle
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
        
        >>> from amuse.support.data.core import Particles
        >>> particles = Particles(4)
        >>> particles1 = particles[:2]
        >>> particles1.x = [1.0, 2.0] | units.m
        >>> particles2 = particles[2:]
        >>> particles2.x = [3.0, 4.0] | units.m
        >>> new_set = particles1 + particles2
        >>> new_set  # doctest:+ELLIPSIS
        <amuse.support.data.particles.ParticlesSubset object at 0x...>
        >>> print len(new_set)
        4
        >>> print new_set.x
        [1.0, 2.0, 3.0, 4.0] m
        """
        particles = particles.as_set()
        original_particles_set = self._original_set()
        if set(original_particles_set.key)!=set(particles._original_set().key):
            raise Exception("Can't create new subset from particles belonging to "
                "separate particle sets. Try creating a superset instead.")
        keys = list(self.key) + list(particles.key)
        new_set = ParticlesSubset(original_particles_set, keys)
        if new_set.has_duplicates():
            raise Exception("Unable to add a particle, because it was already part of this set.")
        return new_set
    
    def __sub__(self, particles):
        """
        Returns a subset of the set without the given particle(s)
        Attribute values are not stored by the subset. The subset 
        provides a view on two or more sets of particles.
        
        :parameter particles: (set of) particle(s) to be subtracted from self.
        
        >>> from amuse.support.data.core import Particles
        >>> particles = Particles(4)
        >>> particles.x = [1.0, 2.0, 3.0, 4.0] | units.m
        >>> junk = particles[2:]
        >>> new_set = particles - junk
        >>> new_set  # doctest:+ELLIPSIS
        <amuse.support.data.particles.ParticlesSubset object at 0x...>
        >>> print len(new_set)
        2
        >>> print new_set.x
        [1.0, 2.0] m
        >>> print particles.x
        [1.0, 2.0, 3.0, 4.0] m
        """
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
    
    def add_particles(self, particles):
        """
        Adds particles from the supplied set to this set. Attributes
        and values are copied over. 
        
        .. note::
            For performance reasons the particles
            are not checked for duplicates. When the same particle 
            is part of both sets errors may occur.
        
        :parameter particles: set of particles to copy values from
        
        >>> from amuse.support.data.core import Particles
        >>> particles1 = Particles(2)
        >>> particles1.x = [1.0, 2.0] | units.m
        >>> particles2 = Particles(2)
        >>> particles2.x = [3.0, 4.0] | units.m
        >>> particles1.add_particles(particles2)  # doctest:+ELLIPSIS
        <amuse.support.data.particles.ParticlesSubset object at 0x...>
        >>> print len(particles1)
        4
        >>> print particles1.x
        [1.0, 2.0, 3.0, 4.0] m
        """
        attributes = particles._get_attribute_names()
        keys = particles._get_keys()
        values = particles._get_values(keys, attributes)
        values = map(self._convert_from_entities_or_quantities, values)
        self._add_particles(keys, attributes, values)
        return ParticlesSubset(self._original_set(), keys)
    
    
    def add_particle(self, particle):
        """
        Add one particle to the set. 
        
        :parameter particle: particle to add
        
        >>> from amuse.support.data.core import Particles,Particle
        >>> particles = Particles()
        >>> print len(particles)
        0
        >>> particle = Particle()
        >>> particle.x = 1.0 | units.m
        >>> particles.add_particle(particle)  # doctest:+ELLIPSIS
        <amuse.support.data.particles.Particle object at ...>
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
        
        >>> from amuse.support.data.core import Particles
        >>> particles1 = Particles(2)
        >>> particles1.x = [1.0, 2.0] | units.m
        >>> particles2 = Particles()
        >>> particles2.add_particle(particles1[0]) # doctest:+ELLIPSIS
        <amuse.support.data.particles.Particle object at ...>
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
        
        >>> from amuse.support.data.core import Particles
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
        
        >>> from amuse.support.data.core import Particles, Particle
        >>> particles = Particles(2)
        >>> particles.x = [1.0, 2.0] | units.m
        >>> copy = particles.copy()
        >>> new_particle = Particle()
        >>> new_particle.x = 3.0 | units.m
        >>> particles.add_particle(new_particle)# doctest:+ELLIPSIS
        <amuse.support.data.particles.Particle object at ...>
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
            attributes = self._get_attribute_names()
            values = self._get_values(added_keys, attributes)
            other_particles._add_particles(added_keys, attributes, values)
        
        removed_keys = list(removed_keys)
        if removed_keys:
            other_particles._remove_particles(removed_keys)
        
    def copy_values_of_state_attributes_to(self, particles):
        channel = self.new_channel_to(particles)
        channel.copy_attributes(self._get_state_attributes())   
    
    def as_set(self):
        """
        Returns a subset view on this set. The subset
        will contain all particles of this set.
        
        >>> from amuse.support.data.core import Particles
        >>> particles = Particles(3)
        >>> particles.x = [1.0, 2.0, 3.0] | units.m
        >>> subset = particles.as_set()
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
        
        >>> from amuse.support.data.core import Particles
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
        
        >>> from amuse.support.data.core import Particles
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
        
        >>> from amuse.support.data.core import Particles
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
        return self.as_set().difference(other)
        
    def get_timestamp(self):
        return None
    
    def has_duplicates(self):
        """
        Returns True when a set contains a particle with the
        same key more than once. Particles with the same
        key are interpreted as the same particles.
        
        >>> from amuse.support.data.core import Particles,Particle
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
        return ParticlesSubset(self._original_set(), keys)
        
        
    def __dir__(self):
        """
        Utility function for introspection of paricle objects
        
        >>> from amuse.support.data.core import Particles
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
        result.extend(self._get_attribute_names())
        result.extend(self._derived_attributes.keys())
        return result
        
    
    def all_attributes(self):
        result = []
        result.append('key')
        result.extend(self._attributes_for_dir())
        return result
        
    def stored_attributes(self):
        return list(self._get_attribute_names())
        

    def is_empty(self):
        return self.__len__()==0
            
