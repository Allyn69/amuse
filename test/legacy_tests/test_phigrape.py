import unittest
import sys

from amuse.legacy.phiGRAPE import muse_dynamics_mpi as mpi_interface

from amuse.support.data import core
from amuse.support.units import nbody_system
from amuse.support.units import units

import numpy

from matplotlib import pyplot


class TestMPIInterface(unittest.TestCase):
    
    def test1(self):
        instance = mpi_interface.PhiGRAPE()
        instance.setup_module()
        instance.add_particle(1, 11.0, 2.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        retrieved_state = instance.get_state(1)
        self.assertEquals(11.0,  retrieved_state['mass'])
        self.assertEquals(instance.get_number(), 1)
        instance.cleanup_module()
        del instance
        
    def xtest2(self):
        instance = mpi_interface.PhiGRAPE()
        instance.eps2 = 0.101
        self.assertEquals(0.101, instance.eps2)
        instance.eps2 = 0.110
        self.assertEquals(0.110, instance.eps2)
        del instance
        
    
    def xtest4(self):
        instance = mpi_interface.PhiGRAPE()
        instance.setup_module()
        
        instance.add_particle( [1,2,3,4]
            , [11.0,12.0,13.0,14.0]
            , [2.0,3.0,4.0,5.0]
            , [2.1,3.1,4.1,5.1]
            , [2.2,3.2,4.2,5.2]
            , [2.3,3.3,4.3,5.3]
            , [2.4,3.4,4.4,5.4]
            , [2.5,3.5,4.5,5.5]
            , [2.6,3.6,4.6,5.6])
        retrieved_state = instance.get_state(1)
        print "result:", retrieved_state
        self.assertEquals(11.0,  retrieved_state['mass'])
        
        retrieved_state = instance.get_state([2,3,4])
        self.assertEquals(12.0,  retrieved_state['mass'][0])
        self.assertEquals(instance.get_number(), 4)
        instance.cleanup_module()
        
    
    def xtest5(self):
        instance = mpi_interface.PhiGRAPE()
        instance.setup_module()
        n = 4000
        ids = [i for i in range(1,n)]
        values = [1.0 * i for i in range(1,n)]
        instance.add_particle(ids
            , values
            , values
            , values
            , values
            , values
            , values
            , values
            , values)
        retrieved_state = instance.get_state(3999)
        print "result:", retrieved_state
        self.assertEquals(3999.0,  retrieved_state['mass'])
        instance.cleanup_module()
        
    def xtest6(self):
        instance = mpi_interface.PhiGRAPE()
        instance.setup_module()
        n = 4000
        ids = [i for i in range(1,n)]
        values = [1.0 * i for i in range(1,n)]
        for i in range(n-1):
            instance.add_particle(ids[i]
                , values[i]
                , values[i]
                , values[i]
                , values[i]
                , values[i]
                , values[i]
                , values[i]
                , values[i])
                
        retrieved_state = instance.get_state(1)
        print "result:", retrieved_state
        self.assertEquals(1.0,  retrieved_state['mass'])
        instance.cleanup_module()
        
        

class TestSunAndEarthSystem(unittest.TestCase):
    def test1(self):
        convert_nbody = nbody_system.nbody_to_si(units.MSun(1.0), units.km(149.5e6))

        instance = mpi_interface.PhiGRAPE(convert_nbody)
        instance.set_eta(0.01, 0.02)
        instance.setup_module()
        
        
        stars = core.Stars(2)
        sun = stars[0]
        sun.mass = units.MSun(1.0)
        sun.position = units.m(numpy.array((0.0,0.0,0.0)))
        sun.velocity = units.ms(numpy.array((0.0,0.0,0.0)))
        sun.radius = units.RSun(1.0)

        earth = stars[1]
        earth.mass = units.kg(5.9736e24)
        earth.radius = units.km(6371) 
        earth.position = units.km(numpy.array((149.5e6,0.0,0.0)))
        earth.velocity = units.ms(numpy.array((0.0,29800,0.0)))

        instance.add_particles(stars)
        instance.initialize_particles(0.0)
        
        postion_at_start = earth.position.value().in_(units.AU).number[0]
        
        instance.evolve_model(365.0 | units.day)
        instance.update_particles(stars)
        
        postion_after_full_rotation = earth.position.value().in_(units.AU) .number[0]
        
        self.assertAlmostEqual(postion_at_start, postion_after_full_rotation, 2)
        
        instance.evolve_model(365.0 + (365.0 / 2) | units.day)
        
        instance.update_particles(stars)
        postion_after_half_a_rotation = earth.position.value().in_(units.AU) .number[0]
        self.assertAlmostEqual(-postion_at_start, postion_after_half_a_rotation, 2)
        
        
        instance.evolve_model(365.0 + (365.0 / 2) + (365.0 / 4)  | units.day)
        
        instance.update_particles(stars)
        postion_after_half_a_rotation = earth.position.value().in_(units.AU) .number[1]
        self.assertAlmostEqual(-postion_at_start, postion_after_half_a_rotation, 3)
        instance.cleanup_module()
        del instance
        
        
    def test2(self):
        convert_nbody = nbody_system.nbody_to_si(units.MSun(1.0), units.km(149.5e6))

        instance = mpi_interface.PhiGRAPE(convert_nbody)
        instance.set_eta(0.01, 0.02)
        instance.setup_module()
        instance.dt_dia = 5000
        
        
        stars = core.Stars(2)
        sun = stars[0]
        sun.mass = units.MSun(1.0)
        sun.position = units.m(numpy.array((0.0,0.0,0.0)))
        sun.velocity = units.ms(numpy.array((0.0,0.0,0.0)))
        sun.radius = units.RSun(1.0)

        earth = stars[1]
        earth.mass = units.kg(5.9736e24)
        earth.radius = units.km(6371) 
        earth.position = units.km(numpy.array((149.5e6,0.0,0.0)))
        earth.velocity = units.ms(numpy.array((0.0,29800,0.0)))

        instance.add_particles(stars)
        instance.initialize_particles(0.0)
    
        for x in range(1,2000,10):
            instance.evolve_model(x  | units.day)
            instance.update_particles(stars)
        
        figure = pyplot.figure(figsize = (40,40))
        plot = figure.add_subplot(1,1,1)
        
        
        for index, (time,position) in enumerate(earth.position.values):
            x_point = position.in_(units.AU).number[0]
            y_point = position.in_(units.AU).number[1]
            color = 'b'
            plot.plot([x_point],[y_point], color + 'o')
        
        figure.savefig("phigrape-earth-sun.svg")    
        
        instance.cleanup_module()
        del instance


    
