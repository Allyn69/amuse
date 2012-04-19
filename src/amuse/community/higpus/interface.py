from amuse.community import *
from amuse.community.interface.gd import GravitationalDynamics 
from amuse.community.interface.gd import GravitationalDynamicsInterface

class HiGPUsInterface(CodeInterface, GravitationalDynamicsInterface):
    
    include_headers = ['worker_code.h']
	    
    def __init__(self, **keyword_arguments):
	CodeInterface.__init__(self, name_of_the_worker="higpus_worker_gpu", **keyword_arguments)
    
    @legacy_function
    def echo_int():
	function = LegacyFunctionSpecification()  
      	function.addParameter('int_in', dtype='int32', direction=function.IN)
      	function.addParameter('int_out', dtype='int32', direction=function.OUT)
      	function.result_type = 'int32'
      	function.can_handle_array = True
      	return function

    @legacy_function
    def new_particle():
      	function = LegacyFunctionSpecification()
      	function.can_handle_array = True
      	function.addParameter('index_of_the_particle', dtype='int32', direction=function.OUT)
      	function.addParameter('mass', dtype='float64', direction=function.IN,
		 description = "The mass of the particle")
        function.addParameter('radius', dtype='float64', direction=function.IN,
                 description = "The radius of the particle")
        function.addParameter('x', dtype='float64', direction=function.IN,
                 description = "The initial position vector of the particle")
        function.addParameter('y', dtype='float64', direction=function.IN,
                 description = "The initial position vector of the particle")
        function.addParameter('z', dtype='float64', direction=function.IN,
                 description = "The initial position vector of the particle")
        function.addParameter('vx', dtype='float64', direction=function.IN,
                 description = "The initial velocity vector of the particle")
        function.addParameter('vy', dtype='float64', direction=function.IN,
                 description = "The initial velocity vector of the particle")
        function.addParameter('vz', dtype='float64', direction=function.IN,
                 description = "The initial velocity vector of the particle")
        function.result_type = 'int32'
        return function
        
    @legacy_function
    def evolve_model():
        function = LegacyFunctionSpecification()
        function.can_handle_array = True
        function.addParameter('dt', dtype='float64', direction=function.IN)
        function.result_type = 'int32'
        return function

    @legacy_function
    def set_time_begin():
	function = LegacyFunctionSpecification()
        function.addParameter('time_begin', dtype='float64', direction=function.IN, description = "start time.")
	function.result_type = 'int32'
        return function

    @legacy_function
    def get_time_begin():
	function = LegacyFunctionSpecification()
        function.addParameter('time_begin', dtype='float64', direction=function.OUT, description = "start time.")
        function.result_type = 'int32'
        return function
    
    @legacy_function
    def set_eta6():
	function = LegacyFunctionSpecification()
        function.addParameter('eta6', dtype='float64', direction=function.IN, description = "eta parameter of time steps.")
        function.result_type = 'int32'
        return function

    @legacy_function
    def get_eta6():
	function = LegacyFunctionSpecification()
        function.addParameter('eta6', dtype='float64', direction=function.OUT, description = "eta parameter of time steps.")
        function.result_type = 'int32'
        return function

    @legacy_function
    def set_eta4():
        function = LegacyFunctionSpecification()
        function.addParameter('eta4', dtype='float64', direction=function.IN, description = "eta parameter of time steps.")
        function.result_type = 'int32'
        return function

    @legacy_function
    def get_eta4():
        function = LegacyFunctionSpecification()
        function.addParameter('eta4', dtype='float64', direction=function.OUT, description = "eta parameter of time steps.")
        function.result_type = 'int32'
        return function

    @legacy_function
    def set_Plummer_core():
        function = LegacyFunctionSpecification()
        function.addParameter('Plummer_core', dtype='float64', direction=function.IN, description = "radius parameter for plummer potential.")
        function.result_type = 'int32'
        return function

    @legacy_function
    def get_Plummer_core():
        function = LegacyFunctionSpecification()
        function.addParameter('Plummer_core', dtype='float64', direction=function.OUT, description = "radius parameter for plummer potential.")
        function.result_type = 'int32'
        return function

    @legacy_function
    def set_Plummer_mass():
        function = LegacyFunctionSpecification()
        function.addParameter('Plummer_mass', dtype='float64', direction=function.IN, description = "analytical mass of the plummer potential.")
        function.result_type = 'int32'
        return function

    @legacy_function
    def get_Plummer_mass():
        function = LegacyFunctionSpecification()
        function.addParameter('Plummer_mass', dtype='float64', direction=function.OUT, description = "analytical mass of the plummer potential.")
        function.result_type = 'int32'
        return function

    @legacy_function
    def set_eps():
	function = LegacyFunctionSpecification()
        function.addParameter('epsilon', dtype='float64', direction=function.IN, description = "softening parameter.")
        function.result_type = 'int32'
        return function

    @legacy_function
    def get_eps():
	function = LegacyFunctionSpecification()
        function.addParameter('epsilon', dtype='float64', direction=function.OUT, description = "softening parameter.")
        function.result_type = 'int32'
        return function
   
    @legacy_function
    def set_number_of_GPU():
        function = LegacyFunctionSpecification()
        function.addParameter('number_of_GPU', dtype='int32', direction=function.IN, description = "number of GPU.")
        function.result_type = 'int32'
        return function

    @legacy_function
    def get_number_of_GPU():
        function = LegacyFunctionSpecification()
        function.addParameter('number_of_GPU', dtype='int32', direction=function.OUT, description = "number of GPU.")
        function.result_type = 'int32'
        return function

    @legacy_function
    def set_number_of_Threads():
        function = LegacyFunctionSpecification()
        function.addParameter('number_of_Threads', dtype='int32', direction=function.IN, description = "number of Threads per block.")
        function.result_type = 'int32'
        return function

    @legacy_function
    def get_number_of_Threads():
        function = LegacyFunctionSpecification()
        function.addParameter('number_of_Threads', dtype='int32', direction=function.OUT, description = "number of Threads per block.")
        function.result_type = 'int32'
        return function

    @legacy_function
    def set_number_of_Print():
        function = LegacyFunctionSpecification()
        function.addParameter('number_of_Print', dtype='int32', direction=function.IN, description = "number of total file to print.")
        function.result_type = 'int32'
        return function

    @legacy_function
    def get_number_of_Print():
        function = LegacyFunctionSpecification()
        function.addParameter('number_of_Print', dtype='int32', direction=function.OUT, description = "number of total file to print.")
        function.result_type = 'int32'
        return function

    @legacy_function
    def get_number_of_particles():
        function = LegacyFunctionSpecification()
        function.addParameter('number_of_particles', dtype='int32', direction=function.OUT, description = "number of particles.")
        function.result_type = 'int32'
        return function

    @legacy_function
    def set_DTPrint():
        function = LegacyFunctionSpecification()
        function.addParameter('DTPrint', dtype='float64', direction=function.IN, description = "unit time of snapshot.")
        function.result_type = 'int32'
        return function

    @legacy_function
    def get_DTPrint():
	function = LegacyFunctionSpecification()
        function.addParameter('DTPrint', dtype='float64', direction=function.OUT, description = "unit time of snapshot.")
        function.result_type = 'int32'
        return function

    @legacy_function
    def set_max_time_step():
        function = LegacyFunctionSpecification()
        function.addParameter('max_time_step', dtype='float64', direction=function.IN, description = "exponent of the maximum time step used.")
        function.result_type = 'int32'
        return function

    @legacy_function
    def get_max_time_step():
        function = LegacyFunctionSpecification()
        function.addParameter('max_time_step', dtype='float64', direction=function.OUT, description = "maximum time step used.")
        function.result_type = 'int32'
        return function

    @legacy_function
    def set_min_time_step():
        function = LegacyFunctionSpecification()
        function.addParameter('min_time_step', dtype='float64', direction=function.IN, description = "exponent of the minimum time step used.")
        function.result_type = 'int32'
        return function

    @legacy_function
    def get_min_time_step():
        function = LegacyFunctionSpecification()
        function.addParameter('min_time_step', dtype='float64', direction=function.OUT, description = "minimum time step used.")
        function.result_type = 'int32'
        return function

    @legacy_function
    def set_gpu_name():
        function = LegacyFunctionSpecification()
        function.addParameter('gpu_name', dtype='string', direction=function.IN, description = "name of the GPU used.")
        function.result_type = 'int32'
        return function

    @legacy_function
    def get_gpu_name():
        function = LegacyFunctionSpecification()
        function.addParameter('gpu_name', dtype='string', direction=function.OUT, description = "name of the GPU used.")
        function.result_type = 'int32'
        return function



class HiGPUs(GravitationalDynamics):

    def __init__(self, convert_nbody = None, **keyword_arguments):
        legacy_interface = HiGPUsInterface(**keyword_arguments)

        GravitationalDynamics.__init__(self,  
                                       legacy_interface,
                                       convert_nbody,
                                       **keyword_arguments)


    def define_parameters(self, object):
        object.add_method_parameter(
            "get_eta4",			          
            "set_eta4",			         
            "eta_4",                  
            "timestep parameter",    
            default_value = 0.01)

        object.add_method_parameter(
            "get_eta6",                          
            "set_eta6",                          
            "eta_6",                             
            "timestep parameter",                
            default_value = 0.4)

        object.add_method_parameter(
            "get_time_begin",                    
            "set_time_begin",                    
            "start_time",                        
            "start time",                        
            default_value = 0.0 | nbody_system.time
        )

        object.add_method_parameter(
            "get_Plummer_core",                  
            "set_Plummer_core",                  
            "r_core_plummer",                    
            "radius of Plummer potential",       
            default_value = 0.0 | nbody_system.length
        )

        object.add_method_parameter(
            "get_Plummer_mass",                  
            "set_Plummer_mass",                  
            "mass_plummer",                      
            "mass of Plummer potential",         
            default_value = 0.0 | nbody_system.mass
        )

        object.add_method_parameter(
            "get_eps",		                 
            "set_eps",          	         
            "softening",                         
            "softening",           	         
            default_value = 0.001 | nbody_system.length
        )

        object.add_method_parameter(
            "get_number_of_Threads",              
            "set_number_of_Threads",              
            "Threads",                            
     "Threads per block",                  
            default_value = 128
        )

        object.add_method_parameter(
            "get_number_of_Print",                
            "set_number_of_Print",                
            "n_Print",                            
     "start number to print file",         
            default_value = 1000000
        )

        object.add_method_parameter(
            "get_DTPrint",                        
            "set_DTPrint",                        
            "dt_Print",                           
     "time for snapshot",                  
            default_value = 1.0 | nbody_system.time
        )

        object.add_method_parameter(
            "get_max_time_step",                  
            "set_max_time_step",                  
            "max_step",                           
     "power of 2 for maximum time step",   
            default_value = -3.0 | nbody_system.time
        )

        object.add_method_parameter(
            "get_min_time_step",                  
            "set_min_time_step",                  
            "min_step",                           
            "power of 2 for minmum time step",    
            default_value = -30.0 | nbody_system.time
        )

        object.add_method_parameter(
            "get_gpu_name",                       
            "set_gpu_name",                       
            "gpu_name",                           
            "gpu name",                           
            default_value = "GeForce GTX 480"
        )

        object.add_method_parameter(
            "get_number_of_GPU",                  
            "set_number_of_GPU",                  
            "n_gpu",                              
            "number of gpus per node",            
            default_value = 2
        )



    def define_methods(self, object):
        GravitationalDynamics.define_methods(self, object)
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
               	object.INDEX,
                object.ERROR_CODE
            )
	)
        object.add_method(
            "set_time_begin",
            (
             	nbody_system.time
            ),
            (
             	object.ERROR_CODE
            )
	)
        object.add_method(
            "get_time_begin",
            (),
            (
             	nbody_system.time,
                object.ERROR_CODE
            )
	)
        object.add_method(
            "set_Plummer_core",
            (
               	nbody_system.length
            ),
            (
             	object.ERROR_CODE
            )
        )

        object.add_method(
            "get_Plummer_core",
            (),
            (
               	nbody_system.length,
                object.ERROR_CODE
            )
        )

        object.add_method(
            "set_Plummer_mass",
            (
               	nbody_system.mass
            ),
            (
             	object.ERROR_CODE
            )
        )

        object.add_method(
            "get_Plummer_mass",
            (),
            (
               	nbody_system.mass,
                object.ERROR_CODE
            )
        )

        object.add_method(
            "set_eta6",
            (
                object.NO_UNIT
            ),
            (
                object.ERROR_CODE
            )
        )

        object.add_method(
            "get_eta6",
            (),
            (
                object.NO_UNIT,
                object.ERROR_CODE
            )
        )

        object.add_method(
            "set_eta4",
            (
                object.NO_UNIT
            ),
            (
             	object.ERROR_CODE
            )
        )

        object.add_method(
            "get_eta4",
            (),
            (
                object.NO_UNIT,
                object.ERROR_CODE
            )
	)


        object.add_method(
            "set_eps",
            (
                nbody_system.length
            ),
            (
                object.ERROR_CODE
            )
        )

        object.add_method(
	    "get_eps",
            (),
	    (
             	nbody_system.length,
                object.ERROR_CODE
            )
	)


	object.add_method(
            "set_number_of_GPU",
            (
             	object.NO_UNIT
            ),
            (
             	object.ERROR_CODE
            )
	)

	object.add_method(
            "get_number_of_GPU",
            (),
            (
             	object.NO_UNIT,
                object.ERROR_CODE
            )
	)

        object.add_method(
            "set_number_of_particles",
            (
                object.NO_UNIT
            ),
            (
                object.ERROR_CODE
            )
        )

        object.add_method(
            "get_number_of_particles",
            (),
            (
                object.NO_UNIT,
                object.ERROR_CODE
            )
        )


        object.add_method(
            "set_number_of_Threads",
            (
                object.NO_UNIT
            ),
            (
             	object.ERROR_CODE
            )
        )

        object.add_method(
            "get_number_of_Threads",
            (),
            (
             	object.NO_UNIT,
                object.ERROR_CODE
            )
	)

	object.add_method(
            "set_number_of_Print",
            (
             	object.NO_UNIT
            ),
            (
             	object.ERROR_CODE
            )
	)

	object.add_method(
            "get_number_of_Print",
            (),
            (
             	object.NO_UNIT,
                object.ERROR_CODE
            )
	)

        object.add_method(
            "set_DTPrint",
            (
                nbody_system.time
            ),
            (
             	object.ERROR_CODE
            )
	)

	object.add_method(
            "get_DTPrint",
            (),
            (
             	nbody_system.time,
                object.ERROR_CODE
            )
	)

        object.add_method(
            "set_max_time_step",
            (
             	nbody_system.time
	    ),
            (
                object.ERROR_CODE
            )
        )

        object.add_method(
            "get_max_time_step",
            (),
            (
                nbody_system.time,
	        object.ERROR_CODE
            )
	)

	object.add_method(
            "set_min_time_step",
            (
             	nbody_system.time
            ),
            (
             	object.ERROR_CODE
            )
	)

        object.add_method(
            "get_min_time_step",
            (),
            (
             	nbody_system.time,
                object.ERROR_CODE
            )
	)

	object.add_method(
            "set_gpu_name",
            (
                object.NO_UNIT
            ),
            (
             	object.ERROR_CODE
            )
	)

	object.add_method(
            "get_gpu_name",
            (),
            (
             	object.NO_UNIT,
                object.ERROR_CODE
            )
	)


    def define_particle_sets(self, object):
        GravitationalDynamics.define_particle_sets(self, object)


