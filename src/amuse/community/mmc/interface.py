from amuse.community import *
from amuse.support.options import OptionalAttributes, option
import os
class mmcInterface(LegacyInterface):
    
    use_modules = ['MMC']
    
    def __init__(self, **keyword_arguments):
        LegacyInterface.__init__(self, **keyword_arguments)

    @option(type="string")
    def data_directory(self):
        """
        The root name of the directory for the EVTwin
        application data files. This directory should contain the
        zams data and init.run and init.dat.
        """
        return os.path.join(get_amuse_root_dir(), 'data', 'mmc')

    @legacy_function
    def nonstandard_init():
        function = LegacyFunctionSpecification()
        function.result_type = 'int32'
        return function
    
    @legacy_function
    def commit_parameters():
        function = LegacyFunctionSpecification()
        function.result_type = 'int32'
        return function

    @legacy_function
    def set_mmc_data_directory():
        function = LegacyFunctionSpecification()
        function.addParameter('data_directory', dtype='string', direction=function.IN)
        function.result_type = 'int32'
        return function

    @legacy_function
    def new_particle():
        function = LegacyFunctionSpecification()
        function.can_handle_array = True
        function.addParameter('index_of_the_particle', dtype='int32', direction=function.OUT)
        function.addParameter('x', dtype='float64', direction=function.IN)
        function.addParameter('y', dtype='float64', direction=function.IN)
        function.addParameter('z', dtype='float64', direction=function.IN)
        function.result_type = 'int32'
        return function

    @legacy_function
    def delete_particle():
        function = LegacyFunctionSpecification()  
        function.addParameter('index_of_the_particle', dtype='int32', direction=function.IN)
        function.result_type = 'int32'
        return function

    @legacy_function
    def get_state():
        function = LegacyFunctionSpecification()
        function.can_handle_array = True 
        function.addParameter('index_of_the_particle', dtype='int32', direction=function.IN)
        function.addParameter('x', dtype='float64', direction=function.OUT)
        function.addParameter('y', dtype='float64', direction=function.OUT)
        function.addParameter('z', dtype='float64', direction=function.OUT)
        function.result_type = 'int32'
        return function
        
    @legacy_function
    def set_state():
        function = LegacyFunctionSpecification()  
        function.can_handle_array = True 
        function.addParameter('index_of_the_particle', dtype='int32', direction=function.IN)
        function.addParameter('x', dtype='float64', direction=function.IN)
        function.addParameter('y', dtype='float64', direction=function.IN)
        function.addParameter('z', dtype='float64', direction=function.IN)
        function.result_type = 'int32'
        return function    

    @legacy_function
    def get_time():
        function = LegacyFunctionSpecification()  
        function.addParameter('time', dtype='float64', direction=function.OUT)
        function.result_type = 'int32'
        return function

    @legacy_function
    def get_kinetic_energy():
        function = LegacyFunctionSpecification()  
        function.addParameter('Ek', dtype='float64', direction=function.OUT)
        function.result_type = 'int32'
        return function

    @legacy_function
    def initial_run():
        function = LegacyFunctionSpecification()  
        function.addParameter('res', dtype='int32', direction=function.OUT)
        function.result_type = 'int32'
        return function

    @legacy_function
    def run():
        function = LegacyFunctionSpecification()
        function.result_type = 'int32'
        return function    
    
    @legacy_function
    def get_number_of_particles():
        function = LegacyFunctionSpecification()  
        function.can_handle_array = True 
        function.addParameter('value', dtype='int32', direction=function.OUT)
        function.result_type = 'int32'
        return function    

    @legacy_function
    def set_ncor():
        function = LegacyFunctionSpecification()
        function.addParameter('numb_of_stars_to_calc_c_parms', dtype='int32', direction=function.IN)
        function.result_type = 'int32'
        return function

    @legacy_function
    def set_istart():
        function = LegacyFunctionSpecification()
        function.addParameter('start_or_restart', dtype='int32', direction=function.IN)
        function.result_type = 'int32'
        return function

    @legacy_function
    def set_nt():
        function = LegacyFunctionSpecification()
        function.addParameter('tot_numb_of_objs', dtype='int32', direction=function.IN)
        function.result_type = 'int32'
        return function

    @legacy_function
    def set_irun():
        function = LegacyFunctionSpecification()
        function.addParameter('init_sequence_of_rnd_numbs', dtype='int32', direction=function.IN)
        function.result_type = 'int32'
        return function
        
    
    
class mmc(CodeInterface):

    def __init__(self):
        CodeInterface.__init__(self,  NearestNeighborInterface())
    
