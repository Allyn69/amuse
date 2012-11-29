"""
   Minimalistic routine for running a stellar evolution code
"""
from amuse.lab import *
    
def main(M=1.0|units.MSun, z=0.02, model_time=4700|units.Myr):

    stellar = MESA()
    stellar.parameters.metallicity = z
    stellar.particles.add_particle(Particle(mass=M))
    stellar.commit_particles()

    L_init = stellar.particles.luminosity
    dt = 1 | units.Myr
    time = 0 | units.Myr
    while stellar.particles[0].age<model_time:
        time+=dt
        stellar.evolve_model(time)

    L_final = stellar.particles.luminosity
    print "L(t=0)=", L_init, ", L (t=", stellar.particles.age, ")=", \
        L_final, stellar.particles.radius
    stellar.stop()
    
def new_option_parser():
    from amuse.units.optparse import OptionParser
    result = OptionParser()
    result.add_option("-M", unit= units.MSun,
                      dest="M", type="float",default = 1.0 | units.MSun,
                      help="stellar mass [1.0] %unit")
    result.add_option("-t", unit = units.Myr,
                      dest="model_time", type="float", 
                      default = 4700.0|units.Myr,
                      help="end time of the simulation [4.7] %unit")
    result.add_option("-z", dest="z", type="float", default = 0.02,
                      help="metalicity [0.02]")
    return result

if __name__ in ('__main__', '__plot__'):
    o, arguments  = new_option_parser().parse_args()
    main(**o.__dict__)
