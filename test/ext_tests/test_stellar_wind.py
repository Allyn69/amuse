
from amuse.test import amusetest
from amuse.units import units, quantities
from amuse.datamodel.particles import Particles

from amuse.community.seba.interface import SeBa

from amuse.ext import stellar_wind


class TestStellarWind(amusetest.TestCase):

    def assertGreaterEqual(self, value, expected):
        self.assertTrue(value >= expected, "Expected {0} >= {1}".format(value, expected))

    def assertLessEqual(self, value, expected):
        self.assertTrue(value <= expected, "Expected {0} <= {1}".format(value, expected))

    def test1(self):
        """ Test the particles created for a simple wind """
        star = self.create_star()
        star_wind = stellar_wind.new_stellar_wind(1e-8|units.MSun)
        star_wind.particles.add_particles(star)

        star_wind.evolve_model(1|units.yr)
        wind = star_wind.create_wind_particles()

        self.assertEqual(len(wind), 100)
        min_dist = (wind.position - star.position).lengths().min()
        max_dist = (wind.position - star.position).lengths().max()
        self.assertGreaterEqual(min_dist, 2|units.RSun)
        self.assertLessEqual(max_dist, 24.7|units.RSun)
        plus_x_wind = wind[wind.x > star.x]
        minus_x_wind = wind[wind.x < star.x]
        plus_y_wind = wind[wind.y > star.y]
        minus_y_wind = wind[wind.y < star.y]
        plus_z_wind = wind[wind.z > star.z]
        minus_z_wind = wind[wind.z < star.z]
        self.assertGreaterEqual(minus_x_wind.vx.min(), -1500|units.ms)
        self.assertLessEqual(minus_x_wind.vx.max(), -1000|units.ms)
        self.assertGreaterEqual(plus_x_wind.vx.min(), -1000|units.ms)
        self.assertLessEqual(plus_x_wind.vx.max(), -500|units.ms)
        self.assertGreaterEqual(minus_y_wind.vy.min(), -500|units.ms)
        self.assertLessEqual(minus_y_wind.vy.max(), 0|units.ms)
        self.assertGreaterEqual(plus_y_wind.vy.min(), 0|units.ms)
        self.assertLessEqual(plus_y_wind.vy.max(), 500|units.ms)
        self.assertGreaterEqual(minus_z_wind.vz.min(), 500|units.ms)
        self.assertLessEqual(minus_z_wind.vz.max(), 1000|units.ms)
        self.assertGreaterEqual(plus_z_wind.vz.min(), 1000|units.ms)
        self.assertLessEqual(plus_z_wind.vz.max(), 1500|units.ms)

    def test2(self):
        """ Test the accelerating wind """
        star = self.create_star()
        star_wind = stellar_wind.new_stellar_wind(
                        3e-11|units.MSun,
                        mode="accelerate",
                        init_v_wind_ratio = 0.01,
                        r_min_ratio=1,
                        r_max_ratio=5
                        )
        star_wind.particles.add_particles(star)

        star_wind.evolve_model(1|units.day)
        wind = star_wind.create_wind_particles()

        self.assertEqual(len(wind), 91)
        min_dist = (wind.position - star.position).lengths().min()
        max_dist = (wind.position - star.position).lengths().max()
        self.assertGreaterEqual(min_dist, 2|units.RSun)
        self.assertLessEqual(max_dist, 2.8|units.RSun)

    def test3(self):
        """ Test the wind acceleration """
        star = self.create_star()
        star.position = [1, 1, 1] | units.RSun
        star_wind = stellar_wind.new_stellar_wind(
                        3e-11|units.MSun,
                        mode="accelerate",
                        init_v_wind_ratio = 0.01,
                        r_min_ratio=1.5,
                        r_max_ratio=5
                        )
        star_wind.particles.add_particles(star)

        # unaffected points
        points = [[1,1,1], [1,1,0], [1,4,1], [12,1,1]]|units.RSun
        x, y, z = points.transpose()
        ax, ay, az = star_wind.get_gravity_at_point(1, x, y, z)
        zeros = [0,0,0,0]|units.m/units.s**2
        self.assertEqual(ax, zeros)
        self.assertEqual(ay, zeros)
        self.assertEqual(az, zeros)

        # affected points
        points = [[5.1,1,1], [1,1,5.1], [1,7,1], [1,7,8], [-8,1,1]]|units.RSun
        x, y, z = points.transpose()
        ax, ay, az = star_wind.get_gravity_at_point(1, x, y, z)
        a = quantities.as_vector_quantity([ax, ay, az]).transpose()
        self.assertAlmostEquals(a[0], [32.64354, 0, 0]|units.m/units.s**2, places=4)
        self.assertAlmostEquals(a[1], [0, 0, 32.64354]|units.m/units.s**2, places=4)
        self.assertAlmostEquals(a[2], [0, 15.24272, 0]|units.m/units.s**2, places=4)
        self.assertAlmostEquals(a[3], [0, 4.20134, 4.90156]|units.m/units.s**2, places=4)
        self.assertAlmostEquals(a[4], [-6.77454, 0, 0]|units.m/units.s**2, places=4)

    def test4(self):
        """ Test the transfer to a target gas particle set """
        star = self.create_star()
        gas = Particles()
        star_wind = stellar_wind.new_stellar_wind(1e-8|units.MSun, target_gas=gas, timestep=1|units.day)
        star_wind.particles.add_particles(star)

        star_wind.evolve_model(1|units.yr)
        self.assertEqual(len(gas), 99)

        star_wind.evolve_model(1.5|units.yr)
        self.assertEqual(len(gas), 149)

    def test5(self):
        """ Test adding an additional star later """
        star1 = self.create_star()
        gas = Particles()
        star_wind = stellar_wind.new_stellar_wind(1e-8|units.MSun, target_gas=gas, timestep=1|units.day)
        star_wind.particles.add_particles(star1)

        star_wind.evolve_model(1|units.yr)
        self.assertEqual(len(gas), 99)

        star2 = self.create_star()[0]
        star2.x = 50 | units.parsec
        star_wind.particles.add_particle(star2)

        star_wind.evolve_model(1.5|units.yr)
        self.assertEqual(len(gas), 198)
        star1_gas = gas[gas.x < 25|units.parsec]
        star2_gas = gas - star1_gas
        self.assertEqual(len(star1_gas), 149)
        self.assertEqual(len(star2_gas), 49)

    def test6(self):
        """ Test deriving wind from stellar evolution """
        stars = self.create_stars_without_wind_attributes()
        star_wind = stellar_wind.new_stellar_wind(1e-8|units.MSun, derive_from_evolution=True)



    def test7(self):
        """ Test deriving static wind from stellar evolution """
        stars = Particles(mass=[1,2]|units.MSun)
        star_wind = stellar_wind.new_stellar_wind(1e-8|units.MSun, derive_from_evolution=True)
        stev = SeBa()
        stev.particles.add_particles(stars)

        stellar_wind.static_wind_from_stellar_evolution(star_wind, stev,
                1.49|units.Gyr, 1.495|units.Gyr)

        self.assertAlmostRelativeEquals(star_wind.particles.wind_mass_loss_rate,
                                        [0., 2.43765e-8]|units.MSun/units.yr, places=5)

        self.assertAlmostRelativeEquals(star_wind.particles.terminal_wind_velocity,
                                        [646317., 50921.7]|units.ms, places=5)

    def create_star(self):
        star = Particles(1)
        star.mass = 2|units.MSun
        star.radius = 2|units.RSun
        star.temperature = 5000|units.K
        star.position = [1, 1, 1] | units.parsec
        star.velocity = [-1000, 0, 1000] | units.ms
        star.wind_mass_loss_rate = 1e-6 | units.MSun / units.yr
        star.terminal_wind_velocity = 500 | units.ms
        return star

    def create_stars_without_wind_attributes(self):
        stars = Particles(2)
        stars.mass = 2|units.MSun
        stars.radius = 2|units.RSun
        stars.temperature = 5000|units.K
        stars.luminosity = 2 | units.LSun
        stars.age = 0|units.Myr
        stars[0].position = [1, 1, 1] | units.parsec
        stars[1].position = [-1, -1, -1] | units.parsec
        stars[0].velocity = [-1000, 0, 1000] | units.ms
        stars[1].velocity = [0, 0, 0] | units.ms

        return stars

