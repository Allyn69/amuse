from amuse.legacy import *
from amuse.legacy.interface.gd import GravitationalDynamics
from amuse.legacy.interface.gd import NBodyGravitationalDynamicsBinding
from amuse.legacy.support.lit import LiteratureRefs
from amuse.support.data.core import Particles,ParticlesWithUnitsConverted
from amuse.support.data import binding


class BHTreeInterface(LegacyInterface, LiteratureRefs, GravitationalDynamics):
    """
        .. [#] Barnes, J., Hut, P., A Hierarchical O(N log N) force-calculation algorithm, *Nature*, **4**, 324 (1986)   
    """
    include_headers = ['BHTree_code.h', 'parameters.h', 'local.h']
    
    timestep = legacy_global(name='timestep',id=21,dtype='d')
    eps2_for_gravity = legacy_global(name='eps2_for_gravity',id=22,dtype='d')
    theta_for_tree = legacy_global(name='theta_for_tree',id=23,dtype='d')
    
    use_self_gravity = legacy_global(name='use_self_gravity',id=24,dtype='i')
    ncrit_for_tree = legacy_global(name='ncrit_for_tree',id=25,dtype='i')
    
    dt_dia = legacy_global(name='dt_dia',id=246,dtype='d')

    def __init__(self, convert_nbody = None, **kwargs):
        LegacyInterface.__init__(self, name_of_the_worker="worker_code", **kwargs)
        """
        self.parameters = parameters.Parameters(self.parameter_definitions, self)
        if convert_nbody is None:
            convert_nbody = nbody_system.nbody_to_si.get_default()
            
        self.convert_nbody = convert_nbody
        """
        LiteratureRefs.__init__(self)

    @legacy_function   
    def setup_module():
        function = LegacyFunctionSpecification() 
        function.result_type = 'i'
        return function
   
    @legacy_function      
    def cleanup_module():
        function = LegacyFunctionSpecification()  
        function.result_type = 'i'
        return function
    
    @legacy_function    
    def initialize_particles():
        function = LegacyFunctionSpecification() 
        function.addParameter('time', dtype='d', direction=function.IN)
        function.result_type = 'i'
        return function;
       
    @legacy_function  
    def reinitialize_particles():
        function = LegacyFunctionSpecification()  
        function.result_type = 'i'
        return function


class BHTreeInCodeAttributeStorage(InCodeAttributeStorage):
    new_particle_method = binding.NewParticleMethod(
        "new_particle", 
        (
            ("mass", "mass", nbody_system.mass),
            ("radius", "radius", nbody_system.length),
            ("x", "x", nbody_system.length),
            ("y", "y", nbody_system.length),
            ("z", "z", nbody_system.length),
            ("vx", "vx", nbody_system.speed),
            ("vy", "vy", nbody_system.speed),
            ("vz", "vz", nbody_system.speed),
        )
    )
    
    getters = (
        binding.ParticleGetAttributesMethod(
            "get_state",
            (
                ("mass", "mass", nbody_system.mass),
                ("radius", "radius", nbody_system.length),
                ("x", "x", nbody_system.length),
                ("y", "y", nbody_system.length),
                ("z", "z", nbody_system.length),
                ("vx", "vx", nbody_system.speed),
                ("vy", "vy", nbody_system.speed),
                ("vz", "vz", nbody_system.speed),
            )
        ),
        binding.ParticleGetAttributesMethod(
            "get_mass",
            (
                ("mass", "mass", nbody_system.mass),
            )
        ),
        binding.ParticleGetAttributesMethod(
            "get_radius",
            (
                ("radius", "radius", nbody_system.length),
            )
        ),
        binding.ParticleGetAttributesMethod(
            "get_position",
            (
                ("x", "x", nbody_system.length),
                ("y", "y", nbody_system.length),
                ("z", "z", nbody_system.length),
            )
        ),
    )
    
    
    setters = (
        binding.ParticleSetAttributesMethod(
            "set_mass",
            (
                ("mass", "mass", nbody_system.mass),
            )
        ),
        binding.ParticleSetAttributesMethod(
            "set_radius",
            (
                ("radius", "radius", nbody_system.length),
            )
        ),
        binding.ParticleSetAttributesMethod(
            "set_position",
            (
                ("x", "x", nbody_system.length),
                ("y", "y", nbody_system.length),
                ("z", "z", nbody_system.length),
            )
        ),
        
    )

   
class BHTreeNBody(BHTreeInterface, NBodyGravitationalDynamicsBinding):

    parameter_definitions = [
        parameters.ModuleAttributeParameterDefinition(
            "eps2_for_gravity",
            "epsilon_squared", 
            "smoothing parameter for gravity calculations", 
            nbody_system.length * nbody_system.length, 
            0.3 | nbody_system.length * nbody_system.length
        )
        ,
        parameters.ModuleAttributeParameterDefinition(
            "timestep",
            "timestep", 
            "constant timestep for iteration", 
            nbody_system.time, 
            0.7 | nbody_system.time
        )
        ,
        parameters.ModuleAttributeParameterDefinition(
            "theta_for_tree",
            "openings_angle", 
            "openings angle for building the tree between 0 and 1", 
            units.none,
            0.5 | units.none
        )
        
    ]
    

    def __init__(self):
        BHTreeInterface.__init__(self)
        NBodyGravitationalDynamicsBinding.__init__(self)
        
        self.particles = Particles(storage = BHTreeInCodeAttributeStorage(self))
        
    def current_model_time(self):
        return self.model_time
    
       
class BHTree(CodeInterfaceWithNBodyUnitsConverted):
    def __init__(self, convert_nbody = None):
        CodeInterfaceWithNBodyUnitsConverted.__init__(
            self,
            BHTreeNBody(),
            convert_nbody
        )
    
            
