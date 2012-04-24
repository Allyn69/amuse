import numpy
from amuse.community import *
from amuse.test.amusetest import TestWithMPI

from .interface import MikkolaInterface
from .interface import Mikkola

class MikkolaInterfaceTests(TestWithMPI):
    
    def xtest0(self):
        instance = MikkolaInterface()
    
    def test1(self):
#        instance = MikkolaInterface(debugger="ddd")
        instance = MikkolaInterface(debugger="xterm")
#        instance = MikkolaInterface()
        instance.initialize_code()
        instance.commit_parameters()

        res1 = instance.new_particle(mass = 1.0, radius = 0, x = 0.0, y = 0.0, z = 0.0, vx = 0.0, vy = 0.0, vz = 0.0)
        res2 = instance.new_particle(mass = 0.001, radius = 0, x = 1.0, y = 0.0, z = 0.0, vx = 0.0, vy = 1.0, vz = 0.0)
        
        self.assertEquals(1, res1['index_of_the_particle'])
        self.assertEquals(2, res2['index_of_the_particle'])
    
        retrieved_state1 = instance.get_state(1)
        retrieved_state2 = instance.get_state(2)
    
        end_time = 10.0 
        instance.evolve(end_time)
        instance.cleanup_code()
        del instance
# run with: 
# %>nosetests -v test_mikkola.py:TestMikkola.test1
class TestMikkola(TestWithMPI):
    def new_system_of_sun_and_earth(self):
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
        
        return stars

    def test1(self):
        instance = Mikkola()
        stars = self.new_system_of_sun_and_earth()
        instance.particles.add_particles(stars)
        Sun = stars[0]
        earth = stars[1]
        
        postion_at_start = earth.position.value_in(units.AU)[0]
        
#        instance.evolve_model(365.0 | units.day)
        instance.evolve_model(1.0 | units.yr)
        instance.particles.copy_values_of_state_attributes_to(stars)
        
        postion_after_full_rotation = earth.position.value_in(units.AU)[0]
       
        self.assertAlmostEqual(postion_at_start, postion_after_full_rotation, 4)
        
        instance.evolve_model(1.5 | units.yr)
        
        instance.particles.copy_values_of_state_attributes_to(stars)
        
        postion_after_half_a_rotation = earth.position.value_in(units.AU)[0]
        self.assertAlmostEqual(-postion_at_start, postion_after_half_a_rotation, 3)
        
        instance.evolve_model(1.75  | units.yr)
         
        instance.particles.copy_values_of_state_attributes_to(stars)
        
        postion_after_half_a_rotation = earth.position.value_in(units.AU)[1]
        
        self.assertAlmostEqual(-postion_at_start, postion_after_half_a_rotation, 3)
        instance.cleanup_code()
        del instance

# run with: 
# %>nosetests -v test_mikkola.py:TestMikkola.test1
    def new_system_of_sun_and_mercury(self):
        stars = core.Stars(2)
        sun = stars[0]
        sun.mass = units.MSun(1.0)
        sun.position = units.m(numpy.array((0.0,0.0,0.0)))
        sun.velocity = units.ms(numpy.array((0.0,0.0,0.0)))
        sun.radius = units.RSun(1.0)

        mercury = stars[1]
        mercury.mass = 3.3022e23 | units.kg
        mercury.radius = 0 | units.RSun
        mercury.position = [0.387098, 0, 0] | units.AU
        mercury.velocity = [0.0, 47.87, 0.0] | units.km/units.s
        return stars

    def test2(self):
        instance = Mikkola()
        stars = self.new_system_of_sun_and_mercury()
        instance.particles.add_particles(stars)
        Sun = stars[0]
        mercury = stars[1]
        
        postion_at_start = mercury.position.value_in(units.AU)[0]
        
        period_mercury = 87.9691 | units.day
        instance.evolve_model(period_mercury)
        instance.particles.copy_values_of_state_attributes_to(stars)
        
        postion_after_full_rotation = mercury.position.value_in(units.AU)[0]
       
        self.assertAlmostEqual(postion_at_start, postion_after_full_rotation, 4)
        
        instance.evolve_model(1.5 * period_mercury)
        
        instance.particles.copy_values_of_state_attributes_to(stars)
        
        postion_after_half_a_rotation = mercury.position.value_in(units.AU)[0]
        self.assertAlmostEqual(-postion_at_start, postion_after_half_a_rotation, 3)
        
        instance.evolve_model(1.75 *period_mercury)
         
        instance.particles.copy_values_of_state_attributes_to(stars)
        
        postion_after_half_a_rotation = mercury.position.value_in(units.AU)[1]
        
        self.assertAlmostEqual(-postion_at_start, postion_after_half_a_rotation, 3)
        instance.cleanup_code()
        del instance

# run with: 
# %>nosetests -v test_mikkola.py:TestMikkola.test3
    def new_system_of_Hulse_Taylor_pulsar(self):
        stars = core.Stars(2)
        Hulse = stars[0]
        Hulse.mass = 1.441 | units.MSun
        Hulse.radius = 1.4e-5 | units.RSun
#        Hulse.position = [-1576800.0, 0, 0] | units.km
#        Hulse.velocity = [0.0, -55.0, 0.0] | units.km/units.s
        Hulse.position = [-1546691.3719943422, 0, 0] | units.km
        Hulse.velocity = [0.0, -110.0, 0.0] | units.km/units.s

        Taylor = stars[1]
        Taylor.mass = 1.387 | units.MSun
        Taylor.radius = 1.4e-5 | units.RSun
        Taylor.position = [1606908.6280056578, 0, 0] | units.km
        Taylor.velocity = [0.0, 114.28262436914201, 0.0] | units.km/units.s
#        Taylor.position = [1576800.0, 0, 0] | units.km
#        Taylor.velocity = [0.0, 55.0, 0.0] | units.km/units.s
        return stars

    def test3(self):
        instance = Mikkola()
        stars = self.new_system_of_Hulse_Taylor_pulsar()
        instance.particles.add_particles(stars)
        Hulse = stars[0]
        Taylor = stars[1]
        
        postion_at_start = Taylor.position.value_in(units.AU)[0]
        
        #orbital period
        #period_HTpulsar = 7.751939106 | units.hour
        #period_HTpulsar = 77.51939106 | units.hour
        # period for abseidal motion
#        period_HTpulsar = 85.0 | units.yr #4.2degrees/year
        period_HTpulsar = 1.0 | units.yr 
        instance.evolve_model(period_HTpulsar)
        instance.particles.copy_values_of_state_attributes_to(stars)

        postion_after_full_rotation = Taylor.position.value_in(units.AU)[0]
       
        self.assertAlmostEqual(postion_at_start, postion_after_full_rotation, 4)
        
        instance.evolve_model(1.5 * period_HTpulsar)
        
        instance.particles.copy_values_of_state_attributes_to(stars)
        
        postion_after_half_a_rotation = Taylor.position.value_in(units.AU)[0]
        self.assertAlmostEqual(-postion_at_start, postion_after_half_a_rotation, 3)
        
        instance.evolve_model(1.75 * period_HTpulsar)
         
        instance.particles.copy_values_of_state_attributes_to(stars)
        
        postion_after_half_a_rotation = Taylor.position.value_in(units.AU)[1]
        
        self.assertAlmostEqual(-postion_at_start, postion_after_half_a_rotation, 3)
        instance.cleanup_code()
        del instance
