import numpy
import os.path

from amuse.test.amusetest import TestWithMPI
from amuse.units import nbody_system, units, constants
from amuse.datamodel import Particles
from amuse.community.pikachu.interface import PikachuInterface, Pikachu

from amuse.ic.plummer import new_plummer_model


default_options = dict(mode='normal')
#~default_options = dict(redirection="none", mode='normal')
#~default_options = dict(debugger="gdb", mode='normal')
#~default_options = dict(redirection="none", mode='large_n')

class TestPikachuInterface(TestWithMPI):
    
    def test1(self):
        print "Test PikachuInterface initialization"
        instance = self.new_instance_of_an_optional_code(PikachuInterface, **default_options)
        self.assertEquals(0, instance.initialize_code())
        
        directory, error = instance.get_kernel_directory()
        self.assertEquals(0, error)
        self.assertEquals("./", directory)
        self.assertEquals(0, instance.set_kernel_directory(instance.default_kernel_directory))
        directory, error = instance.get_kernel_directory()
        self.assertEquals(error, 0)
        self.assertEquals(directory, os.path.join(instance.amuse_root_directory, "src", "amuse", "community", "pikachu"))
        
        self.assertEquals(0, instance.commit_parameters())
        self.assertEquals(0, instance.cleanup_code())
        instance.stop()
    
    def test2(self):
        print "Test PikachuInterface new_particle / get_state"
        instance = self.new_instance_of_an_optional_code(PikachuInterface, **default_options)
        self.assertEquals(0, instance.initialize_code())
        self.assertEquals(0, instance.set_kernel_directory(instance.default_kernel_directory))
        self.assertEquals(0, instance.commit_parameters())
        
        id, error = instance.new_particle(mass = 11.0, x = 0.0, y = 0.0, z = 0.0, vx = 0.0, vy = 0.0, vz = 0.0, radius = 1.0)
        self.assertEquals(0, error)
        self.assertEquals(1, id)
        id, error = instance.new_particle(mass = 21.0, x = 10.0, y = 0.0, z = 0.0, vx = 10.0, vy = 0.0, vz = 0.0, radius = 2.0)
        self.assertEquals(0, error)
        self.assertEquals(2, id)
        self.assertEquals(0, instance.commit_particles())
        retrieved_state1 = instance.get_state(1)
        retrieved_state2 = instance.get_state(2)
        self.assertEquals(0,  retrieved_state1['__result'])
        self.assertEquals(0,  retrieved_state2['__result'])
        self.assertEquals(11.0,  retrieved_state1['mass'])
        self.assertEquals(21.0,  retrieved_state2['mass'])
        self.assertEquals( 0.0,  retrieved_state1['x'])
        self.assertEquals(10.0,  retrieved_state2['x'])
        
        self.assertEquals(0, instance.cleanup_code())
        instance.stop()
    
    def test3(self):
        print "Test PikachuInterface particle property getters/setters"
        instance = self.new_instance_of_an_optional_code(PikachuInterface, **default_options)
        self.assertEquals(0, instance.initialize_code())
        self.assertEquals(0, instance.set_kernel_directory(instance.default_kernel_directory))
        self.assertEquals(0, instance.commit_parameters())
        self.assertEquals([1, 0], instance.new_particle(0.01,  1, 0, 0,  0, 1, 0, 0.1).values())
        self.assertEquals([2, 0], instance.new_particle(0.02, -1, 0, 0,  0,-1, 0, 0.1).values())
        self.assertEquals(-3, instance.get_mass(1)['__result']) # Have to commit first
        self.assertEquals(0, instance.commit_particles())
        
        # getters
        mass, result = instance.get_mass(1)
        self.assertAlmostEquals(0.01, mass)
        self.assertEquals(0,result)
        radius, result = instance.get_radius(2)
        self.assertAlmostEquals(0.1, radius)
        self.assertEquals(0,result)
        self.assertEquals(-3, instance.get_mass(3)['__result']) # Particle not found
        self.assertEquals([ 1, 0, 0,  0], instance.get_position(1).values())
        self.assertEquals([-1, 0, 0,  0], instance.get_position(2).values())
        self.assertEquals([ 0, 1, 0,  0], instance.get_velocity(1).values())
        self.assertEquals([ 0,-1, 0,  0], instance.get_velocity(2).values())
        
        # setters
        self.assertEquals(0, instance.set_state(1, 0.01, 1,2,3, 4,5,6, 0.1))
        self.assertEquals([0.01, 1.0,2.0,3.0, 4.0,5.0,6.0, 0.1, 0], instance.get_state(1).values())
        self.assertEquals(0, instance.set_mass(1, 0.02))
        self.assertEquals([0.02, 1.0,2.0,3.0, 4.0,5.0,6.0, 0.1, 0], instance.get_state(1).values())
        self.assertEquals(0, instance.set_radius(1, 0.2))
        self.assertEquals([0.02, 1.0,2.0,3.0, 4.0,5.0,6.0, 0.2, 0], instance.get_state(1).values())
        self.assertEquals(0, instance.set_position(1, 10,20,30))
        self.assertEquals([0.02, 10.0,20.0,30.0, 4.0,5.0,6.0, 0.2, 0], instance.get_state(1).values())
        self.assertEquals(0, instance.set_velocity(1, 40,50,60))
        self.assertEquals([0.02, 10.0,20.0,30.0, 40.0,50.0,60.0, 0.2, 0], instance.get_state(1).values())

        self.assertEquals(0, instance.cleanup_code())
        instance.stop()
    
    def test4(self):
        print "Test PikachuInterface parameters"
        instance = self.new_instance_of_an_optional_code(PikachuInterface, **default_options)
        self.assertEquals(0, instance.initialize_code())
        
        self.assertEquals(0, instance.set_kernel_directory(instance.default_kernel_directory))
        
        # Pikachu has separate epsilon_squared parameters for different interactions!
        self.assertEquals([1.0e-8, 0], instance.get_eps2_fs_fs().values())
        self.assertEquals([1.0e-8, 0], instance.get_eps2_fs_bh().values())
        self.assertEquals([0, 0], instance.get_eps2_bh_bh().values())
        self.assertEquals(-2, instance.get_eps2()['__result']) # Not implemented (would be ambiguous)
        
        self.assertEquals(0, instance.set_eps2_fs_fs(0.2))
        self.assertEquals([0.2, 0], instance.get_eps2_fs_fs().values())
        self.assertEquals(0, instance.set_eps2_fs_bh(0.3))
        self.assertEquals([0.3, 0], instance.get_eps2_fs_bh().values())
        self.assertEquals(0, instance.set_eps2_bh_bh(0.4))
        self.assertEquals([0.4, 0], instance.get_eps2_bh_bh().values())
        self.assertEquals(-2, instance.set_eps2(0.1)) # Not implemented (would be ambiguous)
        
        self.assertEquals([0.005, 0], instance.get_eta_s().values())
        self.assertEquals([0.025, 0], instance.get_eta_fs().values())
        self.assertEquals([0.025, 0], instance.get_eta_smbh().values())
        
        self.assertEquals(0, instance.set_eta_s(0.01))
        self.assertEquals([0.01, 0], instance.get_eta_s().values())
        self.assertEquals(0, instance.set_eta_fs(0.02))
        self.assertEquals([0.02, 0], instance.get_eta_fs().values())
        self.assertEquals(0, instance.set_eta_smbh(0.03))
        self.assertEquals([0.03, 0], instance.get_eta_smbh().values())
        
        self.assertEquals(0, instance.commit_parameters())
        self.assertEquals(0, instance.cleanup_code())
        instance.stop()
    


class TestPikachu(TestWithMPI):
    
    default_converter = nbody_system.nbody_to_si(1.0e4 | units.MSun, 1.0 | units.AU)
    
    def new_sun_earth_system(self):
        particles = Particles(2)
        particles.mass = [1.0, 3.0037e-6] | units.MSun
        particles.position = [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]] | units.AU
        particles.velocity = [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0]] | units.km / units.s
        particles[1].vy = (constants.G * particles.total_mass() / (1.0 | units.AU)).sqrt()
        return particles
    
    def test1(self):
        print "Testing Pikachu initialization"
        instance = self.new_instance_of_an_optional_code(Pikachu, self.default_converter, **default_options)
        instance.initialize_code()
        instance.commit_parameters()
        instance.cleanup_code()
        instance.stop()
    
    def test2(self):
        print "Testing Pikachu parameters"
        instance = self.new_instance_of_an_optional_code(Pikachu, self.default_converter, **default_options)
        instance.initialize_code()
        
        self.assertEquals(instance.parameters.epsilon_squared, 
            instance.unit_converter.to_si(1.0e-8 | nbody_system.length**2))
        self.assertEquals(instance.parameters.timestep_parameter, 0.025)
        
        for par, value in [('epsilon_squared_star_star', 1.0e-8 | nbody_system.length**2), 
                ('epsilon_squared_star_blackhole', 1.0e-8 | nbody_system.length**2), 
                ('epsilon_squared_blackhole_blackhole', 0.0 | nbody_system.length**2),
                ('initial_timestep_parameter', 0.005),
                ('timestep_parameter_stars', 0.025),
                ('timestep_parameter_black_holes', 0.025),
                ('timestep', 1.0/2048.0 | nbody_system.time),
                ('search_factor', 3.0),
                ('velocity_dispersion', 0.707106781 | nbody_system.speed),
                ('rcut_out_star_star', 2.0e-3 | nbody_system.length),
                ('rcut_out_star_blackhole', 2.0e-2 | nbody_system.length),
                ('rcut_out_blackhole_blackhole', 1.0e5 | nbody_system.length),
                ('rsearch_star_star', 0.0 | nbody_system.length),
                ('rsearch_star_blackhole', 0.0 | nbody_system.length),
                ('rsearch_blackhole_blackhole', 0.0 | nbody_system.length),
                ('opening_angle', 0.4)]:
            self.assertEquals(instance.unit_converter.to_si(value), 
                getattr(instance.parameters, par))
                
            if hasattr(value, 'unit'):
                new_value = 3.0 | value.unit
            else:
                new_value = 3.0
                
            setattr(instance.parameters, par, new_value)
            self.assertEquals(instance.unit_converter.to_si(new_value),
                getattr(instance.parameters, par))
        
        # epsilon_squared is an alias for epsilon_squared_star_star, so epsilon_squared also has become 3:
        self.assertEquals(instance.parameters.epsilon_squared, 
            instance.unit_converter.to_si(3.0 | nbody_system.length**2))
        instance.parameters.epsilon_squared = 0.1 | nbody_system.length**2
        self.assertEquals(instance.parameters.epsilon_squared, 
            instance.unit_converter.to_si(0.1 | nbody_system.length**2))
        # timestep_parameter is an alias for timestep_parameter_stars, so timestep_parameter also has become 3:
        self.assertEquals(instance.parameters.timestep_parameter, 3.0)
        instance.parameters.timestep_parameter = 0.01
        self.assertEquals(instance.parameters.timestep_parameter, 0.01)
        
        self.assertEquals(instance.parameters.calculate_quadrupole_moments, False)
        instance.parameters.calculate_quadrupole_moments = True
        self.assertEquals(instance.parameters.calculate_quadrupole_moments, True)
        
        instance.commit_parameters()
        p = instance.parameters
        self.assertAlmostRelativeEquals(p.rsearch_star_star, 
            p.rcut_out_star_star + p.search_factor * p.velocity_dispersion * p.timestep, 10)
        self.assertAlmostRelativeEquals(p.rsearch_star_blackhole, 
            p.rcut_out_star_blackhole + p.search_factor * p.velocity_dispersion * p.timestep, 10)
        self.assertAlmostRelativeEquals(p.rsearch_blackhole_blackhole, 
            p.rcut_out_blackhole_blackhole + p.search_factor * p.velocity_dispersion * p.timestep, 10)
        
        instance.stop()
    
    def test3(self):
        print "Testing Pikachu particles"
        instance = self.new_instance_of_an_optional_code(Pikachu, self.default_converter, **default_options)
        instance.initialize_code()
        instance.commit_parameters()
        instance.particles.add_particles(self.new_sun_earth_system())
        instance.commit_particles()
        
        self.assertAlmostEquals(instance.particles.mass, [1.0, 3.0037e-6] | units.MSun)
        self.assertAlmostEquals(instance.particles.position, 
            [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]] | units.AU)
        self.assertAlmostEquals(instance.particles.velocity, 
            [[0.0, 0.0, 0.0], [0.0, 29.7885, 0.0]] | units.km / units.s, 3)
        
        instance.cleanup_code()
        instance.stop()
    
    
    def xtest5(self):
        print "Testing Pikachu evolve_model, 2 particles, no SMBH"
        particles = Particles(2)
        particles.mass = 1.0 | units.MSun
        particles.radius = 1.0 | units.RSun
        particles.position = [[0.0, 0.0, 0.0], [2.0, 0.0, 0.0]] | units.AU
        particles.velocity = [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0]] | units.km / units.s
        particles[1].vy = (constants.G * (2.0 | units.MSun) / (2.0 | units.AU)).sqrt()
        particles.move_to_center()
        print particles
        
        converter = nbody_system.nbody_to_si(1.0 | units.MSun, 1.0 | units.AU)
        instance = self.new_instance_of_an_optional_code(Pikachu, converter, **default_options)
        instance.initialize_code()
        instance.parameters.smbh_mass = 0.0 | units.MSun
        instance.commit_parameters()
        instance.particles.add_particles(particles)
        instance.commit_particles()
        primary = instance.particles[0]
        
        P = 2 * math.pi * primary.x / primary.vy
        
        position_at_start = primary.position.x
        instance.evolve_model(P / 4.0)
        self.assertAlmostRelativeEqual(position_at_start, primary.position.y, 3)
        
        instance.evolve_model(P / 2.0)
        self.assertAlmostRelativeEqual(position_at_start, -primary.position.x, 3)
        
        instance.evolve_model(P)
        self.assertAlmostRelativeEqual(position_at_start, primary.position.x, 3)
        
        instance.cleanup_code()
        instance.stop()
    
    def xtest6(self):
        print "Testing Pikachu evolve_model, earth-sun system, no SMBH"
        converter = nbody_system.nbody_to_si(1.0 | units.MSun, 1.0 | units.AU)
        instance = self.new_instance_of_an_optional_code(Pikachu, converter, **default_options)
        instance.initialize_code()
        instance.parameters.smbh_mass = 0.0 | units.MSun
        instance.commit_parameters()
        instance.particles.add_particles(self.new_sun_earth_system())
        instance.commit_particles()
        earth = instance.particles[1]
        
        position_at_start = earth.position.x
        instance.evolve_model(0.25 | units.yr)
        self.assertAlmostRelativeEqual(position_at_start, earth.position.y, 3)
        
        instance.evolve_model(0.5 | units.yr)
        self.assertAlmostRelativeEqual(position_at_start, -earth.position.x, 3)
        
        instance.evolve_model(1.0 | units.yr)
        self.assertAlmostRelativeEqual(position_at_start, earth.position.x, 3)
        
        instance.cleanup_code()
        instance.stop()
