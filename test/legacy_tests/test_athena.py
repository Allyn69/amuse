import os
import sys
import numpy

from amuse.test.amusetest import TestWithMPI
from amuse.legacy.athena.interface import AthenaInterface

from mpi4py import MPI

class TestAthenaInterface(TestWithMPI):
    
    def test0(self):
        instance=self.new_instance(AthenaInterface)
        instance.initialize_code()
        instance.stop()
        
    def test1(self):
        instance=self.new_instance(AthenaInterface)
        instance.initialize_code()
        instance.par_seti("test", "testname", "%d", 10, "a test parameter")
        x = instance.par_geti("test", "testname")
        
        self.assertEquals(x, 10)
        
        instance.stop()
        
    def test2(self):
        instance=self.new_instance(AthenaInterface, debugger="none")
        instance.initialize_code()
        instance.par_setd("test", "test2", "%.15e", 1.123, "a test parameter")
        x = instance.par_getd("test", "test2")
        
        self.assertEquals(x, 1.123)
        instance.stop()
        
        
    def test3(self):
        instance=self.new_instance(AthenaInterface, debugger="none")
        instance.initialize_code()
        instance.set_gamma(1.6666666666666667)
        instance.set_courant_friedrichs_lewy_number(0.8)
        instance.setup_mesh(128, 1, 1, 1.0, 0.0, 0.0)
        instance.set_boundary("periodic","periodic","periodic","periodic","periodic","periodic")
        
        x = instance.par_geti("grid", "Nx1")
        self.assertEquals(x, 128)
        
        result = instance.commit_parameters()
        self.assertEquals(result, 0)
        
        instance.stop()
        
    def test4(self):
        instance=self.new_instance(AthenaInterface)
        instance.initialize_code()
        instance.set_gamma(1.6666666666666667)
        instance.set_courant_friedrichs_lewy_number(0.8)
        instance.setup_mesh(10, 20, 40, 1.0, 1.0, 1.0)
        instance.set_boundary("periodic","periodic","periodic","periodic","periodic","periodic")
        
        x,y,z, error= instance.get_position_of_index(2,2,2)
        self.assertEquals(error, -1)
        
        result = instance.commit_parameters()
        self.assertEquals(result, 0)
        
        x,y,z, error= instance.get_position_of_index(0,0,0)
        self.assertEquals(error, 0)
        print x,y,z
        self.assertAlmostRelativeEquals(-0.35, x)  
        self.assertAlmostRelativeEquals(-0.175, y)
        self.assertAlmostRelativeEquals(-0.0875, z)
        
        
        x,y,z, error= instance.get_position_of_index(10,1,1)
        self.assertEquals(error, -1)
        instance.stop()
        
    
    def test5(self):
        instance=self.new_instance(AthenaInterface)
        instance.initialize_code()
        instance.setup_mesh(5, 5, 5, 1.0, 1.0, 1.0)
        instance.set_gamma(1.6666666666666667)
        instance.set_courant_friedrichs_lewy_number(0.8)
        instance.set_boundary("periodic","periodic","periodic","periodic","periodic","periodic")
        result = instance.commit_parameters()
        self.assertEquals(result, 0)
        
        error = instance.fill_grid_state(1,1,1, 0.1, 0.2, 0.3, 0.4, 0.5)
        self.assertEquals(error, 0)
        
        rho, rhovx, rhovy, rhovz, energy, error = instance.get_grid_state(1,1,1)
        
        self.assertEquals(error, 0)
        self.assertEquals(rho, 0.1)
        self.assertEquals(rhovx, 0.2)
        self.assertEquals(rhovy, 0.3)
        self.assertEquals(rhovz, 0.4)
        self.assertEquals(energy, 0.5)
        
        error = instance.initialize_grid()
        self.assertEquals(error, 0)
        
        timestep, error =  instance.get_timestep()
        self.assertEquals(error, 0)
        
        
        instance.stop()
        
    def test6(self):
        instance=self.new_instance(AthenaInterface)
        instance.initialize_code()
        instance.setup_mesh(5, 5, 5, 1.0, 1.0, 1.0)
        instance.set_gamma(1.6666666666666667)
        instance.set_courant_friedrichs_lewy_number(0.8)
        instance.set_boundary("periodic","periodic","periodic","periodic","periodic","periodic")
        result = instance.commit_parameters()
        self.assertEquals(result, 0)
        
        nghost, error = instance.get_nghost()
        self.assertEquals(4, nghost)
        instance.fill_grid_linearwave_1d(0, 1e-06, 0.0, 1)
        error = instance.initialize_grid()
        self.assertEquals(error, 0)
        
        timestep, error =  instance.get_timestep()
        self.assertEquals(error, 0)
        self.assertAlmostRelativeEqual(timestep, 0.159999, 5)
        
        instance.stop()
        
    def test7(self):
        results = []
        for x in range(1,4):
            instance=self.new_instance(AthenaInterface, number_of_workers=x, debugger="none")
            instance.initialize_code()
            instance.setup_mesh(128,1,1,1.0,0,0)
            instance.set_gamma(1.6666666666666667)
            instance.set_courant_friedrichs_lewy_number(0.8)
            instance.set_boundary("periodic","periodic","periodic","periodic","periodic","periodic")
            result = instance.commit_parameters()
            self.assertEquals(result, 0)
            
            nghost, error = instance.get_nghost()
            self.assertEquals(4, nghost)
            instance.fill_grid_linearwave_1d(0, 1e-06, 0.0, 1)
            error = instance.initialize_grid()
            self.assertEquals(error, 0)
            
            result = instance.get_grid_state_mpi(numpy.arange(0,128), numpy.zeros(128), numpy.zeros(128))
            results.append(list(result))
            
            
            instance.stop()
        
        for x in range(128):
            for y in range(6):
                self.assertEquals(results[1][y][x], results[0][y][x])
                self.assertEquals(results[2][y][x], results[0][y][x])
        
    
    def test8(self):
        instance=self.new_instance(AthenaInterface, number_of_workers=1)
        instance.initialize_code()
        instance.setup_mesh(128,1,1,1.0,0,0)
        instance.set_gamma(1.6666666666666667)
        instance.set_courant_friedrichs_lewy_number(0.8)
        instance.set_boundary("periodic","periodic","periodic","periodic","periodic","periodic")
        result = instance.commit_parameters()
        self.assertEquals(result, 0)
        
        instance.fill_grid_linearwave_1d(0, 1e-06, 0.0, 1)
        error = instance.initialize_grid()
        self.assertEquals(error, 0)
        
        timestep, error =  instance.get_timestep()
        self.assertEquals(error, 0)
        self.assertAlmostRelativeEqual(timestep,  0.006249991, 5)
        
        rho0, rhovx0, rhovy0, rhovz0, energy0, error0  = instance.get_grid_state_mpi(numpy.arange(0,128), numpy.zeros(128), numpy.zeros(128))
        instance.evolve(5.0)
        rho, rhovx, rhovy, rhovz, energy, error  = instance.get_grid_state_mpi(numpy.arange(0,128), numpy.zeros(128), numpy.zeros(128))
        
        error_rho = numpy.sum(numpy.abs(rho - rho0))
        error_rhovx =  numpy.sum(numpy.abs(rhovx - rhovx0))
        error_rhovy =  numpy.sum(numpy.abs(rhovy - rhovy0))
        error_rhovz =  numpy.sum(numpy.abs(rhovz - rhovz0))
        error_energy =  numpy.sum(numpy.abs(energy - energy0))
        self.assertAlmostRelativeEquals(error_rho / 128.0, 1.877334e-09, 6)
        self.assertAlmostRelativeEquals(error_rhovx / 128.0, 1.877334e-09, 6)
        self.assertAlmostRelativeEquals(error_energy / 128.0, 2.816001e-09, 6)
        
        instance.stop()
        
        
