from amuse.support.io import store
from amuse.support.units import units
from amuse.support.data.core import Stars
from amuse.test import amusetest

import os

class TestStoreHDF(amusetest.TestCase):
    
    def test1(self):
        test_results_path = self.get_path_to_results()
        output_file = os.path.join(test_results_path, "test.hdf5")
        if os.path.exists(output_file):
            os.remove(output_file)
        instance = store.StoreHDF(output_file)
        
        number_of_particles = 10
        p = Stars(number_of_particles)
        p.mass = [x * 2.0 for x in range(number_of_particles)] | units.kg
        p.model_time = 2.0 | units.s
        
        instance.store(p)
        
        loaded_particles = instance.load()
        
        loaded_mass_in_kg = loaded_particles.mass.value_in(units.kg)
        previous_mass_in_kg = p.mass.value_in(units.kg)
        for expected, actual in zip(previous_mass_in_kg, loaded_mass_in_kg):
            self.assertEquals(expected, actual)
        
    def test2(self):
        test_results_path = self.get_path_to_results()
        output_file = os.path.join(test_results_path, "test.hdf5")
        if os.path.exists(output_file):
            os.remove(output_file)
        instance = store.StoreHDF(output_file)
        number_of_particles = 10
        p = Stars(number_of_particles)
        p.mass = [x * 2.0 for x in range(number_of_particles)] | units.kg
        p.savepoint(1 | units.Myr)
        instance.store(p.previous_state())
        
        p.mass = [x * 4.0 for x in range(number_of_particles)] | units.kg
        p.savepoint(2 | units.Myr)
        instance.store(p.previous_state())
        instance.close()
        
        instance = store.StoreHDF(output_file)
        loaded_particles = instance.load()
        masses = loaded_particles[1].get_timeline_of_attribute("mass")
        self.assertEquals(len(masses), 2)
        
        
        
        
        
