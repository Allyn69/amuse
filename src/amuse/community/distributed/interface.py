import threading
import sys
import logging
import socket


from amuse.community import *
from amuse.community.interface.common import CommonCodeInterface
from amuse.community.interface.common import CommonCode
from amuse.units import units
from amuse.support import options

from distributed_datamodel import Resources, Resource
from distributed_datamodel import Pilots, Pilot

logger = logging.getLogger(__name__)

class OutputHandler(threading.Thread):
    
    def __init__(self, stream, port):
        threading.Thread.__init__(self)
        self.stream = stream

        logging.getLogger("channel").debug("output handler connecting to distributed code")
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        address = ('localhost', port)
        
        try:
            self.socket.connect(address)
        except:
            raise exceptions.CodeException("Could not connect to distributed code at " + str(address))
        
        self.socket.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)
        
        self.socket.sendall('TYPE_OUTPUT'.encode('utf-8'))

        #fetch ID of this connection
        
        result = SocketMessage()
        result.receive(self.socket)
        
        self.id = result.strings[0]
        
        self.daemon = True
        self.start()
        
    def run(self):
        
        while True:
            logging.getLogger("channel").debug("receiving data for output")
            data = self.socket.recv(1024)
            
            if len(data) == 0:
                logging.getLogger("channel").debug("end of output", len(data))
                return
            
            logging.getLogger("channel").debug("got %d bytes", len(data))
            
            self.stream.write(data)

class DistributedAmuseInterface(CodeInterface, CommonCodeInterface, LiteratureReferencesMixIn):
    """
	Distributed Amuse Code
    
        .. [#] The Distributed Amuse project is a collaboration between Sterrewacht Leiden and The Netherlands eScience Center.
    """

    classpath = ['.', 'worker.jar', 'src/dist/*']
    
    def __init__(self, **keyword_arguments):
        CodeInterface.__init__(self, name_of_the_worker="distributed_worker_java", **keyword_arguments)
        LiteratureReferencesMixIn.__init__(self)



    @option(choices=['mpi','remote','distributed', 'sockets'], sections=("channel",))
    def channel_type(self):
        return 'sockets'
    
    @option(type="boolean", sections=("channel",))
    def initialize_mpi(self):
        """Is MPI initialized in the code or not. Defaults to True if MPI is available"""
        return False
    
    @legacy_function
    def get_worker_port():
        """
        Returns the server socket port of the code. Used by the distributed channel
        """
        function = LegacyFunctionSpecification()
        function.addParameter("worker_port", dtype='int32', direction=function.OUT)
        function.result_type = 'int32'
        return function
    
    @legacy_function
    def get_debug_enabled():
        """
	    Enable or disable debugging
        """
        function = LegacyFunctionSpecification()
        function.addParameter("debug_enabled", dtype='int32', direction=function.OUT)
        function.result_type = 'int32'
        return function
    
    @legacy_function
    def set_debug_enabled():
        """
        Enable or disable debugging
        """
        function = LegacyFunctionSpecification()
        function.addParameter("debug_enabled", dtype='int32', direction=function.IN)
        function.result_type = 'int32'
        return function

    @legacy_function
    def get_webinterface_port():
        """
        Returns the port the webinterface is running on
        """
        function = LegacyFunctionSpecification()
        function.addParameter("webinterface_port", dtype='int32', direction=function.OUT)
        function.result_type = 'int32'
        return function
    
    @legacy_function
    def set_webinterface_port():
        """
        Set the port the webinterface is running on
        """
        function = LegacyFunctionSpecification()
        function.addParameter("webinterface_port", dtype='int32', direction=function.IN)
        function.result_type = 'int32'
        return function
    
    @legacy_function
    def new_resource():
        """
        Define a new resource. This function returns an index that can be used to refer
        to this resource.
        """
        function = LegacyFunctionSpecification()
        function.must_handle_array = True
        function.addParameter('resource_id', dtype='int32', direction=function.OUT)
        function.addParameter("name", dtype='string', direction=function.IN)
        function.addParameter("location", dtype='string', direction=function.IN)
        function.addParameter("amuse_dir", dtype='string', direction=function.IN)
        function.addParameter("gateway", dtype='string', direction=function.IN, default=[""])
        function.addParameter("scheduler_type", dtype='string', direction=function.IN, default=["ssh"])
        function.addParameter('start_hub', dtype='int32', direction=function.IN, default=1)
        function.addParameter("boot_command", dtype='string', direction=function.IN, default = [""])
        function.addParameter('count', dtype='int32', direction=function.LENGTH)
        function.result_type = 'int32'
        return function
    
    @legacy_function
    def get_resource_state():
        """
        Get all the attributes of a resource.
        """
        function = LegacyFunctionSpecification()
        function.must_handle_array = True
        function.addParameter('resource_id', dtype='int32', direction=function.IN)
        function.addParameter("name", dtype='string', direction=function.OUT)
        function.addParameter("location", dtype='string', direction=function.OUT)
        function.addParameter("gateway", dtype='string', direction=function.OUT)
        function.addParameter("amuse_dir", dtype='string', direction=function.OUT)
        function.addParameter("scheduler_type", dtype='string', direction=function.OUT)
        function.addParameter('start_hub', dtype='int32', direction=function.OUT)
        function.addParameter("boot_command", dtype='string', direction=function.OUT)
        function.addParameter('count', dtype='int32', direction=function.LENGTH)
        function.result_type = 'int32'
        return function

    @legacy_function
    def delete_resource():
        """
        Remove the definition of resource from the code. After calling this function the resource is
        no longer part of the model evolution. It is up to the code if the index will be reused.
        This function is optional.
        """
        function = LegacyFunctionSpecification()
        function.must_handle_array = True
        function.addParameter('resource_id', dtype='int32', direction=function.IN,
            description = "Index of the resource to be removed. This index must have been returned by an earlier call to :meth:`new_resource`")

        function.addParameter('count', dtype='int32', direction=function.LENGTH)
        function.result_type = 'int32'
        function.result_doc = """
        0 - OK
            resource was removed from the model
        -1 - ERROR
            resource could not be removed
        -2 - ERROR
            not yet implemented
        """
        return function
    
    @legacy_function
    def new_pilot():
        """
        Reserve one or more nodes for later use by the simulation.
        """
        function = LegacyFunctionSpecification()
        function.must_handle_array = True
        function.addParameter('pilot_id', dtype='int32', direction=function.OUT)
        function.addParameter("resource_name", dtype='string', direction=function.IN)
        function.addParameter("queue_name", dtype='string', direction=function.IN, default=[""])
        function.addParameter("node_count", dtype='int32', direction=function.IN, default = 1)
        function.addParameter("time", dtype='int32', direction=function.IN, unit = units.minute, default = 60)
        function.addParameter("slots_per_node", dtype='int32', direction=function.IN, default = 1)
        function.addParameter("node_label", dtype='string', direction=function.IN, default = ["default"])
        function.addParameter("options", dtype='string', direction=function.IN, default = [""])
        function.addParameter('count', dtype='int32', direction=function.LENGTH)

        function.result_type = 'int32'
        return function
    
 

    @legacy_function
    def get_pilot_state():
        """
        Get all attributes of a pilot
        """
        function = LegacyFunctionSpecification()
        function.must_handle_array = True
        function.addParameter('pilot_id', dtype='int32', direction=function.IN)
        function.addParameter("resource_name", dtype='string', direction=function.OUT)
        function.addParameter("queue_name", dtype='string', direction=function.OUT)
        function.addParameter("node_count", dtype='int32', direction=function.OUT)
        function.addParameter("time", dtype='int32', direction=function.OUT, unit = units.minute)
        function.addParameter("slots_per_node", dtype='int32', direction=function.OUT)
        function.addParameter("node_label", dtype='string', direction=function.OUT)
        function.addParameter("options", dtype='string', direction=function.OUT)
        function.addParameter('status', dtype='string', direction=function.OUT)
        function.addParameter('count', dtype='int32', direction=function.LENGTH)

        function.result_type = 'int32'
        return function

    
    @legacy_function
    def get_pilot_status():
        function = LegacyFunctionSpecification()
        function.must_handle_array = True
        function.addParameter('pilot_id', dtype='int32', direction=function.IN)
        function.addParameter('status', dtype='string', direction=function.OUT)
        function.addParameter('count', dtype='int32', direction=function.LENGTH)
        function.result_type = 'int32'
        return function
    
    @legacy_function
    def delete_pilot():
        """
        Delete (stop) a pilot.
        """
        function = LegacyFunctionSpecification()
        function.must_handle_array = True
        function.addParameter('pilot_id', dtype='int32', direction=function.IN)
        function.addParameter('count', dtype='int32', direction=function.LENGTH)
        function.result_type = 'int32'
        return function
    
    @legacy_function
    def wait_for_pilots():
        """
        Wait until all pilots are started, and all nodes are available to run jobs and/or workers
        """
        function = LegacyFunctionSpecification()
        function.result_type = 'int32'
        return function
    
    @legacy_function
    def submit_script_job():
        """
        Submit a job, specified by a script
        """
        function = LegacyFunctionSpecification()
        function.must_handle_array = True
        function.addParameter('job_id', dtype='int32', direction=function.OUT)
        function.addParameter('script_name', dtype='string', direction=function.IN)
        function.addParameter('arguments', dtype='string', direction=function.IN)
        function.addParameter('script_dir', dtype='string', direction=function.IN)
        function.addParameter("node_label", dtype='string', direction=function.IN, default = ["default"])
        function.addParameter("re_use_code_files", dtype='int32', direction=function.IN, default = 0)
        function.addParameter('count', dtype='int32', direction=function.LENGTH)
        function.result_type = 'int32'
        return function
    
    @legacy_function
    def get_script_job_state():
        """
        Get all attributes of a script job
        """
        function = LegacyFunctionSpecification()
        function.must_handle_array = True
        function.addParameter('job_id', dtype='int32', direction=function.IN)
        function.addParameter('script_name', dtype='string', direction=function.OUT)
        function.addParameter('arguments', dtype='string', direction=function.OUT)
        function.addParameter('script_dir', dtype='string', direction=function.OUT)
        function.addParameter("node_label", dtype='string', direction=function.OUT)
        function.addParameter("re_use_code_files", dtype='int32', direction=function.OUT)
        function.addParameter("status", dtype='string', direction=function.OUT)
        function.addParameter('count', dtype='int32', direction=function.LENGTH)
        function.result_type = 'int32'
        return function
    
    @legacy_function
    def get_script_job_status():
        function = LegacyFunctionSpecification()
        function.must_handle_array = True
        function.addParameter('job_id', dtype='int32', direction=function.IN)
        function.addParameter('status', dtype='string', direction=function.OUT)
        function.addParameter('count', dtype='int32', direction=function.LENGTH)
        function.result_type = 'int32'
        return function
    
    @legacy_function
    def delete_script_job():
        """
        Delete (cancel) a script job
        """
        function = LegacyFunctionSpecification()
        function.must_handle_array = True
        function.addParameter('job_id', dtype='int32', direction=function.IN)
        function.addParameter('count', dtype='int32', direction=function.LENGTH)
        function.result_type = 'int32'
        return function
    
    @legacy_function
    def wait_for_script_jobs():
        """
        Wait until all script jobs are done.
        """
        function = LegacyFunctionSpecification()
        function.result_type = 'int32'
        return function

    @legacy_function
    def submit_function_job():
        """
        Submit a job, specified by a pickle of the function, and a pickle of the arguments.
        """
        function = LegacyFunctionSpecification()
        function.must_handle_array = True
        function.addParameter('job_id', dtype='int32', direction=function.OUT)
        function.addParameter('function', dtype='string', direction=function.IN)
        function.addParameter('arguments', dtype='string', direction=function.IN)
        function.addParameter("node_label", dtype='string', direction=function.IN, default = ["default"])
        function.addParameter('count', dtype='int32', direction=function.LENGTH)
        function.result_type = 'int32'
        return function
     
    @legacy_function
    def get_function_job_state():
        """
        Get all attributes of a pickled job
        """
        function = LegacyFunctionSpecification()
        function.must_handle_array = True
        function.addParameter('job_id', dtype='int32', direction=function.IN)
        function.addParameter("node_label", dtype='string', direction=function.OUT)
        function.addParameter("status", dtype='string', direction=function.OUT)
        function.addParameter('count', dtype='int32', direction=function.LENGTH)
        function.result_type = 'int32'
        return function
     
     
     
    @legacy_function
    def get_function_job_status():
        """
        Get all attributes of a pickled job
        """
        function = LegacyFunctionSpecification()
        function.must_handle_array = True
        function.addParameter('job_id', dtype='int32', direction=function.IN)
        function.addParameter("status", dtype='string', direction=function.OUT)
        function.addParameter('count', dtype='int32', direction=function.LENGTH)
        function.result_type = 'int32'
        return function
     
    @legacy_function
    def get_function_job_result():
        """
        Get a result of a picked function job. Will block until the result is available
        """
        function = LegacyFunctionSpecification()
        function.must_handle_array = True
        function.addParameter('job_id', dtype='int32', direction=function.IN)
        function.addParameter('result', dtype='string', direction=function.OUT)
        function.addParameter('count', dtype='int32', direction=function.LENGTH)
        function.result_type = 'int32'
        return function
     
    @legacy_function
    def delete_function_job():
        """
        Delete (cancel) a script job
        """
        function = LegacyFunctionSpecification()
        function.must_handle_array = True
        function.addParameter('job_id', dtype='int32', direction=function.IN)
        function.addParameter('count', dtype='int32', direction=function.LENGTH)
        function.result_type = 'int32'
        return function
     
    @legacy_function
    def get_worker_state():
        """
        Get all attributes of a pickled job
        """
        function = LegacyFunctionSpecification()
        function.must_handle_array = True
        function.addParameter('worker_id', dtype='int32', direction=function.IN)

        function.addParameter('executable', dtype='string', direction=function.OUT)
        function.addParameter("node_label", dtype='string', direction=function.OUT)
        function.addParameter("worker_count", dtype='int32', direction=function.OUT)
        function.addParameter("thread_count", dtype='int32', direction=function.OUT)
        function.addParameter("status", dtype='string', direction=function.OUT)
        
        function.addParameter('count', dtype='int32', direction=function.LENGTH)
        
        function.result_type = 'int32'
        return function
    
    @legacy_function
    def get_worker_status():
        """
        Get all attributes of a worker
        """
        function = LegacyFunctionSpecification()
        function.must_handle_array = True
        function.addParameter('worker_id', dtype='int32', direction=function.IN)
        function.addParameter("status", dtype='string', direction=function.OUT)
        function.addParameter('count', dtype='int32', direction=function.LENGTH)
        function.result_type = 'int32'
        return function
    
    @legacy_function
    def get_number_of_workers():
        function = LegacyFunctionSpecification()
        function.addParameter('number_of_workers', dtype='int32', direction=function.OUT)
        function.result_type = 'int32'
        return function
    
    @legacy_function
    def get_worker_ids():
        function = LegacyFunctionSpecification()
        function.must_handle_array = True
        function.addParameter('index', dtype='int32', direction=function.IN) # probably unused, but required to get 'count'
        function.addParameter('id_of_the_worker', dtype='int32', direction=function.OUT)
        function.addParameter('count', dtype='int32', direction=function.LENGTH)
        function.result_type = 'int32'
        return function
    
    @legacy_function
    def get_current_error():
        """When a function returns an error, this will retrieve
        a description (if possible)
        """
        function = LegacyFunctionSpecification()  
        function.addParameter('string', 
            dtype='string',
            direction=function.OUT,
            description = "description of the error"
        )
        function.result_type = 'int32'
        return function
    
    @legacy_function
    def end_all():
        """
        Stop all jobs, resources and pilots
        """
        function = LegacyFunctionSpecification()
        function.result_type = 'int32'
        return function
    
    def cleanup_code(self):
        del options.GlobalOptions.instance().overriden_options["channel_type"]
        self.end_all()
        return 0
    
    def new_worker(self):
        raise exceptions.AmuseException("Can't add to 'workers' directly. Create community code instances in the usual way instead.")
    
    def delete_worker(self):
        raise exceptions.AmuseException("Can't remove from 'workers' directly. Stop community code instances in the usual way instead.")

class DistributedAmuse(CommonCode):

    def __init__(self, **options):
        CommonCode.__init__(self,  DistributedAmuseInterface(**options), **options)
    
    def submit_function_job(self, function, *args, **kwargs):
        # pickle the input function
        return self.overridden().submit_function_job(*args, **kwargs)
    
    def get_function_job_result(self, function, *args, **kwargs):
        result = self.overridden().get_function_job_result(*args, **kwargs)
        #un-pickle
        return result
    
    def get_webinterface_url(self):
        return "http://localhost:" + str(self.parameters.webinterface_port)
    
    def commit_parameters(self):
        self.parameters.send_not_set_parameters_to_code()
        self.parameters.send_cached_parameters_to_code()
        self.overridden().commit_parameters()
        
        port = self.get_worker_port()
        
        #logging.basicConfig(level=logging.DEBUG)
        
        logger.debug("running on port %d", port)

#        self.stdoutHandler = OutputHandler(sys.stdout, port)
#        self.stderrHandler = OutputHandler(sys.stderr, port)

        options.GlobalOptions.instance().override_value_for_option("channel_type", "distributed")
        options.GlobalOptions.instance().override_value_for_option("port", port)
        
    def define_state(self, object): 
        CommonCode.define_state(self, object)   
        object.add_transition('INITIALIZED','RUN','commit_parameters')
        object.add_transition('RUN','CHANGE_PARAMETERS_RUN','before_set_parameter', False)
        object.add_transition('CHANGE_PARAMETERS_RUN','RUN','recommit_parameters')
        
        object.add_method('CHANGE_PARAMETERS_RUN', 'before_set_parameter')
        object.add_method('CHANGE_PARAMETERS_RUN', 'before_get_parameter')
        object.add_method('RUN', 'before_get_parameter')
        
        
        object.add_method('RUN', 'new_resource')
        object.add_method('RUN', 'new_pilot')
        object.add_method('RUN', 'get_resource_state')
        object.add_method('RUN', 'get_pilot_state')
        object.add_method('RUN', 'get_pilot_status')
        object.add_method('RUN', 'get_script_job_state')
        object.add_method('RUN', 'get_script_job_status')
        object.add_method('RUN', 'get_function_job_state')
        object.add_method('RUN', 'get_function_job_status')
        object.add_method('RUN', 'get_worker_state')
        object.add_method('RUN', 'get_worker_status')
    
    def define_parameters(self, object):
              
        object.add_boolean_parameter(
            "get_debug_enabled",
            "set_debug_enabled",
            "debug_enabled", 
            "If enabled, will output additional debugging information and logs", 
            default_value = False
        )
        
        object.add_method_parameter(
            "get_worker_port",
            None,
            "worker_port", 
            "Port that the distributed code uses to handle new worker requests on from the distributed channel", 
            default_value = 0
        )
        
        object.add_method_parameter(
            "get_webinterface_port",
            "set_webinterface_port",
            "webinterface_port", 
            "Port for monitoring webinterface", 
            default_value = 0
        )

    
    def define_particle_sets(self, object):
        object.define_super_set('items', ['resources', 'pilots', 'script_jobs', 'function_jobs', '_workers'])
        
        #resources
        object.define_set('resources', 'resource_id')
        object.set_new('resources', 'new_resource')
        object.set_delete('resources', 'delete_resource')
        object.add_getter('resources', 'get_resource_state')
        object.mapping_from_name_to_set_definition['resources'].particles_factory = Resources
        
        #pilots
        object.define_set('pilots', 'pilot_id')
        object.set_new('pilots', 'new_pilot')
        object.set_delete('pilots', 'delete_pilot')
        object.add_getter('pilots', 'get_pilot_state')
        object.add_getter('pilots', 'get_pilot_status', names = ('status',))
        object.mapping_from_name_to_set_definition['pilots'].particles_factory = Pilots
        
        #script jobs
        object.define_set('script_jobs', 'job_id')
        object.set_new('script_jobs', 'submit_script_job')
        object.set_delete('script_jobs', 'delete_script_job')
        object.add_getter('script_jobs', 'get_script_job_state')
        object.add_getter('script_jobs', 'get_script_job_status', names = ('status',))
        
        #function jobs
        object.define_set('function_jobs', 'job_id')
        object.set_new('function_jobs', 'submit_function_job')
        object.set_delete('function_jobs', 'delete_function_job')
        object.add_getter('function_jobs', 'get_function_job_state')
        object.add_getter('function_jobs', 'get_function_job_status')
        
        #workers
        object.define_set('_workers', 'worker_id')
        object.set_new('_workers', 'new_worker')
        object.set_delete('_workers', 'delete_worker')
        object.add_getter('_workers', 'get_worker_state')
        object.add_getter('_workers', 'get_worker_status', names = ('status',))
        
    @property
    def workers(self):
        self.update_workers_particle_set()
        return self._workers
    
    def update_workers_particle_set(self):
        """
        Update the "workers" particle set after new instances of codes have been
        created or previously created instances have been stopped.
        """
        old_ids = set(self._workers.get_all_indices_in_store())
        number_of_workers = self.get_number_of_workers()
        if not number_of_workers == 0:
            new_ids = set(self.get_worker_ids(range(number_of_workers)))
        
        ids_to_remove = old_ids - new_ids
        ids_to_add = new_ids - old_ids
        if not len(ids_to_remove) == 0:
            self._workers._remove_indices_in_attribute_storage(list(ids_to_remove))
        if not len(ids_to_add) == 0:
            self._workers._add_indices_in_attribute_storage(list(ids_to_add))
    
