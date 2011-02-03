import os.path
from amuse.test.amusetest import TestWithMPI
from amuse.support.units import units
from amuse.support.data.core import Particles
from amuse.community.simplex.interface import SimpleXInterface, SimpleX

# Change the default for some SimpleX(-Interface) keyword arguments:
default_options = dict(number_of_workers=2)
default_options = dict(number_of_workers=2, redirection="none")

class TestSimpleXInterface(TestWithMPI):

    def test1(self):
        print "Test 1: initialization"
        instance = SimpleXInterface(**default_options)
        self.assertEqual(0, instance.set_output_directory(instance.output_directory))
        self.assertEqual(0, instance.initialize_code())
        self.assertEqual(0, instance.commit_parameters())
        self.assertEqual(0, instance.cleanup_code())
        instance.stop()
    
    def test2(self):
        print "Test 2: commit_particles, getters and setters"
        instance = SimpleXInterface(**default_options)
        self.assertEqual(0, instance.set_output_directory(instance.output_directory))
        self.assertEqual(0, instance.initialize_code())
        self.assertEqual(0, instance.commit_parameters())
        
        input_file = os.path.join(instance.data_directory, 'vertices_10.txt')
        x, y, z, n_H, flux, X_ion = read_input_file(input_file)
        number_of_particles = len(x)
        indices, errors = instance.new_particle(x, y, z, n_H, flux, X_ion)
        self.assertEqual(errors, [0]*number_of_particles)
        self.assertEqual(indices, range(number_of_particles))
        self.assertEqual(0, instance.commit_particles())
        x_out, y_out, z_out, n_H_out, flux_out, X_ion_out, error = instance.get_state(indices)
        for expected, received in zip([x, y, z, n_H, flux, X_ion, [0]*number_of_particles], 
                [x_out, y_out, z_out, n_H_out, flux_out, X_ion_out, error]):
            self.assertAlmostEqual(expected, received, 5)
        
        x, y, z, n_H, flux, X_ion, error = instance.get_state(0)
        for expected, received in zip([0.5, 0.5, 0.5, 0.001, 5.0, 0.0, 0], 
                [x, y, z, n_H, flux, X_ion, error]):
            self.assertAlmostEqual(expected, received)
        x, y, z, error1 = instance.get_position(0)
        n_H, error2     = instance.get_density(0)
        flux, error3    = instance.get_flux(0)
        X_ion, error4   = instance.get_ionisation(0)
        for expected, received in zip([0.5, 0.5, 0.5, 0.001, 5.0, 0.0, 0, 0, 0, 0], 
                [x, y, z, n_H, flux, X_ion, error1, error2, error3, error4]):
            self.assertAlmostEqual(expected, received, 5)
        
        self.assertEqual(0, instance.set_state(3, 1.0, 2.0, 3.0, 4.0, 5.0, 0.6))
        x, y, z, n_H, flux, X_ion, error = instance.get_state(3)
        for expected, received in zip([1.0, 2.0, 3.0, 4.0, 5.0, 0.6, 0], 
                [x, y, z, n_H, flux, X_ion, error]):
            self.assertAlmostEqual(expected, received, 5)
        self.assertEqual(0, instance.set_position(4, 3.0, 2.0, 1.0))
        self.assertEqual(0, instance.set_density(4, 0.6))
        self.assertEqual(0, instance.set_flux(4, 0.5))
        self.assertEqual(0, instance.set_ionisation(4, 0.4))
        x, y, z, n_H, flux, X_ion, error = instance.get_state(4)
        for expected, received in zip([3.0, 2.0, 1.0, 0.6, 0.5, 0.4, 0], 
                [x, y, z, n_H, flux, X_ion, error]):
            self.assertAlmostEqual(expected, received, 5)
        
        self.assertEqual(0, instance.cleanup_code())
        instance.stop()
    
    def test3(self):
        print "Test 3: evolve"
        instance = SimpleXInterface(**default_options)
        self.assertEqual(0, instance.set_output_directory(instance.output_directory))
        self.assertEqual(0, instance.initialize_code())
        self.assertEqual(0, instance.commit_parameters())
        
        input_file = os.path.join(instance.data_directory, 'vertices_10.txt')
        x, y, z, n_H, flux, X_ion = read_input_file(input_file)
        number_of_particles = len(x)
        indices, errors = instance.new_particle(x, y, z, n_H, flux, X_ion)
        self.assertEqual(errors, [0]*number_of_particles)
        self.assertEqual(indices, range(number_of_particles))
        self.assertEqual(0, instance.commit_particles())
        X_ion, errors = instance.get_ionisation(indices)
        self.assertEqual(errors, [0]*number_of_particles)
        self.assertAlmostEqual(X_ion.sum()/number_of_particles, 0.0)
        self.assertEqual(0, instance.evolve(0.5))
        X_ion, errors = instance.get_ionisation(indices)
        self.assertEqual(errors, [0]*number_of_particles)
        self.assertAlmostEqual(X_ion.sum()/number_of_particles, 0.000933205)
        
        self.assertEqual(0, instance.cleanup_code())
        instance.stop()
    

class TestSimpleX(TestWithMPI):

    def test1(self):
        print "Test 1: initialization"
        instance = SimpleX(**default_options)
        instance.initialize_code()
        instance.commit_parameters()
        instance.cleanup_code()
        instance.stop()
    
    def test2(self):
        print "Test 2: commit_particles, getters and setters"
        instance = SimpleX(**default_options)
        instance.initialize_code()
        instance.commit_parameters()
        
        input_file = os.path.join(instance.data_directory, 'vertices_10.txt')
        particles = particles_from_input_file(input_file)
        instance.particles.add_particles(particles)
        instance.commit_particles()
        for attribute in ['position', 'rho', 'flux', 'xion']:
            self.assertAlmostEqual(getattr(particles, attribute),
                                   getattr(instance.particles, attribute), 5)
            setattr(instance.particles, attribute, getattr(particles, attribute)*2.0)
            self.assertAlmostEqual(getattr(particles, attribute)*2.0,
                                   getattr(instance.particles, attribute), 5)
        instance.cleanup_code()
        instance.stop()
    
    def test3(self):
        print "Test 3: evolve"
        instance = SimpleX(**default_options)
        instance.initialize_code()
        instance.commit_parameters()
        
        input_file = os.path.join(instance.data_directory, 'vertices_10.txt')
        particles = particles_from_input_file(input_file)
        instance.particles.add_particles(particles)
        instance.commit_particles()
        self.assertAlmostEqual(instance.particles.xion.mean(), 0.0 | units.none)
        instance.evolve_model(0.5 | units.Myr)
        self.assertAlmostEqual(instance.particles.xion.mean(), 0.000933205 | units.none)
        instance.cleanup_code()
        instance.stop()
    
def read_input_file(input_file):
    file = open(input_file, 'r')
    lines = file.readlines()
    lines.pop(0)
    x, y, z, nh, flux, xion = [], [], [], [], [], []
    for line in lines:
        l = line.strip().split()
        if len(l) >= 7:
            x.append(float(l[1]))
            y.append(float(l[2]))
            z.append(float(l[3]))
            nh.append(float(l[4]))
            flux.append(float(l[5]))
            xion.append(float(l[6]))
    return x, y, z, nh, flux, xion

def particles_from_input_file(input_file):
    x, y, z, n_H, flux, X_ion = read_input_file(input_file)
    particles = Particles(len(x))
    particles.x = x | 13.20 * units.kpc
    particles.y = y | 13.20 * units.kpc
    particles.z = z | 13.20 * units.kpc
    particles.rho = n_H | 0.001 * units.amu / units.cm**3
    particles.flux = flux | 1.0e48 / units.s
    particles.xion = X_ion | units.none
    return particles

