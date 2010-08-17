from amuse.test.amusetest import TestWithMPI
import sys
import os.path
from numpy import pi

from amuse.legacy.mesa.interface import MESA, MESAInterface

from amuse.support.data import core
from amuse.support.units import units
from amuse.support.legacy import channel

class TestMESAInterface(TestWithMPI):
    
    def test1(self):
        print "Testing initialization of the interface..."
        #channel.MessageChannel.DEBUGGER = channel.MessageChannel.XTERM
        instance = self.new_instance(MESAInterface)
        #channel.MessageChannel.DEBUGGER = None
        if instance is None:
            print "MESA was not built. Skipping test."
            return
        inlist_path = instance.default_path_to_inlist
        #print "Path to inlist: ", inlist_path
        MESA_data_path = instance.default_path_to_MESA_data
        #print "Path to MESA data directory: ", MESA_data_path
        instance.set_MESA_paths(instance.default_path_to_inlist, 
            instance.default_path_to_MESA_data, instance.get_data_directory())
        status = instance.initialize_code()
        self.assertEqual(status,0)
        instance.stop()
        del instance
        
    def slowtest2(self):
        print "Testing get/set of metallicity (tests new ZAMS model implicitly)..."
        print "The first time this test will take quite some time" \
            " to generate new starting models."
        #channel.MessageChannel.DEBUGGER = channel.MessageChannel.XTERM
        instance = self.new_instance(MESAInterface)
        #channel.MessageChannel.DEBUGGER = None
        if instance is None:
            print "MESA was not built. Skipping test."
            return
        instance.set_MESA_paths(instance.default_path_to_inlist, 
            instance.default_path_to_MESA_data, instance.get_data_directory())
        status = instance.initialize_code()
        self.assertEqual(status,0)
        (metallicity, error) = instance.get_metallicity()
        self.assertEquals(0, error)
        self.assertEquals(0.02, metallicity)
        for x in [0.04, 0.02, 0.01, 0.00]:
            error = instance.set_metallicity(x)
            self.assertEquals(0, error)
            (metallicity, error) = instance.get_metallicity()
            self.assertEquals(0, error)
            self.assertEquals(x, metallicity)
        instance.stop()
        del instance
    
    def test3(self):
        print "Testing basic operations: new_particle..."
        #channel.MessageChannel.DEBUGGER = channel.MessageChannel.XTERM
        instance = self.new_instance(MESAInterface)
        #channel.MessageChannel.DEBUGGER = None
        if instance is None:
            print "MESA was not built. Skipping test."
            return
        (maximum_number_of_stars, error) = instance.get_maximum_number_of_stars()
        self.assertEquals(0, error)
        self.assertEqual(maximum_number_of_stars,1000)
        instance.set_MESA_paths(instance.default_path_to_inlist, 
            instance.default_path_to_MESA_data, instance.get_data_directory())
        status = instance.initialize_code()
        self.assertEqual(status,0)
        number_of_stars = 1
        for i in range(number_of_stars):
            #print i
            (index_of_the_star, error) = instance.new_particle(0.5+i*1.0/number_of_stars)
            self.assertEquals(0, error)
            self.assertEqual(index_of_the_star,i+1)
        #import time    # To check the amount of memory is used ...
        #time.sleep(10) # when a large number of stars is created.
        instance.stop()
        del instance
        
    def test4(self):
        print "Testing basic operations: evolve..."
        #channel.MessageChannel.DEBUGGER = channel.MessageChannel.XTERM
        instance = self.new_instance(MESAInterface)
        #channel.MessageChannel.DEBUGGER = None
        if instance is None:
            print "MESA was not built. Skipping test."
            return
        instance.set_MESA_paths(instance.default_path_to_inlist, 
            instance.default_path_to_MESA_data, instance.get_data_directory())
        status = instance.initialize_code()
        (index_of_the_star, error) = instance.new_particle(1.0)
        self.assertEquals(0, error)
        self.assertEqual(index_of_the_star,1)
        (time_step, error) = instance.get_time_step(index_of_the_star)
        self.assertEquals(0, error)
        self.assertAlmostEqual(time_step,1.0e5,1)
        error = instance.evolve(index_of_the_star)
        self.assertEquals(0, error)
        end_time = 5.0e5 # (years)
        instance.evolve_to(index_of_the_star, end_time)
        (age_of_the_star, error) = instance.get_age(index_of_the_star)
        self.assertEquals(0, error)
        self.assertAlmostEqual(age_of_the_star,end_time,3)
        (L_of_the_star, error) = instance.get_luminosity(index_of_the_star)
        self.assertEquals(0, error)
        self.assertAlmostEqual(L_of_the_star,0.725,1)
        (M_of_the_star, error) = instance.get_mass(index_of_the_star)
        self.assertEquals(0, error)
        self.assertAlmostEqual(M_of_the_star,1.000,3)
        (T_of_the_star, error) = instance.get_temperature(index_of_the_star)
        self.assertEquals(0, error)
        self.assertAlmostEqual(T_of_the_star,5650.998,-2)
        (time_step, error) = instance.get_time_step(index_of_the_star)
        self.assertEquals(0, error)
        self.assertAlmostEqual(time_step,163200.0,1)
        instance.stop()
        del instance
            
    def slowtest5(self):
        print "Testing evolve with varying Z (tests new ZAMS model implicitly)..."
        print "If the required starting models do not exist, this test will " \
            "take quite some time to generate them."
        #channel.MessageChannel.DEBUGGER = channel.MessageChannel.XTERM
        instance = self.new_instance(MESAInterface)
        #channel.MessageChannel.DEBUGGER = None
        if instance is None:
            print "MESA was not built. Skipping test."
            return
        instance.set_MESA_paths(instance.default_path_to_inlist, 
            instance.default_path_to_MESA_data, instance.get_data_directory())
        status = instance.initialize_code()
        self.assertEqual(status,0)
        metallicities = [0.00, 0.01, 0.02, 0.04]
        luminosities = [1.717, 0.938, 0.725, 0.592]
        for (i,(Z,L)) in enumerate(zip(metallicities, luminosities)):
            status = instance.set_metallicity(Z)
            self.assertEquals(0, status)
            (index_of_the_star, status) = instance.new_particle(1.0)
            self.assertEquals(0, status)
            self.assertEqual(index_of_the_star,i+1)
            instance.evolve_to(index_of_the_star, 5.0e5)
            (L_of_the_star, status) = instance.get_luminosity(index_of_the_star)
            self.assertEquals(0, status)
            self.assertAlmostEqual(L_of_the_star,L,1)
        instance.stop()
        del instance     
    
    def test6(self):
        print "Testing MESA stop conditions..."
        instance = self.new_instance(MESAInterface)
        if instance is None:
            print "MESA was not built. Skipping test."
            return
        (value, error) = instance.get_max_age_stop_condition()
        self.assertEquals(0, error) 
        self.assertEquals(1.0e12, value)
        for x in range(10,14):
            error = instance.set_max_age_stop_condition(10 ** x)
            self.assertEquals(0, error)
            (value, error) = instance.get_max_age_stop_condition()
            self.assertEquals(0, error)
            self.assertEquals(10 ** x, value)
        (value, error) = instance.get_min_timestep_stop_condition()
        self.assertEquals(0, error)
        self.assertEquals(1.0e-6, value)
        for x in range(-9,-2):
            error = instance.set_min_timestep_stop_condition(10.0 ** x)
            self.assertEquals(0, error)
            (value, error) = instance.get_min_timestep_stop_condition()
            self.assertEquals(0, error)
            self.assertEquals(10.0 ** x, value)
        instance.stop()
        del instance
    
    def test7(self):
        print "Testing MESA parameters..."
        instance = self.new_instance(MESAInterface)
        if instance is None:
            print "MESA was not built. Skipping test."
            return
        (value, error) = instance.get_mixing_length_ratio()
        self.assertEquals(0, error) 
        self.assertEquals(2.0, value)
        for x in [1.0, 1.5, 3.0]:
            error = instance.set_mixing_length_ratio(x)
            self.assertEquals(0, error)
            (value, error) = instance.get_mixing_length_ratio()
            self.assertEquals(0, error)
            self.assertEquals(x, value)
        (value, error) = instance.get_semi_convection_efficiency()
        self.assertEquals(0, error)
        self.assertEquals(0.0, value)
        for x in [0.1, 0.04, 0.001]:
            error = instance.set_semi_convection_efficiency(x)
            self.assertEquals(0, error)
            (value, error) = instance.get_semi_convection_efficiency()
            self.assertEquals(0, error)
            self.assertEquals(x, value)
        instance.stop()
        del instance
    
    def test8(self):
        print "Testing MESA wind parameters..."
        instance = self.new_instance(MESAInterface)
        if instance is None:
            print "MESA was not built. Skipping test."
            return
        (value, error) = instance.get_RGB_wind_scheme()
        self.assertEquals(0, error) 
        self.assertEquals(0, value)
        for x in range(6):
            error = instance.set_RGB_wind_scheme(x)
            self.assertEquals(0, error)
            (value, error) = instance.get_RGB_wind_scheme()
            self.assertEquals(0, error)
            self.assertEquals(x, value)
            
        (value, error) = instance.get_RGB_wind_efficiency()
        self.assertEquals(0, error)
        self.assertEquals(0.0, value)
        for x in [0.0, 0.1, 0.5, 1.0]:
            error = instance.set_RGB_wind_efficiency(x)
            self.assertEquals(0, error)
            (value, error) = instance.get_RGB_wind_efficiency()
            self.assertEquals(0, error)
            self.assertEquals(x, value)
            
        (value, error) = instance.get_AGB_wind_scheme()
        self.assertEquals(0, error) 
        self.assertEquals(0, value)
        for x in range(6):
            error = instance.set_AGB_wind_scheme(x)
            self.assertEquals(0, error)
            (value, error) = instance.get_AGB_wind_scheme()
            self.assertEquals(0, error)
            self.assertEquals(x, value)
            
        (value, error) = instance.get_AGB_wind_efficiency()
        self.assertEquals(0, error)
        self.assertEquals(0.0, value)
        for x in [0.0, 0.1, 0.5, 1.0]:
            error = instance.set_AGB_wind_efficiency(x)
            self.assertEquals(0, error)
            (value, error) = instance.get_AGB_wind_efficiency()
            self.assertEquals(0, error)
            self.assertEquals(x, value)
        instance.stop()
        del instance


class TestMESA(TestWithMPI):
    
    def test1(self):
        print "Testing initialization and default MESA parameters..."
        #channel.MessageChannel.DEBUGGER = channel.MessageChannel.XTERM
        instance = self.new_instance(MESA)
        #channel.MessageChannel.DEBUGGER = None
        if instance is None:
            print "MESA was not built. Skipping test."
            return
        instance.set_MESA_paths(instance.default_path_to_inlist, 
            instance.default_path_to_MESA_data, instance.get_data_directory())
        status = instance.initialize_code()
        self.assertEqual(status,0)
        instance.parameters.set_defaults()
        self.assertEquals(0.02 | units.no_unit, instance.parameters.metallicity)
        self.assertEquals(1.0e12 | units.yr, instance.parameters.max_age_stop_condition)
        instance.parameters.max_age_stop_condition = 1.0e2 | units.Myr
        self.assertEquals(1.0e2 | units.Myr, instance.parameters.max_age_stop_condition)
        instance.stop()
        del instance
    
    def test2(self):
        print "Testing basic operations: evolve and get_..."
        #channel.MessageChannel.DEBUGGER = channel.MessageChannel.XTERM
        instance = self.new_instance(MESA)
        #channel.MessageChannel.DEBUGGER = None
        if instance is None:
            print "MESA was not built. Skipping test."
            return
        instance.initialize_module_with_default_parameters()
        index_of_the_star = instance.new_particle(1.0 | units.MSun)
        self.assertEqual(index_of_the_star,1)
        time_step = instance.get_time_step(index_of_the_star)
        self.assertAlmostEqual(time_step, 1.0e5 | units.yr,1)
        instance.evolve(index_of_the_star)
        end_time = 5.0e5
        instance.evolve_to(index_of_the_star, end_time)
        age_of_the_star = instance.get_age(index_of_the_star)
        self.assertAlmostEqual(age_of_the_star,end_time | units.yr,3)
        L_of_the_star = instance.get_luminosity(index_of_the_star)
        self.assertAlmostEqual(L_of_the_star,0.725 | units.LSun,1)
        M_of_the_star = instance.get_mass(index_of_the_star)
        self.assertAlmostEqual(M_of_the_star,1.000 | units.MSun,3)
        T_of_the_star = instance.get_temperature(index_of_the_star)
        self.assertAlmostEqual(T_of_the_star,5650.998 | units.K,-2)
        time_step = instance.get_time_step(index_of_the_star)
        self.assertAlmostEqual(time_step,163200.0 | units.yr,1)
        instance.stop()
        del instance
    
    def test3(self):
        print "Testing basic operations: evolve_model and channels..."
        #channel.MessageChannel.DEBUGGER = channel.MessageChannel.XTERM
        instance = self.new_instance(MESA)
        #channel.MessageChannel.DEBUGGER = None
        if instance is None:
            print "MESA was not built. Skipping test."
            return
        instance.initialize_module_with_default_parameters()
        stars = core.Stars(1)
        mass = 10. | units.MSun
        stars.mass = mass
        instance.setup_particles(stars)
        instance.initialize_stars()
        from_code_to_model = instance.particles.new_channel_to(stars)
        from_code_to_model.copy()
        #print stars
        #instance.evolve_model(end_time = 0.03 | units.Myr) # speeding test up:
        self.assertEquals(stars[0].mass, mass)
        self.assertAlmostEquals(stars[0].luminosity, 5841. | units.LSun, 0)
        instance.evolve_model()
        from_code_to_model.copy()
        self.assertEquals(stars[0].mass, mass)
        self.assertAlmostEquals(stars[0].luminosity, 5820.85 | units.LSun, 0)
        instance.stop()
        del instance
    
    def slowtest4(self):
        print "Testing stellar type..."
        instance = self.new_instance(MESA)
        if instance is None:
            print "MESA was not built. Skipping test."
            return
        instance.initialize_module_with_default_parameters() 
        stars =  core.Stars(1)
        
        star = stars[0]
        star.mass = 5.0 | units.MSun
        
        instance.particles.add_particles(stars)
        instance.initialize_stars()
        
        from_code_to_model = instance.particles.new_channel_to(stars)
        from_code_to_model.copy()
        
        previous_type = 15 | units.stellar_type
        results = []
        current_time = 0 | units.Myr
        
        while current_time < (101 | units.Myr):
            if not star.stellar_type == previous_type:
                print (star.age, star.mass, star.stellar_type)
                results.append((star.age, star.mass, star.stellar_type))
                previous_type = star.stellar_type
            instance.evolve_model()
            from_code_to_model.copy()
            current_time = star.age
        
        self.assertEqual(len(results), 4)
        
        times = ( 
            0.0 | units.Myr, 
            81.6 | units.Myr, 
            99.9 | units.Myr, 
            100.3 | units.Myr
        )
        for result, expected in zip(results, times):
            self.assertAlmostEqual(result[0].value_in(units.Myr), expected.value_in(units.Myr), 1)
            
        masses = ( 
            5.000 | units.MSun, 
            5.000 | units.MSun, 
            5.000 | units.MSun, 
            5.000 | units.MSun
        )
        for result, expected in zip(results, masses):
            self.assertAlmostEqual(result[1].value_in(units.MSun), expected.value_in(units.MSun), 3)
         
        types = (
            "Main Sequence star",
            "First Giant Branch",
            "Core Helium Burning",
            "First Asymptotic Giant Branch"
        )
        
        for result, expected in zip(results, types):
            self.assertEquals(str(result[2]), expected)
        
        instance.stop()
        del instance
    
    def test5(self):
        print "Testing evolve_model for particle set..."
        #channel.MessageChannel.DEBUGGER = channel.MessageChannel.XTERM
        instance = self.new_instance(MESA)
        #channel.MessageChannel.DEBUGGER = None
        if instance is None:
            print "MESA was not built. Skipping test."
            return
        masses = [0.5, 1.0] | units.MSun
        max_age = 0.6 | units.Myr
        number_of_stars=len(masses)
        stars =  core.Stars(number_of_stars)
        for i, star in enumerate(stars):
            star.mass = masses[i]
        instance.initialize_module_with_default_parameters() 
        self.assertEqual(instance.parameters.max_age_stop_condition, 1e6 | units.Myr)
        instance.parameters.max_age_stop_condition = max_age
        self.assertEqual(instance.parameters.max_age_stop_condition, max_age)
        instance.setup_particles(stars)
        instance.initialize_stars()
        from_code_to_model = instance.particles.new_channel_to(stars)
        from_code_to_model.copy()
        instance.evolve_model(end_time = 0.5 | units.Myr)
        from_code_to_model.copy()
        #print stars
        for i in range(number_of_stars):
            self.assertTrue(stars[i].age.value_in(units.Myr) >= 0.5)
            self.assertTrue(stars[i].age <= max_age)
            self.assertTrue(stars[i].mass <= masses[i])
            self.assertTrue(stars[i].age+stars[i].time_step <= max_age)
        try:
            instance.evolve_model(end_time = 2*max_age)
            print 2*max_age
            print stars
            self.fail("Should not be able to evolve beyond maximum age.")
        except Exception as ex:
            self.assertEquals("Error when calling 'evolve' of a 'MESA', "
                "errorcode is -12, error is 'Evolve terminated: Maximum age reached.'", str(ex))
        instance.stop()
        del instance
    
    def test6(self):
        print "Test for obtaining the stellar structure model"
        stars = core.Particles(2)
        stars.mass = [1.0, 10.0] | units.MSun
        instance = self.new_instance(MESA)
        if instance is None:
            print "MESA was not built. Skipping test."
            return
        instance.initialize_module_with_current_parameters() 
        instance.setup_particles(stars)
        instance.initialize_stars()
        instance.evolve_model()
        self.assertEquals(instance.particles.get_number_of_zones(), [479, 985] | units.none)
        self.assertEquals(len(instance.particles[0].get_mass_profile()), 479)
        self.assertAlmostEquals(instance.particles[0].get_mass_profile().sum(), 1.0 | units.none)
        try:
            print instance.particles.get_mass_profile()
            self.fail("Should not be able to get profiles of more than one star at a time.")
        except Exception as ex:
            self.assertEquals("Querying mass profiles of more than one particle at a time is not supported.", str(ex))
        print instance.particles
        self.assertEquals(len(instance.particles[1].get_density_profile()), 985)
        self.assertIsOfOrder(instance.particles[0].get_radius_profile()[0],          1.0 | units.RSun)
        self.assertIsOfOrder(instance.particles[0].get_temperature_profile()[-1],  1.0e7 | units.K)
        self.assertIsOfOrder(instance.particles[0].get_luminosity_profile()[0],      1.0 | units.LSun)
        delta_mass = instance.particles[0].get_mass_profile() * instance.particles[0].mass
        radius1 = instance.particles[0].get_radius_profile()
        radius2 = radius1[1:]
        radius2.append(0|units.m)
        delta_radius_cubed = (radius1**3 - radius2**3)
        self.assertAlmostEquals(instance.particles[0].get_density_profile() / (delta_mass/(4./3.*pi*delta_radius_cubed)), [1]*479|units.none, places=3)
        instance.stop()
        del instance
    
    def test7(self):
        print "Test for obtaining the stellar composition structure"
        stars = core.Particles(1)
        stars.mass = 1.0 | units.MSun
        instance = self.new_instance(MESA)
        if instance is None:
            print "MESA was not built. Skipping test."
            return
        instance.initialize_module_with_current_parameters() 
        instance.setup_particles(stars)
        instance.initialize_stars()
        instance.evolve_model()
        number_of_zones   = instance.particles.get_number_of_zones().value_in(units.none)[0]
        number_of_species = instance.particles.get_number_of_species().value_in(units.none)[0]
        composition       = instance.particles[0].get_chemical_abundance_profiles()
        species_names     = instance.particles[0].get_names_of_species()
        species_IDs       = instance.particles[0].get_IDs_of_species()
        species_masses    = instance.particles[0].get_masses_of_species()
        self.assertEquals(number_of_zones,    479)
        self.assertEquals(number_of_species,    8)
        self.assertEquals(len(species_names),  number_of_species)
        self.assertEquals(len(composition),    number_of_species)
        self.assertEquals(len(composition[0]), number_of_zones)
        self.assertEquals(species_names, ['h1', 'he3', 'he4', 'c12', 'n14', 'o16', 'ne20', 'mg24'])
        self.assertEquals(species_IDs,   [2,    5,     6,     38,    51,    69,    114,    168])
        self.assertAlmostEquals(species_masses, [1.0078250, 3.0160293, 4.0026032, 12.0, 
                                14.0030740, 15.9949146, 19.9924401, 23.9850417] | units.amu, places=5)
        self.assertAlmostEquals(composition[ :1,0].sum(),  0.7 | units.none)
        self.assertAlmostEquals(composition[1:3,0].sum(),  (0.3 | units.none) - instance.parameters.metallicity)
        self.assertAlmostEquals(composition[3: ,0].sum(),  instance.parameters.metallicity)
        self.assertAlmostEquals(composition.sum(axis=0), [1.0]*number_of_zones | units.none)
        instance.stop()
        del instance
    
    def slowtest8(self):
        print "Test for obtaining the stellar composition structure - evolved star with zero metalicity"
        stars = core.Particles(1)
        stars.mass = 1.0 | units.MSun
        instance = self.new_instance(MESA)
        if instance is None:
            print "MESA was not built. Skipping test."
            return
        instance.parameters.metallicity = 0.0 | units.none
        instance.initialize_module_with_current_parameters() 
        instance.setup_particles(stars)
        instance.initialize_stars()
        instance.evolve_model(5.85 | units.Gyr)
        self.assertTrue(instance.particles[0].age >= 5.85 | units.Gyr)
        self.assertTrue(str(instance.particles[0].stellar_type) == "First Giant Branch")
        number_of_zones   = instance.particles.get_number_of_zones().value_in(units.none)[0]
        number_of_species = instance.particles.get_number_of_species().value_in(units.none)[0]
        composition       = instance.particles[0].get_chemical_abundance_profiles()
        species_names     = instance.particles[0].get_names_of_species()
        species_IDs       = instance.particles[0].get_IDs_of_species()
        self.assertEquals(number_of_zones,    578)
        self.assertEquals(number_of_species,    8)
        self.assertEquals(len(species_names),  number_of_species)
        self.assertEquals(len(composition),    number_of_species)
        self.assertEquals(len(composition[0]), number_of_zones)
        self.assertEquals(species_names, ['h1', 'he3', 'he4', 'c12', 'n14', 'o16', 'ne20', 'mg24'])
        self.assertEquals(species_IDs,   [2,    5,     6,     38,    51,    69,    114,    168])
        self.assertAlmostEquals(composition[ :1,0].sum(),  0.76 | units.none)
        self.assertAlmostEquals(composition[1:3,0].sum(),  0.24 | units.none)
        self.assertAlmostEquals(composition[3: ,0].sum(),  0.00 | units.none)
        self.assertAlmostEquals(composition.sum(axis=0), [1.0]*number_of_zones | units.none)
        self.assertAlmostEquals(composition[ :1,number_of_zones-1].sum(),  0.00 | units.none)
        self.assertAlmostEquals(composition[1:3,number_of_zones-1].sum(),  1.00 | units.none)
        self.assertAlmostEquals(composition[3: ,number_of_zones-1].sum(),  0.00 | units.none)
        instance.stop()
        del instance
