from amuse.legacy import *
from amuse.support.units import nbody_system
from amuse.support.units import units

from amuse.legacy.interface.gd import GravitationalDynamics

class SmallNInterface(LegacyInterface):
    """
        Interface to the Kira Small-N Integrator and Kepler modules from
        Starlab.  http://www.ids.ias.edu/~starlab/
        
        You will need to download Starlab from the above site, make it, install
        it, and then set the STARLAB_INSTALL_PATH variable to be equal to the
        installation directory (typically something like ~/starlab/usr).

        Starlab is available under the GNU General Public Licence (version 2),
        and is developed by:
            * Piet Hut
            * Steve McMillan
            * Jun Makino
            * Simon Portegies Zwart
        Other Starlab Contributors:
            * Douglas Heggie
            * Kimberly Engle
            * Peter Teuben 
            
    """
    include_headers = ['amuse_interface.h']

   

    def __init__(self, convert_nbody = None):
        LegacyInterface.__init__(self, name_of_the_worker='muse_worker_starlab')
        
        self.has_run = False
        self.eps2 = 0.0
        self.time = 0.0

    @legacy_function
    def report_multiples():
        function = LegacyFunctionSpecification()
        function.addParameter('level', 'i', function.IN)
        return function;

    @legacy_function   
    def get_total_energy():
        function = LegacyFunctionSpecification()  
        function.result_type = 'd'
        return function;

    @legacy_function
    def add_to_interaction():
        function = LegacyFunctionSpecification()
        function.addParameter('id', 'i', function.OUT)
        for x in ['m', 'x', 'y', 'z', 'vx', 'vy', 'vz']:
            function.addParameter(x, 'd', function.IN)
        return function;

    @legacy_function
    def get_particle_result():
        function = LegacyFunctionSpecification()
        function.addParameter('k', 'i', function.IN)
        function.addParameter('id', 'i', function.OUT)
        for x in ['mass', 'x', 'y', 'z', 'vx', 'vy', 'vz']:
            function.addParameter(x, 'd', function.OUT)
        return function;

    @legacy_function
    def get_particle_original():
        function = LegacyFunctionSpecification()
        function.addParameter('k', 'i', function.IN)
        function.addParameter('id', 'i', function.OUT)
        for x in ['mass', 'x', 'y', 'z', 'vx', 'vy', 'vz']:
            function.addParameter(x, 'd', function.OUT)
        return function

    @legacy_function
    def integrate_multiple():
        function = LegacyFunctionSpecification()
        function.addParameter('start_time', 'd', function.IN)
        function.addParameter('end_time', 'd', function.OUT)
        function.addParameter('verbose', 'i', function.IN)
        function.addParameter('eps2', 'd', function.IN)
        return function;

    def delete_particle(self, id):
        return -1   # -1 == Not yet implemented.

    def get_time(self):
        return self.time

    def set_time(self, new_time_value):
        self.time = new_time_value
        
    @legacy_function
    def add_binary():
        function = LegacyFunctionSpecification()
        function.addParameter('id1', 'i', function.IN)
        function.addParameter('id2', 'i', function.IN)
        function.addParameter('mass1', 'd', function.IN)
        function.addParameter('mass2', 'd', function.IN)
        function.addParameter('period', 'd', function.IN)
        function.addParameter('eccentricity', 'd', function.IN)
        return function;

    @legacy_function
    def clear_multiple():
        function = LegacyFunctionSpecification()
        return function;

    @legacy_function
    def get_number_of_particles():
        function = LegacyFunctionSpecification()
        function.addParameter('number_of_particles', 'i', function.OUT)
        return function;

    def evolve(self, verbose=False, super_verbose=False):
        """ Evolves the system until a stable configuration is reached. """
        self.has_run = True
        verbose_int = 0
        if verbose:
            verbose_int = 1
        if super_verbose:
            verbose_int = 100
        end_time = self.integrate_multiple(self.time, verbose_int, self.eps2)
        self.time = end_time

    def new_particle(self, mass, radius, x, y, z, vx, vy, vz):
        return (self.add_to_interaction(mass, x, y, z, vx, vy, vz),0)

    def reset_close_encounter(self):
        """ Resets the internal variables so that a new close encounter can be
        run.  This method should be called once before every close encounter to
        ensure that no data remains from the previous close encounter. """
        self.clear_multiple()
        self.time = 0.0

    def get_state(self, index):
        if self.has_run:
            (key, mass, x, y, z, vx, vy, vz) = self.get_particle_result(index)
        else:
            (key, mass, x, y, z, vx, vy, vz) = self.get_particle_original(index)
       
        return mass, x, y, z, vx, vy, vz


        
        
class SmallN(GravitationalDynamics):
    
    
    def __init__(self, convert_nbody = None):
        legacy_interface = SmallNInterface()
        
        GravitationalDynamics.__init__(
            self,
            legacy_interface,
            convert_nbody,
        )     
            
    def define_parameters(self, object):
        object.add_attribute_parameter(
            "eps2",
            "epsilon_squared", 
            "smoothing parameter for gravity calculations", 
            nbody_system.length * nbody_system.length, 
            0.0 | nbody_system.length * nbody_system.length
        )
        object.add_attribute_parameter(
             "number_of_particles",
            "number_of_particles", 
            "The number of particles being managed by the SmallN module", 
            units.none, 
            0 | units.none
        )
    
    def define_properties(self, object):
        object.add_property("get_total_energy", nbody_system.mass * nbody_system.length ** 2  * nbody_system.time ** -2)
        
    def define_state(self, object):
        pass
        
    def define_methods(self, object):
            
        object.add_method(
            'evolve', 
            (nbody_system.time,), 
            public_name = 'evolve_model'
        )

        object.add_method(
            "new_particle", 
            (
                nbody_system.mass,
                nbody_system.length,
                nbody_system.length,
                nbody_system.length,
                nbody_system.length,
                nbody_system.speed,
                nbody_system.speed,
                nbody_system.speed,
            ), 
            ( 
                object.NO_UNIT,
                object.ERROR_CODE
            )
        )
        object.add_method(
            "delete_particle", 
            (
                object.NO_UNIT,
            ), 
            ( 
                object.ERROR_CODE,
            )
        )
        object.add_method(
            "get_state", 
            (
                object.NO_UNIT,
            ), 
            (
                nbody_system.mass,
                nbody_system.length,
                nbody_system.length,
                nbody_system.length,
                nbody_system.speed,
                nbody_system.speed,
                nbody_system.speed,
            )
        )
        object.add_method(
            "get_time", 
            (        
            ), 
            nbody_system.time
        )
        object.add_method(
            "set_time", 
            (
                nbody_system.time,
            ), 
            ( 
            )
        )
    
        
    
    def define_particle_sets(self, object):
        object.define_set('particles', 'index_of_the_particle')
        object.set_new('particles', 'new_particle')
        object.set_delete('particles', 'delete_particle')
        object.add_getter('particles', 'get_state', names = ('mass','x', 'y','z', 'vx','vy','vz'))
        
    
  
        
        
    
    

