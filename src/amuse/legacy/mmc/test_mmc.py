from amuse.legacy import *
from amuse.test.amusetest import TestWithMPI

from .interface import mmcInterface
from .interface import mmc

class mmcInterfaceTests(TestWithMPI):
    
    def xtest1(self):
        instance = mmcInterface(redirection="file", redirect_file = "junk.txt")
        instance.nonstandard_init()
        while (1):
            print instance.get_time()
            print instance.get_kinetic_energy()
            res, err =  instance.initial_run()
            print res
            if (res<0): break
            #break
            
        instance.stop()
    
