from amuse.test import amusetest
from amuse.support.data.core import *

from amuse.support.units import units
from amuse.legacy.hermite0.interface import Hermite
from amuse.support.units import nbody_system
from amuse.support.io import store
import numpy
import math
import os

class TestAttributeError(amusetest.TestCase):
    
    def test1(self):
        print "Test1: Should get error when accessing non-existent attributes (InMemoryAttributeStorage)."
        particles = Particles(4)
        particle  = Particle()
        subset    = particles[:2]
        superset  = ParticlesSuperset([particles, particle.as_set()])

        instances = [particles, particle, subset, superset]
        classes = [Particles, Particle, ParticlesSubset, ParticlesSuperset]
        lengths = [4, 1, 2, 5]
        for i, x in enumerate(instances):
            self.assertTrue(isinstance(x, classes[i]))
            self.assertEquals(len(x.as_set()), lengths[i])
            self.assertRaises(AttributeError, lambda: x.bogus, expected_message = 
                "You tried to access attribute 'bogus' but this attribute is not defined for this set.")
                
    def test2(self):
        print "Test2: Should get error when accessing non-existent attributes (in Legacy code storage)."
        particles = Particles(4)
        particle  = Particle()
        subset    = particles[:2]
        superset  = ParticlesSuperset([particles, particle.as_set()])
        superset.mass = 1.0 | units.MSun
        superset.radius = 1.0 | units.RSun
        for i, x in enumerate(superset):
            x.position = units.AU(numpy.array((math.cos(i),math.sin(i),0.0)))
            x.velocity = units.kms(numpy.array((math.sin(i),math.cos(i),0.0)))
        instances = [particles, particle, subset, superset]
        classes = [Particles, Particle, ParticlesSubset, ParticlesSuperset]
        lengths = [4, 1, 2, 5]
        convert_nbody = nbody_system.nbody_to_si(1.0 | units.MSun, 1.0 | units.AU)
        for i, x in enumerate(instances):
            self.assertTrue(isinstance(x, classes[i]))
            self.assertEquals(len(x.as_set()), lengths[i])
            gravity = Hermite(convert_nbody)
            gravity.initialize_code()
            if isinstance(x, Particle): x = x.as_set()
            gravity.particles.add_particles(x)
            self.assertRaises(AttributeError, lambda: gravity.particles.bogus, expected_message = 
                "You tried to access attribute 'bogus' but this attribute is not defined for this set.")
            gravity.stop()
    
    def test3(self):
        print "Test3: Should get error when accessing non-existent attributes (HDF5 storage)."
        particles = Particles(4)
        particle  = Particle()
        subset    = particles[:2]
        superset  = ParticlesSuperset([particles, particle.as_set()])
        superset.mass = 1.0 | units.MSun
        test_results_path = self.get_path_to_results()
        output_file = os.path.join(test_results_path, "attr_test.hdf5")
        
        instances = [particles, particle, subset]
        classes = [Particles, Particle, ParticlesSubset]
        lengths = [4, 1, 2]
        for i, x in enumerate(instances):
            self.assertTrue(isinstance(x, classes[i]))
            self.assertEquals(len(x.as_set()), lengths[i])
            if os.path.exists(output_file):
                os.remove(output_file)
            HDFstorage = store.StoreHDF(output_file)
            if isinstance(x, Particle): x = x.as_set()
            x.model_time = 2.0 | units.s
            HDFstorage.store(x)
            loaded_particles = HDFstorage.load()
            self.assertRaises(AttributeError, lambda: loaded_particles.bogus, expected_message = 
                "You tried to access attribute 'bogus' but this attribute is not defined for this set.")
            HDFstorage.close()
            del HDFstorage
    
    def bogus_func(self, x):
        x.mass = 1.0
    
    def test4(self):
        print "Test4: Should get error when setting attributes with non-quantities (InMemoryAttributeStorage)."
        particles = Particles(4)
        particle  = Particle()
        subset    = particles[:2]
        superset  = ParticlesSuperset([particles, particle.as_set()])

        instances = [particles, particle, subset, superset]
        classes = [Particles, Particle, ParticlesSubset, ParticlesSuperset]
        lengths = [4, 1, 2, 5]
        for i, x in enumerate(instances):
            self.assertTrue(isinstance(x, classes[i]))
            self.assertEquals(len(x.as_set()), lengths[i])
            self.assertRaises(AttributeError, self.bogus_func, x, expected_message = 
                "Can only assign quantities or other particles to an attribute.")
    
    def test5(self):
        print "Test5: Should get error when setting attributes with non-quantities (in Legacy code storage)."
        particles = Particles(4)
        particle  = Particle()
        subset    = particles[:2]
        superset  = ParticlesSuperset([particles, particle.as_set()])
        superset.mass = 1.0 | units.MSun
        superset.radius = 1.0 | units.RSun
        for i, x in enumerate(superset):
            x.position = units.AU(numpy.array((math.cos(i),math.sin(i),0.0)))
            x.velocity = units.kms(numpy.array((math.sin(i),math.cos(i),0.0)))
        instances = [particles, particle, subset, superset]
        classes = [Particles, Particle, ParticlesSubset, ParticlesSuperset]
        lengths = [4, 1, 2, 5]
        convert_nbody = nbody_system.nbody_to_si(1.0 | units.MSun, 1.0 | units.AU)
        for i, x in enumerate(instances):
            self.assertTrue(isinstance(x, classes[i]))
            self.assertEquals(len(x.as_set()), lengths[i])
            gravity = Hermite(convert_nbody)
            gravity.initialize_code()
            if isinstance(x, Particle): x = x.as_set()
            gravity.particles.add_particles(x)
            self.assertRaises(AttributeError, self.bogus_func, gravity.particles, expected_message = 
                "Can only assign quantities or other particles to an attribute.")
            gravity.stop()
    
    def test6(self):
        print "Test6: Should get error when setting attributes with non-quantities (HDF5 storage)."
        particles = Particles(4)
        particle  = Particle()
        subset    = particles[:2]
        superset  = ParticlesSuperset([particles, particle.as_set()])
        superset.mass = 1.0 | units.MSun
        test_results_path = self.get_path_to_results()
        output_file = os.path.join(test_results_path, "attr_test.hdf5")
        instances = [particles, particle, subset]
        classes = [Particles, Particle, ParticlesSubset]
        lengths = [4, 1, 2]
        for i, x in enumerate(instances):
            self.assertTrue(isinstance(x, classes[i]))
            self.assertEquals(len(x.as_set()), lengths[i])
            if os.path.exists(output_file):
                os.remove(output_file)
            HDFstorage = store.StoreHDF(output_file)
            if isinstance(x, Particle): x = x.as_set()
            x.model_time = 2.0 | units.s
            HDFstorage.store(x)
            loaded_particles = HDFstorage.load()
            self.assertRaises(AttributeError, self.bogus_func, loaded_particles, expected_message = 
                "Can only assign quantities or other particles to an attribute.")
            HDFstorage.close()
            del HDFstorage
    
