import numpy
from amuse.support.units import nbody_system
from amuse.legacy import *

class Hermite(LegacyInterface):
    include_headers = ['muse_dynamics.h', 'parameters.h', 'local.h']
    
    t = legacy_global(name='t',id=20,dtype='d')
    dt_param = legacy_global(name='dt_param',id=21,dtype='d')
    dt_dia = legacy_global(name='dt_dia',id=22,dtype='d')
    eps2 = legacy_global(name='eps2',id=23,dtype='d')
    flag_collision = legacy_global(name='flag_collision',id=24,dtype='i')
            
    def __init__(self, convert_nbody = nbody_system.noconvert_nbody_to_si()):
        LegacyInterface.__init__(self)
        self.convert_nbody = convert_nbody

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
    def add_particle():
        function = RemoteFunction() 
        function.can_handle_array = True
        function.addParameter('id', dtype='i', direction=function.IN)
        for x in ['mass','radius','x','y','z','vx','vy','vz']:
            function.addParameter(x, dtype='d', direction=function.IN)
        function.result_type = 'i'
        return function
        
    @legacy_function    
    def get_state():
        function = RemoteFunction()  
        function.can_handle_array = True
        function.addParameter('id', dtype='i', direction=function.IN)
        function.addParameter('id_out', dtype='i', direction=function.OUT)
        for x in ['mass','radius','x','y','z','vx','vy','vz']:
            function.addParameter(x, dtype='d', direction=function.OUT)
        function.result_type = None
        return function
        
    @legacy_function    
    def evolve():
        function = RemoteFunction()  
        function.addParameter('time_end', dtype='d', direction=function.IN)
        function.addParameter('synchronize', dtype='i', direction=function.IN)
        function.result_type = 'i'
        return function
        
    @legacy_function  
    def reinitialize_particles():
        function = RemoteFunction() 
        function.result_type = 'i'
        return function
        
    @legacy_function   
    def get_number():
        function = RemoteFunction()  
        function.result_type = 'i'
        return function;
     
    @legacy_function
    def set_mass():
        function = RemoteFunction() 
        function.result_type = 'i'
        function.addParameter('id', dtype='i', direction=function.IN)
        function.addParameter('mass', dtype='d', direction=function.IN)
        return function;
        
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
        time = self.convert_nbody.to_si( self.t | nbody_system.time)
        #star.mass.set_value_at_time(time, self.convert_nbody.to_si(nbody_system.mass(state.mass)))
        star.position.set_value_at_time(time, self.convert_nbody.to_si(nbody_system.length(numpy.array((state['x'], state['y'], state['z'])))))
        star.velocity.set_value_at_time(time, self.convert_nbody.to_si(nbody_system.speed(numpy.array((state['vx'], state['vy'], state['vz'])))))
        return star
         
    def evolve_model(self, time_end):
        result = self.evolve(self.convert_nbody.to_nbody(time_end).number, 0.0)
        return result
        
    def set_eps2(self, eps2):
        self.eps2 = self.convert_nbody.to_nbody(eps2).number
    
    
    def _add_particles(self, particles):
        for x in particles:
            self.add_star(x)
            
    def update_particles(self, particles):
        for x in particles:
            self.update_star(x)
            
    def add_particles(self, particles):
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
        self.add_particle(id, mass, radius, x_, y, z, vx, vy, vz)
            
    def update_attributes(self, attributes):
        
        ids = []
        mass_of_particles = []
        for id, x in attributes:
            if x.name == 'mass':
                id.append(x.id)
                mass = self.convert_nbody.to_nbody(x.mass.value())
                mass_of_particles.append(mass.number)
        self.set_mass(ids, mass_of_particles)
        
    
    def get_energies(self):
        energy_unit = nbody_system.mass * nbody_system.length ** 2  * nbody_system.time ** -2
        kinetic_energy = self.get_kinetic_energy() | energy_unit
        potential_energy = self.get_potential_energy() | energy_unit
        return (self.convert_nbody.to_si(kinetic_energy), self.convert_nbody.to_si(potential_energy))
        
    
  
