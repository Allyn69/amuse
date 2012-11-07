"""
Calculated theoretical pre-main-sequance evolutionary tracks for stars of various masses.
After Iben, ApJ 141, 993, 1965
"""

from matplotlib import pyplot
from amuse.plot import loglog, xlabel, ylabel, text

from amuse.units import units
from amuse.community.mesa.interface import MESA
from amuse import datamodel

def simulate_evolution_tracks(masses = [0.5, 1.0, 1.25, 1.5, 2.25, 3.0, 5.0, 9.0, 15.0] | units.MSun):
    stellar_evolution = MESA()
    stellar_evolution.parameters.AGB_wind_scheme = 0
    stellar_evolution.parameters.RGB_wind_scheme = 0

    stars = datamodel.Particles(len(masses), mass=masses)
    stars = stellar_evolution.pre_ms_stars.add_particles(stars)
    
    data={}
    
    for star in stars:
        luminosity = [] | units.LSun
        temperature = [] | units.K
        time = [] | units.yr
        
        print 'Evolving pre main sequence star with'
        print '    mass:', star.mass
        print '    luminosity:', star.luminosity
        print '    radius:', star.radius
        
        while star.stellar_type == 17 | units.stellar_type:
            luminosity.append(star.luminosity)
            temperature.append(star.temperature)
            time.append(star.age)
            star.evolve_one_step()
            
        print 'Evolved pre main sequence star to:', star.stellar_type
        print '    age:', star.age
        print '    mass:', star.mass
        print '    luminosity:', star.luminosity
        print '    radius:', star.radius
        print
        
        stardata = {}
        stardata['luminosity'] = luminosity
        stardata['temperature'] = temperature
        stardata['time'] = time
        data[star.mass] = stardata
        
    return data
    
def plot_track(data):
    pyplot.figure(figsize = (6, 8))
    pyplot.title('Hertzsprung-Russell diagram', fontsize=12)
    for mass,stardata in data.items():
        temperature=stardata['temperature']
        luminosity=stardata['luminosity']
        loglog(temperature[4:], luminosity[4:], marker="s") # first few points show transient
        text(1.25*temperature[-1], 0.5*luminosity[-1], mass)
    xlabel('Effective Temperature')
    ylabel('Luminosity')
    pyplot.xlim(10**4.6, 10**3.5)
    pyplot.ylim(1.0e-2,1.e5)
    pyplot.show()   
    
if __name__ in ('__main__', '__plot__'):
    data = simulate_evolution_tracks()
    plot_track(data)
    
