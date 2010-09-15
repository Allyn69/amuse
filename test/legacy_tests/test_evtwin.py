from amuse.test.amusetest import TestWithMPI
import sys
import os.path

from amuse.legacy.evtwin.interface import EVtwin, EVtwinInterface

from amuse.support.exceptions import AmuseException
from amuse.support.data import core
from amuse.support.units import nbody_system
from amuse.support.units import units
from amuse.support.legacy import channel

class TestInterface(TestWithMPI):
    
    def test1(self):
        print "Testing get/set for metallicity..."
        #channel.MessageChannel.DEBUGGER = channel.MessageChannel.XTERM
        instance = EVtwinInterface()
        #channel.MessageChannel.DEBUGGER = None
        (metallicity, error) = instance.get_metallicity()
        self.assertEquals(0, error)
        self.assertEquals(0.02, metallicity)
        error = instance.set_ev_path(instance.get_data_directory())
        self.assertEquals(0, error)
        error = instance.initialize_code()
        self.assertEquals(0, error)
        instance.stop()

        for x in [0.03, 0.01, 0.004, 0.001, 0.0003, 0.0001]:
            instance = EVtwinInterface()
            error = instance.set_metallicity(x)
            self.assertEquals(0, error)
            (metallicity, error) = instance.get_metallicity()
            self.assertEquals(0, error)
            self.assertEquals(x, metallicity)
            error = instance.set_ev_path(instance.get_data_directory())
            self.assertEquals(0, error)      
            error = instance.initialize_code()
            if os.path.exists(os.path.join(instance.get_data_directory(),'zams','zams'+str(x)[2:]+'.mod')):
                self.assertEquals(0, error)
            else:
                self.assertEquals(-1, error)
                print "Metallicities other than solar need additional starting models!"
            instance.stop()
    
    def test2(self):
        print "Testing get/set for maximum number of stars..."
        instance = EVtwinInterface()
        
        (value, error) = instance.get_maximum_number_of_stars()
        self.assertEquals(0, error)      
        
        for x in range(10,100,10):
            error = instance.set_maximum_number_of_stars(x)
            self.assertEquals(0, error)      
            
            (value, error) = instance.get_maximum_number_of_stars()
            self.assertEquals(0, error)      
            self.assertEquals(x, value)      
        
        instance.stop()
    
    def test4(self):
        print "Testing initialization..."
        instance = EVtwinInterface()
        
        error = instance.set_ev_path(instance.get_data_directory())
        self.assertEquals(0, error)      
        
        error = instance.initialize_code()
        self.assertEquals(0, error)      
        
        instance.stop()
    
    def test5(self):
        print "Testing basic operations (new_particle, evolve etc.)..."
        #code/library_v2.f:602
        #channel.MessageChannel.DEBUGGER = channel.MessageChannel.XTERM
        instance = EVtwinInterface()
        #channel.MessageChannel.DEBUGGER = None
        
        error = instance.set_ev_path(instance.get_data_directory())
        self.assertEquals(0, error)      
        
        error = instance.initialize_code()
        self.assertEquals(0, error)      
        
        (index_of_the_star, error) = instance.new_particle(1.05)
        self.assertEquals(0, error)       
        
        self.assertTrue(index_of_the_star >= 0)      
        
        (mass, error) = instance.get_mass(index_of_the_star)
        self.assertEquals(0, error)      
        self.assertEquals(1.05, mass)    
        
        error = instance.evolve(index_of_the_star)
        self.assertEquals(0, error)      
          
        for i in range(2):
            error = instance.evolve(index_of_the_star)
            self.assertEquals(0, error)      
    
        (mass, error) = instance.get_mass(index_of_the_star)
        self.assertEquals(0, error)      
        self.assertTrue(mass < 1.05)  
    
        (age, error) = instance.get_age(index_of_the_star)
        self.assertEquals(0, error) 
        self.assertTrue(age > 0)      
        
        instance.stop()
        
    def test6(self):
        print "Testing EVtwin stop conditions..."
        instance = EVtwinInterface()
        error = instance.set_ev_path(instance.get_data_directory())
        self.assertEquals(0, error)      
        error = instance.initialize_code()
        self.assertEquals(0, error)      
        
        (value, error) = instance.get_max_age_stop_condition()
        self.assertEquals(0, error)
        self.assertEquals(2.0e12, value)
        for x in range(10,14):
            error = instance.set_max_age_stop_condition(10 ** x)
            self.assertEquals(0, error)
            (value, error) = instance.get_max_age_stop_condition()
            self.assertEquals(0, error)      
            self.assertEquals(10 ** x, value)
            
        (value, error) = instance.get_min_timestep_stop_condition()
        self.assertEquals(0, error)
        self.assertAlmostEqual(0.031689, value, 5)
        for x in range(-3,2):
            error = instance.set_min_timestep_stop_condition(10 ** x)
            self.assertEquals(0, error)
            (value, error) = instance.get_min_timestep_stop_condition()
            self.assertEquals(0, error)
            self.assertEquals(10 ** x, value)
        
        instance.stop()

    def test7(self):
        print "Testing EVtwin parameters..."
        instance = EVtwinInterface()
        error = instance.set_ev_path(instance.get_data_directory())
        self.assertEquals(0, error)      
        error = instance.initialize_code()
        self.assertEquals(0, error)      
        
        (value, error) = instance.get_number_of_ionization_elements()
        self.assertEquals(0, error)
        self.assertEquals(2, value)
        for x in range(1,10):
            error = instance.set_number_of_ionization_elements(x)
            self.assertEquals(0, error)
            (value, error) = instance.get_number_of_ionization_elements()
            self.assertEquals(0, error)
            self.assertEquals(x, value)

        (value, error) = instance.get_convective_overshoot_parameter()
        self.assertEquals(0, error)
        self.assertEquals(0.12, value)
        for x in [0.0, 0.1, 0.12, 0.15]:
            error = instance.set_convective_overshoot_parameter(x)
            self.assertEquals(0, error)
            (value, error) = instance.get_convective_overshoot_parameter()
            self.assertEquals(0, error)
            self.assertEquals(x, value)

        (value, error) = instance.get_mixing_length_ratio()
        self.assertEquals(0, error)
        self.assertEquals(2.0, value)
        for x in [0.1, 1.0, 3.0]:
            error = instance.set_mixing_length_ratio(x)
            self.assertEquals(0, error)
            (value, error) = instance.get_mixing_length_ratio()
            self.assertEquals(0, error)
            self.assertEquals(x, value)

        (value, error) = instance.get_semi_convection_efficiency()
        self.assertEquals(0, error)
        self.assertEquals(0.04, value)
        for x in [0.0, 0.1]:
            error = instance.set_semi_convection_efficiency(x)
            self.assertEquals(0, error)
            (value, error) = instance.get_semi_convection_efficiency()
            self.assertEquals(0, error)
            self.assertEquals(x, value)
        
        (value, error) = instance.get_thermohaline_mixing_parameter()
        self.assertEquals(0, error)
        self.assertEquals(1.0, value)
        for x in [0.0, 0.5, 1.5]:
            error = instance.set_thermohaline_mixing_parameter(x)
            self.assertEquals(0, error)
            (value, error) = instance.get_thermohaline_mixing_parameter()
            self.assertEquals(0, error)
            self.assertEquals(x, value)
        
        (value, error) = instance.get_AGB_wind_setting()
        self.assertEquals(0, error)
        self.assertEquals(1, value)
        error = instance.set_AGB_wind_setting(2)
        self.assertEquals(0, error)
        (value, error) = instance.get_AGB_wind_setting()
        self.assertEquals(0, error)
        self.assertEquals(2, value)
        
        (value, error) = instance.get_RGB_wind_setting()
        self.assertEquals(0, error)
        self.assertEquals(1.0, value)
        for x in [-1.0, -0.5, 0.0, 1.0]:
            error = instance.set_RGB_wind_setting(x)
            self.assertEquals(0, error)
            (value, error) = instance.get_RGB_wind_setting()
            self.assertEquals(0, error)
            self.assertEquals(x, value)
        
        instance.stop()

    def test8(self):
        print "Testing basic operations for spinning particle (new_spinning_particle, get_spin etc.)..."
        instance = EVtwinInterface()
        error = instance.set_ev_path(instance.get_data_directory())
        self.assertEquals(0, error)
        error = instance.initialize_code()
        self.assertEquals(0, error)
        
        (index_of_default_star, error) = instance.new_particle(1.05)
        self.assertEquals(0, error)
        self.assertTrue(index_of_default_star >= 0)
        (index_of_spinning_star, error) = instance.new_spinning_particle(1.05, 300.0)
        self.assertEquals(0, error)
        self.assertTrue(index_of_spinning_star >= 0)
        
        (spin, error) = instance.get_spin(index_of_default_star)
        self.assertEquals(0, error)
        self.assertAlmostEqual(54450.2652, spin,3)
        (spin, error) = instance.get_spin(index_of_spinning_star)
        self.assertEquals(0, error)
        self.assertEquals(300.0, spin)
        
        instance.stop()
    
    
class TestInterfaceBinding(TestWithMPI):
    
            
    
    def test1(self):
        print "Testing assigned default parameter values..."
        instance = EVtwin()
        
        instance.parameters.set_defaults()
        
        self.assertEquals(10.0 | units.no_unit, instance.parameters.maximum_number_of_stars)
        instance.parameters.maximum_number_of_stars = 12 | units.no_unit
        self.assertEquals(12.0 | units.no_unit, instance.parameters.maximum_number_of_stars)
        instance.stop()
    
    def test2(self):
        print "Testing basic operations (setup_particles, initialize_stars etc.)..."
        instance = EVtwin()
        instance.initialize_module_with_default_parameters()
        
        path = os.path.join(instance.default_path_to_ev_database, 'run')
        path = os.path.join(path, 'muse')
        
        #instance.set_init_dat_name(os.path.join(path,'init.dat'))
        #instance.set_init_run_name(os.path.join(path,'init.run'))
        
        stars = core.Stars(1)
        stars[0].mass = 10 | units.MSun
        
        instance.setup_particles(stars)
        instance.initialize_stars()
        instance.update_particles(stars)
        
        self.assertEquals(stars[0].mass, 10 | units.MSun)
        self.assertAlmostEquals(stars[0].luminosity.value_in(units.LSun), 5695.19757302, 6)
        instance.stop()
    
    def xtest3(self):
        #channel.MessageChannel.DEBUGGER = channel.MessageChannel.DDD
        instance = EVtwin()
        #channel.MessageChannel.DEBUGGER = None
        instance.initialize_module_with_default_parameters() 
        stars =  core.Stars(1)
        
        star = stars[0]
        star.mass = 5.0 | units.MSun
        star.radius = 0.0 | units.RSun
        
        instance.particles.add_particles(stars)
        instance.initialize_stars()
        
        from_code_to_model = instance.particles.new_channel_to(stars)
        from_code_to_model.copy()
        
        previous_type = star.stellar_type
        results = []
        t0 = 0 | units.Myr
        current_time = t0
        
        while current_time < (115 | units.Myr):
            instance.evolve_model()
            from_code_to_model.copy()
            
            current_time = star.age
            print (star.age, star.mass, star.stellar_type)
            if not star.stellar_type == previous_type:
                results.append((star.age, star.mass, star.stellar_type))
                previous_type = star.stellar_type
        
        print results
        self.assertEqual(len(results), 6)
        
        times = ( 
            104.0 | units.Myr, 
            104.4 | units.Myr, 
            104.7 | units.Myr, 
            120.1 | units.Myr,
            120.9 | units.Myr,
            121.5 | units.Myr
        )
        for result, expected in zip(results, times):
            self.assertAlmostEqual(result[0].value_in(units.Myr), expected.value_in(units.Myr), 1)
            
        masses = ( 
            5.000 | units.MSun, 
            5.000 | units.MSun, 
            4.998 | units.MSun, 
            4.932 | units.MSun,
            4.895 | units.MSun,
            0.997 | units.MSun
        )
        for result, expected in zip(results, masses):
            self.assertAlmostEqual(result[1].value_in(units.MSun), expected.value_in(units.MSun), 3)
         
        types = (
            "Hertzsprung Gap",
            "First Giant Branch",
            "Core Helium Burning",
            "First Asymptotic Giant Branch",
            "Second Asymptotic Giant Branch",
            "Carbon/Oxygen White Dwarf",
        )
        
        for result, expected in zip(results, types):
            self.assertEquals(str(result[2]), expected)
        
        instance.stop()
        
    def test4(self):
        print "Testing max age stop condition..."
        #masses = [.5, 1.0, 1.5] | units.MSun # Test with fewer particles for speed-up.
        masses = [.5] | units.MSun
        max_age = 6.0 | units.Myr

        number_of_stars=len(masses)
        stars =  core.Stars(number_of_stars)
        for i, star in enumerate(stars):
            star.mass = masses[i]
            star.radius = 0.0 | units.RSun

#       Initialize stellar evolution code
        instance = EVtwin()
        instance.initialize_module_with_default_parameters() 
        if instance.get_maximum_number_of_stars() < number_of_stars:
            instance.set_maximum_number_of_stars(number_of_stars)
        self.assertEqual(instance.parameters.max_age_stop_condition, 2e6 | units.Myr)
        instance.parameters.max_age_stop_condition = max_age
        self.assertEqual(instance.parameters.max_age_stop_condition, max_age)
        instance.setup_particles(stars)
#       Let the code perform initialization actions after all particles have been created. 
        instance.initialize_stars()
        
        from_code_to_model = instance.particles.new_channel_to(stars)
        from_code_to_model.copy()
        
        instance.evolve_model(end_time = 4.0 | units.Myr)
        from_code_to_model.copy()
        
        for i in range(number_of_stars):
            self.assertTrue(stars[i].age.value_in(units.Myr) >= 4.0)
            self.assertTrue(stars[i].age <= max_age)
            self.assertTrue(stars[i].mass <= masses[i])
            self.assertTrue(stars[i].time_step <= max_age)
                
        self.assertRaises(AmuseException, instance.evolve_model, end_time = 2*max_age, 
            expected_message = "Error when calling 'evolve' of a 'EVtwin', errorcode "
                "is 2, error is 'BACKUP -- tstep reduced below limit; quit'")

        instance.stop()
        
    def test5_add_and_remove(self):
        print "Testing adding and removing particles from stellar evolution code..."
        instance = EVtwin()
        instance.initialize_module_with_default_parameters() 
        stars = core.Stars(0)
#       Create an "array" of one star
        stars1 = core.Stars(1)
        star1=stars1[0]
        star1.mass = 1.0 | units.MSun
        star1.radius = 0.0 | units.RSun
#       Create another "array" of one star
        stars2 = core.Stars(1)
        star2=stars2[0]
        star2.mass = 1.0 | units.MSun
        star2.radius = 0.0 | units.RSun
        key1 = stars1._get_keys()[0]
        key2 = stars2._get_keys()[0]
        stars.add_particles(stars1)
        stars.add_particles(stars2)
        self.assertEquals(stars._get_keys()[1], key2)
        self.assertEquals(len(instance.particles), 0) # before creation
        instance.setup_particles(stars)
        instance.initialize_stars()
        indices_in_the_code = instance.particles._private.attribute_storage.get_indices_of(instance.particles._get_keys())
        for i in range(len(instance.particles)):
            self.assertEquals(indices_in_the_code[i], i+1)
        from_code_to_model = instance.particles.new_channel_to(stars)
        from_code_to_model.copy()
        instance.evolve_model(end_time=1.0|units.Myr)
        from_code_to_model.copy()
        self.assertEquals(len(instance.particles), 2) # before remove
        for i in range(len(instance.particles)):
            self.assertTrue(stars[i].age.value_in(units.Myr) > 1.0)
        instance.particles.remove_particle(stars[0])
        self.assertEquals(instance.particles._private.attribute_storage.get_indices_of(instance.particles._get_keys())[0], 2)
        self.assertEquals(len(instance.particles), 1) # in between remove
        self.assertEquals(instance.get_number_of_particles().number_of_particles, 1)
        stars.remove_particle(stars[0])
        self.assertEquals(stars._get_keys()[0], key2)
        self.assertEquals(len(stars), 1) # after remove
        from_code_to_model = instance.particles.new_channel_to(stars)
        instance.evolve_model(end_time=2.0|units.Myr)
        from_code_to_model.copy()
        age_of_star=stars[0].age
        self.assertTrue(age_of_star.value_in(units.Myr) > 2.0)
#       Create another "array" of one star
        stars3 = core.Stars(1)
        star3=stars3[0]
        star3.mass = 1.0 | units.MSun
        star3.radius = 0.0 | units.RSun
        key3 = stars3._get_keys()[0]
        stars.add_particles(stars3)
        stars.add_particles(stars1)
        self.assertEquals(stars._get_keys()[0], key2)
        self.assertEquals(stars._get_keys()[1], key3)
        self.assertEquals(stars._get_keys()[2], key1)
        instance.particles.add_particles(stars3)
        instance.particles.add_particles(stars1)
        indices_in_the_code = instance.particles._private.attribute_storage.get_indices_of(instance.particles._get_keys())
        self.assertEquals(indices_in_the_code[0], 2)
        self.assertEquals(indices_in_the_code[1], 1)
        self.assertEquals(indices_in_the_code[2], 3)
        self.assertEquals(len(instance.particles), 3) # it's back...
        self.assertEquals(stars[1].age.value_in(units.Myr), 0.0)
        self.assertEquals(stars[2].age.value_in(units.Myr), 0.0) # ... and rejuvenated
        from_code_to_model = instance.particles.new_channel_to(stars)
        instance.evolve_model(end_time=1.0|units.Myr)
        from_code_to_model.copy()
        self.assertTrue(stars[1].age.value_in(units.Myr) > 1.0 and stars[1].age.value_in(units.Myr) < 2.0)
        self.assertEquals(stars[1].age, stars[2].age)
        instance.evolve_model(end_time=2.0|units.Myr)
        from_code_to_model.copy()
        self.assertAlmostEqual(stars[1].age.value_in(units.Myr), age_of_star.value_in(units.Myr), 3)
        self.assertTrue(stars[0].age >= age_of_star)
        
        instance.stop()

