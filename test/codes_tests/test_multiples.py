# nosetests --nocapture --nologcapture -w test/codes_tests --tests=test_multiples 

from amuse.test.amusetest import TestWithMPI

import os
import sys
import numpy
import time
import math

from amuse.community.hermite0.interface import Hermite
from amuse.community.kepler.interface import Kepler
from amuse.community.smalln.interface import SmallN

from amuse.units import nbody_system
from amuse.units import units
from amuse.units import constants

from amuse import datamodel
from amuse.ic import plummer
from amuse.couple import multiples
from amuse.couple import encounters

class TestSimpleMultiples(TestWithMPI):
    previous = None
    
    def new_smalln(self):
        if not self.previous is None:
            self.previous.stop()
            
        result = SmallN()
        result.parameters.timestep_parameter = 0.1
        result.parameters.cm_index = 2001
        self.previous = result
        return result
        
    def new_kepler_si(self):
        unit_converter = nbody_system.nbody_to_si(
            1 | units.MSun,
            1 | units.AU
        )
        kepler = Kepler(unit_converter)
        kepler.initialize_code()
        return kepler
        
    def new_kepler(self):
        kepler = Kepler()
        kepler.initialize_code()
        return kepler
        
    def new_smalln_si(self):
    
        if not self.previous is None:
            self.previous.stop()
        converter = nbody_system.nbody_to_si(units.MSun, units.parsec)
        result = SmallN(converter)
        result.parameters.timestep_parameter = 0.1
        result.parameters.cm_index = 2001
        return result
        
    def new_binary(self, mass1, mass2, semi_major_axis,
                   eccentricity = 0, keyoffset = -1):
        total_mass = mass1 + mass2
        mass_fraction_particle_1 = mass1 / (total_mass)
    
        if keyoffset >= 0:
            binary = datamodel.Particles(keys=range(keyoffset, keyoffset+2))
        else:
            binary = datamodel.Particles()
            
        binary[0].mass = mass1
        binary[1].mass = mass2
    
        mu = nbody_system.G * total_mass
    
        velocity_perihelion = numpy.sqrt( mu / semi_major_axis  * ((1.0 + eccentricity)/(1.0 - eccentricity)))
        radius_perihelion = semi_major_axis * (1.0 - eccentricity)
        
        binary[0].position = ((1.0 - mass_fraction_particle_1) * radius_perihelion * [1.0,0.0,0.0])
        binary[1].position = -(mass_fraction_particle_1 * radius_perihelion * [1.0,0.0,0.0])
    
        binary[0].velocity = ((1.0 - mass_fraction_particle_1) * velocity_perihelion * [0.0,1.0,0.0])
        binary[1].velocity = -(mass_fraction_particle_1 * velocity_perihelion * [0.0,1.0,0.0])

        return binary
        
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
        
        encounter_code = encounters.HandleEncounter(
            kepler_code =  self.new_kepler(),
            resolve_collision_code = self.new_smalln(),
            interaction_over_code = None
        )
        multiples_code = encounters.Multiples(
            gravity_code = code,
            handle_encounter_code = encounter_code
        )
        multiples_code.particles.add_particles(stars)
        multiples_code.commit_particles()
        multiples_code.evolve_model(0.6|nbody_system.time)
        self.assertEquals(len(multiples_code.multiples), 1)
        self.assertEquals(len(multiples_code.binaries), 1)
        
        
    def test1(self):
        code = Hermite()
        stars = datamodel.Particles(keys = (1,2,3, 4))
        stars.mass = 1 | nbody_system.mass
        stars.position = [
            [0,0,0],
            [0.5, 0, 0],
            [2, 0, 0],
            [-10, 0, 0],
        ]|nbody_system.length
        stars.velocity = [
            [0,0,0],
            [0,0.1, 0],
            [0,-0.1, 0],
            [0,0.2, 0],
        ]|nbody_system.speed
        stars.radius = 0.5 | nbody_system.length
        
        encounter_code = encounters.HandleEncounter(
            kepler_code =  self.new_kepler(),
            resolve_collision_code = self.new_smalln(),
            interaction_over_code = None
        )
        multiples_code = encounters.Multiples(
            gravity_code = code,
            handle_encounter_code = encounter_code
        )
        multiples_code.particles.add_particles(stars)
        multiples_code.commit_particles()
        
        multiples_code.evolve_model(0.6|nbody_system.time)
        self.assertEquals(len(multiples_code.multiples), 1)
        self.assertEquals(len(multiples_code.binaries), 1)
        multiples_code.evolve_model(2|nbody_system.time)
        self.assertEquals(len(multiples_code.multiples), 1)
        self.assertEquals(len(multiples_code.binaries), 1)
        multiples_code.evolve_model(3|nbody_system.time)
        self.assertEquals(len(multiples_code.multiples), 1)
        self.assertEquals(len(multiples_code.particles), 2)
        print multiples_code.binaries
        self.assertEquals(len(multiples_code.binaries), 1)
        

    def test2(self):
        code = Hermite()
        stars = datamodel.Particles(keys = (1,2,3, 4))
        stars.mass = 1 | nbody_system.mass
        stars.position = [
            [0,0,0],
            [0.5, 0, 0],
            [2, 0, 0],
            [-10, 0, 0],
        ]|nbody_system.length
        stars.velocity = [
            [0,0,0],
            [0,0.1, 0],
            [0,-0.1, 0],
            [0,0.2, 0],
        ]|nbody_system.speed
        stars.radius = 0.5 | nbody_system.length
        
        encounter_code = encounters.HandleEncounter(
            kepler_code =  self.new_kepler(),
            resolve_collision_code = self.new_smalln(),
            interaction_over_code = None
        )
        multiples_code = encounters.Multiples(
            gravity_code = code,
            handle_encounter_code = encounter_code
        )
        multiples_code.particles.add_particles(stars)
        multiples_code.commit_particles()
        
        multiples_code.evolve_model(3|nbody_system.time)
        self.assertEquals(len(multiples_code.multiples), 1)
        self.assertEquals(len(multiples_code.particles), 2)
        self.assertEquals(len(multiples_code.binaries), 1)
    
    
    def test3(self):
        code = Hermite()
        particles_in_binary = self.new_binary(
            0.1 | nbody_system.mass,
            0.1 | nbody_system.mass,
            0.01 | nbody_system.length,
            keyoffset = 1
        )
        particles_in_binary.radius = 0.001 | nbody_system.length
        binary = datamodel.Particle(key = 3)
        binary.child1 = particles_in_binary[0]
        binary.child2 = particles_in_binary[1]
        binary.radius = 0.5 | nbody_system.length
        binary.mass = 0.2 | nbody_system.mass
        encounter_code = encounters.HandleEncounter(
            kepler_code =  self.new_kepler(),
            resolve_collision_code = self.new_smalln(),
            interaction_over_code = None
        )
        multiples_code = encounters.Multiples(
            gravity_code = code,
            handle_encounter_code = encounter_code
        )
        multiples_code.singles.add_particles(particles_in_binary)
        multiples_code.binaries.add_particle(binary)
        
        self.assertEquals(len(multiples_code.singles), 2)
        self.assertEquals(id(multiples_code.binaries[0].child1.particles_set), id(multiples_code.singles))
        
        multiples_code.commit_particles()
        
        self.assertEquals(len(multiples_code.multiples), 1)
        
    def xtest2(self):
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
        
        multiples_code = multiples.Multiples(code, self.new_smalln_si, self.new_kepler_si(), gravity_constant = constants.G)
        multiples_code.binary_breakup_factor = 1
        
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
        print "ERROR:", error
        self.assertTrue(error < 1e-4)
        #self.assertAlmostRelativeEquals(multiples_code.multiples_energy_correction - multiples_code.kinetic_energy, -total_energy0, 7)

    def xtest3(self):
        code = Hermite()
        stars = datamodel.Particles()
        binary1 = self.new_binary(
            1.0 | nbody_system.mass,
            0.4 | nbody_system.mass,
            0.01 |  nbody_system.length,
            keyoffset = 1
        )
        binary2 = self.new_binary(
            0.5 | nbody_system.mass,
            0.2 | nbody_system.mass,
            0.005 |  nbody_system.length,
            keyoffset = 3
        )
        binary2.position += [0.5,0,0] | nbody_system.length
        binary2.velocity += [0,0,0.03] | nbody_system.speed
        stars.add_particles(binary1)
        stars.add_particles(binary2)
        stars.radius = 0.005 | nbody_system.length
        print stars
        code.particles.add_particles(stars)

        multiples_code = multiples.Multiples(code, self.new_smalln, self.new_kepler())
        multiples_code.binary_breakup_factor = 1
        
       
        total_energy0 = multiples_code.kinetic_energy + multiples_code.potential_energy - multiples_code.multiples_energy_correction
        multiples_code.evolve_model(0.1|nbody_system.time)
        multiples_code.print_multiples()
        total_energy1 =  multiples_code.kinetic_energy + multiples_code.potential_energy - multiples_code.multiples_energy_correction

        error = abs((total_energy1 - total_energy0)/total_energy0)
        
        self.assertTrue(error < 1e-7)
        multiples_code.evolve_model(0.2|nbody_system.time)
        multiples_code.print_multiples()
        total_energy2 =  multiples_code.kinetic_energy + multiples_code.potential_energy - multiples_code.multiples_energy_correction

        error = abs((total_energy2 - total_energy0)/total_energy0)
        
        self.assertTrue(error < 1e-5)
        
        stars = multiples_code.stars
        self.assertEquals(len(stars), 4)
        self.assertEquals(len(code.particles), 2)
    

    def xtest4(self):
        code = Hermite()
        stars = datamodel.Particles()
        binary1 = self.new_binary(
            1.0 | nbody_system.mass,
            1.0 | nbody_system.mass,
            0.1 | nbody_system.length,
            keyoffset = 1
        )
        binary2 = self.new_binary(
            1.0 | nbody_system.mass,
            1.0 | nbody_system.mass,
            0.2 | nbody_system.length,
            keyoffset = 3
        )
        binary1.position += [1.0,0.0,0] | nbody_system.length
        binary2.position -= [1.0,0.0,0] | nbody_system.length
        stars.add_particles(binary1)
        stars.add_particles(binary2)
        stars.radius = 0.25 | nbody_system.length
        
        code.particles.add_particles(stars)

        multiples_code = multiples.Multiples(code, self.new_smalln, self.new_kepler())
        multiples_code.binary_breakup_factor = 1
        total_energy0 = (
            multiples_code.kinetic_energy 
            + multiples_code.potential_energy 
            - multiples_code.multiples_energy_correction
        )
        multiples_code.evolve_model(0.1|nbody_system.time)
        multiples_code.print_multiples()
        total_energy1 =  (
            multiples_code.kinetic_energy
            + multiples_code.potential_energy
            - multiples_code.multiples_energy_correction
        )

        error = abs((total_energy1 - total_energy0)/total_energy0)
        
        self.assertTrue(error < 1e-7)
        multiples_code.evolve_model(2.0|nbody_system.time)
        multiples_code.print_multiples()
        total_energy2 =(
            multiples_code.kinetic_energy
            + multiples_code.potential_energy 
            - multiples_code.multiples_energy_correction
        )

        error = abs((total_energy2 - total_energy0)/total_energy0)
        
        self.assertTrue(error < 1e-5)
        
    def xtest5(self):
        code1 = Hermite()
        stars = datamodel.Particles()
        binary1 = self.new_binary(
            1.0 | nbody_system.mass,
            0.2 | nbody_system.mass,
            0.01 |  nbody_system.length,
            eccentricity = 0.7,
            keyoffset = 1
        )
        binary2 = self.new_binary(
            0.8 | nbody_system.mass,
            0.3 | nbody_system.mass,
            0.01 |  nbody_system.length,
            eccentricity = 0.9,
            keyoffset = 3
        )
        binary1.position += [-0.5,-0.5,-0.5] | nbody_system.length
        binary1.velocity += [0.0,0.0,0.0] | nbody_system.speed
        binary2.position += [0.5,0.5,0.5] | nbody_system.length
        binary2.velocity += [0.0,0.0,0.0] | nbody_system.speed
        stars.add_particles(binary1)
        stars.add_particles(binary2)
        stars.radius = 0.2 | nbody_system.length
        code1.particles.add_particles(stars)
        kepler1 = self.new_kepler()
        print binary2.velocity, (binary2[0].velocity - binary2[1].velocity).length
        multiples_code1 = multiples.Multiples(code1, self.new_smalln, kepler1)
        multiples_code1.binary_breakup_factor = 1
        multiples_code1.evolve_model(0.1|nbody_system.time)
        multiples_code1.print_multiples()
        stars = multiples_code1.stars
        self.assertEquals(len(stars), 4)
        code2 = Hermite()
        code2.particles.add_particles(stars)
        kepler2 = self.new_kepler()
        multiples_code2 = multiples.Multiples(code2, self.new_smalln, kepler2)
        multiples_code2.binary_breakup_factor = 1
        multiples_code1.evolve_model(0.2|nbody_system.time)
        multiples_code2.evolve_model(0.1|nbody_system.time)
        multiples_code1.print_multiples()
        multiples_code2.print_multiples()
        # compare the root positions
        p01 = multiples_code1._inmemory_particles[0]
        p02 = p01.as_particle_in_set(multiples_code2._inmemory_particles)
        self.assertAlmostRelativeEquals(p01.position, p01.position)
        p11 = multiples_code1._inmemory_particles[1]
        p12 = p11.as_particle_in_set(multiples_code2._inmemory_particles)
        self.assertAlmostRelativeEquals(p11.position, p11.position)
        
        if p01.mass == 1.2 | nbody_system.mass:
            b1 = p01
            b2 = p11
        else:
            b1 = p11
            b2 = p01
        b1stars = binary1.get_intersecting_subset_in(multiples_code1.stars)
        self.assertAlmostRelativeEquals(
            b1stars.center_of_mass(),
            b1.position,
        )
        b2stars = binary2.get_intersecting_subset_in(multiples_code1.stars)
        self.assertAlmostRelativeEquals(
            b2stars.center_of_mass(),
            b2.position,
        )
        
             
    def xtest6(self):
        code = Hermite()
        stars = datamodel.Particles(2)
        
        stars.mass = 2 | nbody_system.mass
        
        stars.position = [
            [0, 0, 0],
            [1, 1, 0]
        ]|nbody_system.length
        
        stars.velocity = [
            [1, 0,0],
            [-1, 0, 0]
        ]|nbody_system.speed
        
        stars.radius = 0.5 | nbody_system.length
        
        code.particles.add_particles(stars)
        
        multiples_code = multiples.Multiples(code, self.new_smalln, self.new_kepler())
        multiples_code.evolve_model(0.6|nbody_system.time)
        print multiples_code.particles
        
        self.assertEquals(len(multiples_code.particles), 2)

    def xtest7(self):
        code = Hermite()
        stars = datamodel.Particles(3)
        
        stars.mass = 2 | nbody_system.mass
        stars.position = [
            [0, 0, 0],
            [1, 1, 0],
            [2, 2, 0],
        ]|nbody_system.length
        
        stars.velocity = [
            [1, 0,0],
            [-1, 0, 0],
            [-2,-2, 0],
        ]|nbody_system.speed
        
        stars.radius = 0.5 | nbody_system.length
        
        code.particles.add_particles(stars)
        
        multiples_code = multiples.Multiples(code, self.new_smalln, self.new_kepler())
        multiples_code.evolve_model(0.6|nbody_system.time)
        print multiples_code.particles
        
        self.assertEquals(len(multiples_code.particles), 3)
