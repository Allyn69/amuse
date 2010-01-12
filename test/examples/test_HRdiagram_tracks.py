import sys
import numpy 
import os

try:
    from matplotlib import pyplot
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

from amuse.support.units import units
from amuse.support.data import core
from amuse.legacy.sse.muse_stellar_mpi import SSE
from amuse.legacy.evtwin.interface import EVtwin
from amuse.legacy.support.core import is_mpd_running

def simulate_evolution_tracks(masses = [.5, 1., 2., 5., 10., 20., 30.] | units.MSun, name_of_the_figure = "HR_evolution_tracks.png"):
    """
    For every mass in the `masses' array, a stellar evolution track across the Hertzsprung-Russell
    diagram will be calculated and plotted. Each star will be created, evolved and removed one by 
    one. This is only necessary because the time span of each track is different (a solar mass star
    evolution track takes billions of years, but we don't want to also evolve high mass stars for 
    billions of years) In most applications the stars have to be evolved up to a common end time,
    which can be more easily accomplished by creating an array (stars = core.Stars(number_of_stars))
    and using evolve_model(end_time = ...).
    """
    number_of_stars=len(masses)
    if number_of_stars < 1:
        print "No tracks to simulate. Set 'masses' of stars to be simulated, or use the default value."
        return
    
    Stefan_Boltzmann_constant = 5.670400e-8 | units.J * units.s**-1 * units.m**-2 * units.K**-4

    print "The evolution across the Hertzsprung-Russell diagram of ", str(number_of_stars), \
        " stars with\nvarying masses will be simulated..."
        
#   Declare lists that will collect data of each simulated star
    all_tracks_lumi = []     # luminosity track of each star
    all_tracks_Teff = []     # temperature track of each star
    all_props_at_switch = [] # properties stored each time star switches to new evolutionary phase
    
#   Initialize the stellar evolution code
    stellar_evolution = SSE()
    stellar_evolution.initialize_module_with_default_parameters() 

#   Simulate evolution of stars with mass=`masses', one by one:
    for j in range(number_of_stars):
#       Create an "array" of one star
        stars = core.Stars(1)
        star=stars[0]
        star.mass = masses[j]
        star.radius = 0.0 | units.RSun
#       Initialize the stars
        stellar_evolution.setup_particles(stars)
        stellar_evolution.initialize_stars()
        from_code_to_model = stellar_evolution.particles.new_channel_to(stars)
        from_code_to_model.copy()
    
        print star
                    
#       Lists to monitor changes of the star with time:
        luminosity_at_time = []
        Teff_at_time       = []
        
#       Remember initial properties of the star
        current_Teff = ((star.luminosity/(4*numpy.pi*Stefan_Boltzmann_constant*star.radius**2))**.25).in_(units.K)
        properties_at_switch_state = [(star.age.value_in(units.Myr), star.luminosity.value_in(units.LSun), \
                    current_Teff.value_in(units.K), star.type.value_in(units.stellar_type))]
        previous_type = star.type
        
#       Evolve this star until it changes into a compact stellar remnant (white dwarf, neutron star, or black hole)
        while star.type.value_in(units.stellar_type) < 10:
#           Store current values of luminosity and effective temperature
            luminosity_at_time.append(star.luminosity.value_in(units.LSun))
            current_Teff = ((star.luminosity/(4*numpy.pi*Stefan_Boltzmann_constant*star.radius**2))**.25).in_(units.K)
            Teff_at_time.append(current_Teff.value_in(units.K))

#           Store some more details whenever the star switches state:
            if not star.type == previous_type:
                properties_at_switch_state.append((star.age.value_in(units.Myr), star.luminosity.value_in(units.LSun), \
                    current_Teff.value_in(units.K), star.type.value_in(units.stellar_type)))
                previous_type = star.type
            
            current_age=star.age
            stellar_evolution.evolve_model()
            from_code_to_model.copy()
            if star.age == current_age:
                print "Age did not increase during timestep. Stop evolving..."
                print star
                break

        print " ... evolved model to t = " + str(star.age)
        print "Star has now become a: ", star.type, "(stellar_type: "+str(star.type.value_in(units.stellar_type))+")"
        print
        
#       An obscure but elegant way to transpose the list of tuples:
        transpose = map(list, zip(*properties_at_switch_state))
#       Save the relevant data of this star to produce a plot later on, before simulating the next star:
        all_props_at_switch.append(transpose)
        all_tracks_lumi.append(luminosity_at_time)
        all_tracks_Teff.append(Teff_at_time)
        
#       Remove the star before creating the next one. See comments at the top.
        stellar_evolution.particles.remove_particles(stars)

    del stellar_evolution
        
    if HAS_MATPLOTLIB:
        print "Plotting the data..."
        pyplot.figure(figsize = (7, 8))
        pyplot.suptitle('Hertzsprung-Russell diagram', fontsize=16)
        pyplot.title('Evolutionary tracks were simulated using the SSE package\n(Hurley J.R., Pols O.R., Tout C.A., 2000, MNRAS, 315, 543)', \
            fontsize=12)
        pyplot.xlabel('Effective Temperature (K)')
        pyplot.ylabel('Luminosity (solar luminosity)')
        plot_format_strings=["r-","r-","y-","y-","c-","c-","b-"]
        plot_format_strings_2=["r^","rs","y^","ys","c^","cs","b^"]
        for j in range(number_of_stars):
            x_values = all_tracks_Teff[j]
            y_values = all_tracks_lumi[j]
            pyplot.loglog(x_values, y_values, plot_format_strings[j])
            x_values = all_props_at_switch[j][2]
            y_values = all_props_at_switch[j][1]
            pyplot.loglog(x_values, y_values, plot_format_strings_2[j])
            T_offset_factor=1.05
            lum_offset_factor=0.6
            for i, phase in enumerate(all_props_at_switch[j][3]):
                pyplot.annotate(str(int(phase)), xy=(x_values[i],y_values[i]), \
                    xytext=(x_values[i]*T_offset_factor,y_values[i]*lum_offset_factor))
            T_offset_factor=1.1
            lum_offset_factor=0.9
            pyplot.annotate(str(masses[j]),xy=(x_values[0],y_values[0]), \
                xytext=(x_values[0]*T_offset_factor,y_values[0]*lum_offset_factor), \
                color='g', horizontalalignment='right')
                
        print
        print "Meaning of the stellar evolution phase markers (black numbers):"
        for i in range(16):
            print str(i)+": ", (i | units.stellar_type)
            
        pyplot.axis([300000., 2500., 1.e-2, 1.e6])
#       Or use these axes to also view neutron stars and black holes:
#        pyplot.axis([1.e7, 2500., 1.e-11, 1.e6])

        pyplot.savefig(name_of_the_figure)
        
    print "All done!"
        
        
        
def test_simulate_one_star():
    assert is_mpd_running()
    simulate_evolution_tracks([5.0] | units.MSun)
    
if __name__ == '__main__':
    simulate_evolution_tracks(name_of_the_figure = sys.argv[1])
