from amuse.test.amusetest import TestWithMPI

import os
import sys
import numpy
import time
import math

from amuse.community.hermite0.interface import Hermite
from amuse.community.newsmallN.interface import SmallN

from amuse.units import nbody_system
from amuse.units import units
from amuse.units import constants

from amuse import datamodel
from amuse.ic import plummer
from amuse.couple import multiples



class TestSimpleMultiples(TestWithMPI):

    def new_smalln(self):
        result = SmallN()
        result.parameters.timestep_parameter = 0.1
        result.parameters.cm_index = 2001
        return result
        
    def new_smalln_si(self):
    
        converter = nbody_system.nbody_to_si(units.MSun, units.parsec)
        result = SmallN(converter)
        result.parameters.timestep_parameter = 0.1
        result.parameters.cm_index = 2001
        return result
        
   
        
    def test0(self):
        code = Hermite()
        stars = datamodel.Particles(2)
        stars.mass = 1 | nbody_system.mass
        stars.position = [
            [0,0,0],
            [1.2, 0, 0]
        ]|nbody_system.length
        stars.velocity = [
            [0,0,0],
            [0,0.1, 0]
        ]|nbody_system.speed
        stars.radius = 0.5 | nbody_system.length
        code.particles.add_particles(stars)
        
        multiples_code = multiples.Multiples(code, self.new_smalln)
        print multiples_code.multiples_energy_correction
        total_energy0 = multiples_code.kinetic_energy + multiples_code.potential_energy - multiples_code.multiples_energy_correction
        print total_energy0
        multiples_code.evolve_model(0.6|nbody_system.time)
        total_energy1 =  multiples_code.kinetic_energy + multiples_code.potential_energy - multiples_code.multiples_energy_correction
        print total_energy1
        print 
        print total_energy0
        error = abs((total_energy1 - total_energy0)/total_energy0)
        print multiples_code.multiples_energy_correction
        
        self.assertTrue(error < 1e-7)
        self.assertAlmostRelativeEquals(multiples_code.multiples_energy_correction - multiples_code.kinetic_energy, -total_energy0, 7)
    
    def test1(self):
        code = Hermite()
        stars = datamodel.Particles(3)
        stars.mass = 1 | nbody_system.mass
        stars.position = [
            [0,0,0],
            [1.2, 0, 0],
            [-10, 0, 0],
        ]|nbody_system.length
        stars.velocity = [
            [0,0,0],
            [0,0.1, 0],
            [0,0, 0],
        ]|nbody_system.speed
        stars.radius = 0.5 | nbody_system.length
        code.particles.add_particles(stars)
        
        converter = nbody_system.nbody_to_si(units.MSun, units.parsec)
        print converter.to_si(stars.velocity)
        print converter.to_si(0.6|nbody_system.time).as_quantity_in(units.Myr)
        
        multiples_code = multiples.Multiples(code, self.new_smalln)
        print multiples_code.multiples_energy_correction
        total_energy0 = multiples_code.kinetic_energy + multiples_code.potential_energy - multiples_code.multiples_energy_correction
        print total_energy0
        multiples_code.evolve_model(0.6|nbody_system.time)
        total_energy1 =  multiples_code.kinetic_energy + multiples_code.potential_energy - multiples_code.multiples_energy_correction
        print total_energy1
        print multiples_code.multiples_energy_correction
        error = abs((total_energy1 - total_energy0)/total_energy0)
        print "error:", error
        self.assertTrue(error < 1e-7)
        
    def test2(self):
        converter = nbody_system.nbody_to_si(units.MSun, units.parsec)
        
        code = Hermite(converter)
        stars = datamodel.Particles(2)
        stars.mass = converter.to_si(1 | nbody_system.mass)
        stars.position = converter.to_si([
            [0,0,0],
            [1.2, 0, 0]
        ]|nbody_system.length)
        stars.velocity = converter.to_si([
            [0,0,0],
            [0,0.1, 0]
        ]|nbody_system.speed)
        stars.radius = converter.to_si(0.5 | nbody_system.length)
        code.particles.add_particles(stars)
        
        multiples_code = multiples.Multiples(code, self.new_smalln_si, gravity_constant = constants.G)
        print multiples_code.multiples_energy_correction
        total_energy0 = multiples_code.kinetic_energy + multiples_code.potential_energy - multiples_code.multiples_energy_correction
        print total_energy0
        multiples_code.evolve_model(converter.to_si(0.6|nbody_system.time))
        total_energy1 =  multiples_code.kinetic_energy + multiples_code.potential_energy - multiples_code.multiples_energy_correction
        print total_energy1
        print total_energy0
        
        print converter.to_nbody(total_energy1)
        print converter.to_nbody(total_energy0)
        error = abs((total_energy1 - total_energy0)/total_energy0)
        print multiples_code.multiples_energy_correction
        print converter.to_nbody(multiples_code.multiples_energy_correction)
        self.assertTrue(error < 1e-7)
        self.assertAlmostRelativeEquals(multiples_code.multiples_energy_correction - multiples_code.kinetic_energy, -total_energy0, 7)
    
