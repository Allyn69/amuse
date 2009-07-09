import os.path
from mpi4py import MPI
import numpy

class Hermite(object):
    class dynamics_state(object):
        _attributes = ['mass','radius','x','y','z','vx','vy','vz']
        def __init__(self, id = 0, doubles = [0.0 for x in range(8)]):
            self.id = id
            print doubles
            for i, name in enumerate(self._attributes):
                setattr(self, name, doubles[i])
                
        def to_doubles(self):
            result = [0.0 for x in range(8)]
            for i, name in enumerate(self._attributes):
                result[i] = getattr(self, name)
            return result
                
                        
    def __init__(self):
        directory_of_this_module = os.path.dirname(__file__);
        full_name_of_the_worker = os.path.join(directory_of_this_module , 'muse_worker')
        print "name:", full_name_of_the_worker
        self.intercomm = MPI.COMM_SELF.Spawn(full_name_of_the_worker, None, 1)
    def __del__(self):
        print "deleting!"
        self.do_call(0)

    def do_call(self, tag, id=0, int_arg1=0, int_arg2=0, doubles_arg=[]):
        header = numpy.array([tag, id, int_arg1, int_arg2, len(doubles_arg)], dtype='i')
        self.intercomm.Send([header, MPI.INT], dest=0, tag=0)
        if doubles_arg:
            doubles = numpy.array(doubles_arg, dtype='d')
            self.intercomm.Send([doubles, MPI.DOUBLE], dest=0, tag=0)
        self.intercomm.Recv([header, MPI.INT], source=0, tag=999)
        id = header[1]
        int_result = header[2]
        n_doubles = header[4]
        if n_doubles > 0:
            doubles_result = numpy.empty(n_doubles,  dtype='d')
            self.intercomm.Recv([doubles_result, MPI.DOUBLE], source=0, tag=999)
        else:
            doubles_result = []
        return (id, int_result, doubles_result)
    def setup_module(self):
        id, int_result, double_result = self.do_call(1)
        return int_result
    def cleanup_module(self):
        id, int_result, double_result = self.do_call(2)
        return int_result
    def initialize_particles(self, time = 0.0):
        id, int_result, double_result = self.do_call(3, doubles_arg=[time])
        return int_result
    def evolve(self, time_end = 0.0, synchronize = 0):
        id, int_result, double_result = self.do_call(3, int_arg1 = synchronize, doubles_arg=[time_end])
        return int_result
    def reinitialize_particles(self):
        id, int_result, double_result = self.do_call(4, doubles_arg=[time])
        return int_result
    def add_particle(self, state):
        id, int_result, double_result = self.do_call(5, id=state.id, doubles_arg=state.to_doubles())
        return int_result
    def get_state(self,id):
        id_result, int_result, double_result = self.do_call(8, id=id)
        return self.dynamics_state(id_result, double_result)
        
    
  
