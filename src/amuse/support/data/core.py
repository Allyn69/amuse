"""
"""

from amuse.support.data import values
from amuse.support.units import si

import numpy

class TemporalAttribute(object):
    def __init__(self, name):
        self.values = []
        self.name = name
    
    def get_times(self):
        for time, value in self.values:
            yield time
            
    def set_value_at_time(self, time, value):
        self.values.append((time, value))
    
    def get_value_at_time(self, requested_time = None):
        if requested_time is None:
            return self.value()
            
        min = 0
        max = len(self.values) - 1
        while True:
            index_of_midpoint = (max + min) / 2 
            time, value = self.values[index_of_midpoint]
            requested_time_is_after_time_of_index = requested_time > time
            if max - min == 1:
                if requested_time_is_after_time_of_index:
                    return self.values[max]
                else:
                    return self.values[min]
                    
            if requested_time_is_after_time_of_index:
                min = index_of_midpoint
            else:
                max = index_of_midpoint
            
    
    def value(self):
        return self.values[-1][1]
    
    def time(self):
        return self.values[-1][0]
        
    def to_number_in(self, units):
        return self.value().value_in(units)
        
    def __str__(self):
        return str(self.time()) + " - " + str(self.value())

class AttributeValues(object):
    __slots__ = ["attribute", "values", "unit", "model_times"]
    
    def __init__(self, attribute, unit, values = None,  model_times = None, length = None):
        self.attribute = attribute
        self.unit = unit
        self.model_times = model_times
        if values is None:
            self.values = numpy.empty(length)
        else:
            self.values = values
        
    def copy(self):
        return AttributeValues(self.attribute, self.unit, self.values.copy(), self.model_times)
        
class AttributeList(object):
    
    def __init__(self, particles, attributes = [], lists_of_values = [], units = [], model_times = None):
        d = {}
        for index, particle in enumerate(particles):
            d[id(particle)] = index
        self.mapping_from_particle_to_index = d
        
        if not model_times is None and isinstance(model_times, values.Quantity):
            model_times = numpy.fromfunction(lambda x : model_times, (len(particles),))
        
        self.mapping_from_attribute_to_values_and_unit = {}
        for attribute, values, unit in zip(attributes, lists_of_values, units):
            self.mapping_from_attribute_to_values_and_unit[attribute] = AttributeValues(
                attribute,
                unit,
                values,
                model_times
            )
        
        self.particles = numpy.array(particles)
        
    def copy(self):
        copy = AttributeList([])
        copy.mapping_from_particle_to_index = self.mapping_from_particle_to_index.copy()
        copy.particles = self.particles.copy()
        for attribute, attribute_values in self.mapping_from_attribute_to_values_and_unit.iteritems():
            copy.mapping_from_attribute_to_values_and_unit[attribute] = attribute_values.copy()
        return copy
        
    def get_value_of(self, particle, attribute):
        if not attribute in self.mapping_from_attribute_to_values_and_unit:
            raise AttributeError("particle does not have a "+attribute)
        
        attribute_values = self.mapping_from_attribute_to_values_and_unit[attribute]
        
        index = self.mapping_from_particle_to_index[id(particle)]
        
        return attribute_values.values[index] | attribute_values.unit
        
    def get_values_of_attributes_of_particle(self, particle, attributes):
        
        index = self.mapping_from_particle_to_index[id(particle)]
        result = []
        for attribute in attribute:
            if not attribute in self.mapping_from_attribute_to_values_and_unit:
                raise AttributeError("particle does not have a "+attribute)
            
            attribute_values = self.mapping_from_attribute_to_values_and_unit[attribute]
            
            result.append(attribute_values.values[index] | attribute_values.unit)
        return result
        
    
    def set_value_of(self, particle, attribute, quantity):
        index = self.mapping_from_particle_to_index[id(particle)]
            
        if index is None:
            raise Exception("unknown particle " + particle)
            
        attribute_values = self.get_attributevalues_for(attribute, quantity.unit)
             
        value_to_set = quantity.value_in(attribute_values.unit)
        attribute_values.values[index] = value_to_set
        
            
    def iter_values_of_particle(self, particle):
        index = self.mapping_from_particle_to_index[id(particle)]
        for attribute in self.mapping_from_attribute_to_values_and_unit:
            attribute_values = self.mapping_from_attribute_to_values_and_unit[attribute]
            yield attribute, (attribute_values.values[index] | attribute_values.unit)
    
    
            
    def iter_values_of(self, attribute):
        if not attribute in self.mapping_from_attribute_to_values_and_unit:
            return
            
        attribute_values = self.mapping_from_attribute_to_values_and_unit[attribute]
        values = attribute_values.values
        unit = attribute_values.unit
        particles = self.particles
        
        for index in range(len(self.particles)):
            yield particles[i], (values[i] | unit)
            
    def iter_particles(self):
        index = 0
        for particle in self.particles:
            yield particle
            index += 1
    
    def get_indices_of(self, particles):
        mapping_from_particle_to_index = self.mapping_from_particle_to_index 
        result = numpy.zeros(len(particles),dtype='int32')
        #result = [mapping_from_particle_to_index[id(particle)] for particle in particles]
        
        index = 0
        for index, particle in enumerate(particles):
            result[index] = mapping_from_particle_to_index[id(particle)]
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
    
    def set_values_of_particles_in_units(self, particles, attributes, list_of_values_to_set, source_units, model_times = None):
        indices = self.get_indices_of(particles)
        
        if not model_times is None and isinstance(model_times, values.Quantity):
            model_times = numpy.fromfunction(lambda x : model_times, (len(particles),))
        
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
                    length = len(self.particles)
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
            
                
        other.set_values_of_particles_in_units(self.particles, source_attributes, source_values, source_units)
        
    def remove_particles(self, particles):
        indices = self.get_indices_of(particles)
        
        mapping_from_attribute_to_values_and_unit = self.mapping_from_attribute_to_values_and_unit.copy()
        for attribute in mapping_from_attribute_to_values_and_unit:
            attribute_values = mapping_from_attribute_to_values_and_unit[attribute]
            attribute_values.values = numpy.delete(attribute_values.values,indices)
        
        self.particles = numpy.delete(self.particles,indices)
        
        #self.mapping_from_particle_to_index = None
        d = {}
        index = 0
        for particle in self.particles:
            d[id(particle)] = index
            index += 1
          
        self.mapping_from_particle_to_index = d
        
    def get_attribute_as_vector(self, particle, names_of_the_scalar_attributes):
        index = self.mapping_from_particle_to_index[id(particle)]
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
                length = len(self.particles)
            )
            self.mapping_from_attribute_to_values_and_unit[attribute] = attribute_values
        return attribute_values
        
    def set_attribute_as_vector(self, particle, names_of_the_scalar_attributes, quantity):
        index = self.mapping_from_particle_to_index[id(particle)]
        vector = []
        for i, attribute  in enumerate(names_of_the_scalar_attributes):
            attribute_values = self.get_attributevalues_for(attribute, quantity.unit)
        
            value_to_set = quantity[i].value_in(attribute_values.unit)
            attribute_values.values[index] = value_to_set
            
    def attributes(self):
        return set(self.mapping_from_attribute_to_values_and_unit.keys())
    
        
        
    
    
    
class Particles(object):
    """A set of particle objects"""
    def __init__(self, size = 0):
        self.particles = [Particle(i+1, self) for i in range(size)]
        self.attributelist = AttributeList(self.particles)
        self.history = []
        
    def __iter__(self):
        return self.attributelist.iter_particles()

    def __getitem__(self, index):
        return self.particles[index]
        
    def __len__(self):
        return len(self.particles)
        
    def savepoint(self):
        self.history.append(self.attributelist.copy())
    
    def get_timeline_of_attribute(self, particle, attribute):
        timeline = []
        for x in reversed(self.history):
            timeline.append((None, x.get_value_of(particle, attribute)))
        return timeline
            
    @property
    def mass(self):
        result = []
        for x in self:
            result.append((x.id, x.mass))
        return result
    
    @property
    def ids(self):
        for x in self.particles:
            yield x.id
            
        
class Stars(Particles):
    
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
        
class Measurement(object):
    def __init__(self, timestamp,  attributes, units,  ids, values=None):
        self.timestamp = timestamp
        self.ids = ids
        self.attributes = attributes
        if values == None:
            self.values = zeros((len(attributes), len(ids)))
        else:
            self.values = values
        self.units = units
        
        if self.values.ndim != 2:
            raise Exception("values must be a 2 dimensional array")
        if self.values.shape[0] != len(self.attributes):
            raise Exception("there must be the same number of columns in the values array as there are attributes")
        if len(self.attributes) != len(self.units):
            raise Exception("there must be the same number of attributes as units")
        if self.values.shape[1] != len(ids):
            raise Exception("there must be the same number of rows in the values array as there are ids")
            
        self.ids_to_rownumber = {}
        for rownumber, id in enumerate(self.ids):
            self.ids_to_rownumber[id] = rownumber
            
        self.attribute_to_colnumber = {}
        for colnumber, attribute in enumerate(self.attributes):
            self.attribute_to_colnumber[attribute] = colnumber
            
    def __str__(self):
        rows = []
        columns = map(lambda x : str(x), self.attributes)
        columns.insert(0,'id')
        rows.append(columns)
        
        columns = map(lambda x : str(x), self.units)
        columns.insert(0,'-')
        rows.append(columns)
        rows.append(map(lambda x : '========', range(len(self.units)+1)))
        for i in range(self.values.shape[1]):
            row = [str(self.ids[i])]
            for j in range(self.values.shape[0]):
                row.append(str(self.values[j,i]))
            rows.append(row)
        lines = map(lambda  x : '\t'.join(x), rows)
        return '\n'.join(lines)
        
    def get_value(self, attribute, id):
        rownumber = self.ids_to_rownumber[id]
        colnumber = self.attribute_to_colnumber[attribute]
        return self.values[colnumber][rownumber] | self.units[colnumber]
            
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
    __slots__ = ["id", "attributes", "set", "_module_ids_to_index"]
    
    position = VectorAttribute(("x","y","z"))
    velocity = VectorAttribute(("vx","vy","vz"))
    
    def __init__(self, id = -1, set = None, **keyword_arguments):
        object.__setattr__(self, "id", id)
        object.__setattr__(self, "attributes", {})
        object.__setattr__(self, "_module_ids_to_index", {})
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
