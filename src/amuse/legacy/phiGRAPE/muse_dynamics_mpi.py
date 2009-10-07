import numpy

from amuse.support.units import nbody_system
from amuse.support.units import units
from amuse.legacy import *


class PhiGRAPE(LegacyInterface):   
    parameter_definitions = [
        parameters.ModuleMethodParameterDefinition(
            "get_eps", "set_eps",
            "epsilon_squared", 
            "smoothing parameter for gravity calculations", 
            nbody_system.length * nbody_system.length, 
            0.0 | nbody_system.length * nbody_system.length
        ),
        parameters.ModuleMethodParameterDefinition(
            "get_eta", "set_eta1",
            "eta", 
            "timestep parameter", 
            units.none , 
            0.01 |  units.none
        ),
        parameters.ModuleMethodParameterDefinition(
            "get_eta_s", "set_eta_s",
            "eta_s", 
            "parameter to determine the initial timestep", 
            units.none , 
            0.002 |  units.none
        ),
    ]
    
             
    def __init__(self, convert_nbody = None):
        LegacyInterface.__init__(self)
        self.convert_nbody = convert_nbody
        self.parameters = parameters.Parameters(self.parameter_definitions, self)

    @legacy_function   
    def setup_module():
        function = RemoteFunction()  
        function.result_type = 'i'
        return function
        
    @legacy_function      
    def cleanup_module():
        function = RemoteFunction()  
        function.result_type = 'i'
        return function
    
    @legacy_function    
    def initialize_particles():
        function = RemoteFunction()  
        function.addParameter('time', dtype='d', direction=function.IN)
        function.result_type = 'i'
        return function;

    @legacy_function  
    def reinitialize_particles():
        function = RemoteFunction()  
        function.result_type = 'i'
        return function
                
    @legacy_function    
    def add_particle():
        function = RemoteFunction()  
        function.can_handle_array = True
        function.addParameter('id', dtype='i', direction=function.IN)
        for x in ['mass','radius','x','y','z','vx','vy','vz']:
            function.addParameter(x, dtype='d', direction=function.IN)
        function.result_type = 'i'
        return function

    @legacy_function    
    def evolve():
        function = RemoteFunction()  
        function.addParameter('time_end', dtype='d', direction=function.IN)
        function.addParameter('synchronize', dtype='i', direction=function.IN)
        function.result_type = 'i'
        return function
        
    @legacy_function   
    def get_number():
        function = RemoteFunction()  
        function.result_type = 'i'
        return function;

    @legacy_function   
    def get_eps2():
        function = RemoteFunction()  
        function.result_type = 'd'
        return function;

             
    @legacy_function    
    def get_state():
        function = RemoteFunction()  
        function.addParameter('id', dtype='i', direction=function.IN)
        for x in ['mass','radius','x','y','z','vx','vy','vz']:
            function.addParameter(x, dtype='d', direction=function.OUT)
        return function

    @legacy_function      
    def get_potential():
        function = RemoteFunction()  
        function.addParameter('id', dtype='i', direction=function.IN)
        function.result_type = 'd'
        return function

        
    @legacy_function
    def set_mass():
        function = RemoteFunction()  
        function.result_type = 'i'
        function.addParameter('id', dtype='i', direction=function.IN)
        function.addParameter('mass', dtype='d', direction=function.IN)
        return function;

    @legacy_function      
    def get_time():
        function = RemoteFunction()
        function.result_type = 'd'
        return function

    @legacy_function      
    def get_time_step():
        function = RemoteFunction()  
        function.result_type = 'd'
        return function

    @legacy_function      
    def set_eps():
        function = RemoteFunction()  
        function.addParameter('eps2', dtype='d', direction=function.IN)
        return function

    @legacy_function      
    def set_eta():
        function = RemoteFunction()  
        function.addParameter('etas', dtype='d', direction=function.IN)
        function.addParameter('eta', dtype='d', direction=function.IN)
        return function

    @legacy_function      
    def set_eta_s():
        function = RemoteFunction()  
        function.addParameter('value', dtype='d', direction=function.IN)
        return function

    @legacy_function      
    def set_eta1():
        function = RemoteFunction()  
        function.addParameter('value', dtype='d', direction=function.IN)
        return function


    @legacy_function      
    def get_eta():
        function = RemoteFunction()  
        function.result_type = 'd'
        return function
        
    @legacy_function      
    def get_eta_s():
        function = RemoteFunction()  
        function.result_type = 'd'
        return function


    @legacy_function      
    def get_kinetic_energy():
        function = RemoteFunction()  
        function.result_type = 'd'
        return function

    @legacy_function      
    def get_potential_energy():
        function = RemoteFunction()  
        function.result_type = 'd'
        return function

    @legacy_function      
    def get_energy_error():
        function = RemoteFunction()  
        function.result_type = 'd'
        return function

    def get_energies(self):
        energy_unit = nbody_system.mass * nbody_system.length ** 2  * nbody_system.time ** -2
        kinetic_energy = self.get_kinetic_energy() | energy_unit
        potential_energy = self.get_potential_energy() | energy_unit
        return (self.convert_nbody.to_si(kinetic_energy), self.convert_nbody.to_si(potential_energy))

    @legacy_function      
    def find_colliding_secondary():
        function = RemoteFunction()  
        function.addParameter('id1', dtype='i', direction=function.IN)
        function.result_type = 'i'
        return function

    @legacy_function          
    def remove_particle():
        function = RemoteFunction()  
        function.addParameter('id', dtype='i', direction=function.IN)
        function.result_type = 'i'
        return function    
        
    def add_star(self, star):
        id = star.id
        mass = self.convert_nbody.to_nbody(star.mass.value())
        position = self.convert_nbody.to_nbody(star.position.value())
        velocity = self.convert_nbody.to_nbody(star.velocity.value())
        
        mass = mass.number
        x = position.number[0]
        y = position.number[1]
        z = position.number[2]
        vx = velocity.number[0]
        vy = velocity.number[1]
        vz = velocity.number[2]
        radius = self.convert_nbody.to_nbody(star.radius.value()).number
        self.add_particle(id, mass, radius, x, y, z, vx, vy, vz)
        
    def update_star(self, star):
        state = self.get_state(star.id)
        time = self.convert_nbody.to_si( 0.0 | nbody_system.time)
        #star.mass.set_value_at_time(time, self.convert_nbody.to_si(nbody_system.mass(state.mass)))
        star.position.set_value_at_time(time, self.convert_nbody.to_si(nbody_system.length(numpy.array((state['x'], state['y'], state['z'])))))
        star.velocity.set_value_at_time(time, self.convert_nbody.to_si(nbody_system.speed(numpy.array((state['vx'], state['vy'], state['vz'])))))
        return star
         
    def evolve_model(self, time_end):
        result = self.evolve(self.convert_nbody.to_nbody(time_end).number, 0.0)
        return result
    
    def add_particles(self, particles):
        for x in particles:
            self.add_star(x)
            
    def update_particles(self, particles):
        for x in particles:
            self.update_star(x)
            
    def xadd_particles(self, particles):
        mass = []
        x_ = []
        y = []
        z = []
        vx = []
        vy = []
        vz = []
        radius = []
        id = []
        for x in particles:
            #self.update_star(x)
            id.append(x.id)
            mass_ = self.convert_nbody.to_nbody(x.mass.value())
            position = self.convert_nbody.to_nbody(x.position.value())
            velocity = self.convert_nbody.to_nbody(x.velocity.value())
            
            mass.append(mass_.number)
            x_.append(position.number[0])
            y.append(position.number[1])
            z.append(position.number[2])
            vx.append(velocity.number[0])
            vy.append(velocity.number[1])
            vz.append(velocity.number[2])
            radius.append(self.convert_nbody.to_nbody(x.radius.value()).number)
        self._add_particle(id, mass, radius, x_, y, z, vx, vy, vz)
            
    def update_attributes(self, attributes):
        for id, x in attributes:
            if x.name == 'mass':
                self.set_mass(id, self.convert_nbody.to_nbody(x.value()).number)
        
    
  
