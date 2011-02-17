from amuse.community import *

from amuse.support.units import units
from amuse.support.data.values import Quantity
from amuse.support.data.core import Particles, ParticlesSubset

class BSEInterface(CodeInterface, LiteratureRefs): 
    """
    Binary evolution is performed by the **rapid** binary-star evolution (BSE) 
    algorithm. Circularization of eccentric orbits and synchronization of stellar 
    rotation with the orbital motion owing to tidal interaction is modelled in detail. 
    Angular momentum loss mechanisms, such as gravitational radiation and magnetic 
    braking, are also modelled. Wind accretion, where the secondary may accrete some 
    of the material lost from the primary in a wind, is allowed with the necessary 
    adjustments made to the orbital parameters in the event of any mass variations. 
    Mass transfer also occurs if either star fills its Roche lobe and may proceed on a 
    nuclear, thermal or dynamical time-scale. In the latter regime, the radius of the 
    primary increases in response to mass-loss at a faster rate than the Roche-lobe of 
    the star. Stars with deep surface convection zones and degenerate stars are 
    unstable to such dynamical time-scale mass loss unless the mass ratio of the system 
    is less than some critical value. The outcome is a common-envelope event if the 
    primary is a giant star. This results in merging or formation of a close binary, or 
    a direct merging if the primary is a white dwarf or low-mass main-sequence star. On 
    the other hand, mass transfer on a nuclear or thermal time-scale is assumed to be a 
    steady process. Prescriptions to determine the type and rate of mass transfer, the 
    response of the secondary to accretion and the outcome of any merger events are in 
    place in BSE and the details can be found in the BSE paper:
    
        .. [#] Hurley J.R., Tout C.A., & Pols O.R., 2002, MNRAS, 329, 897:
        .. [#] ... Evolution of binary stars and the effect of tides on binary populations
        .. [#] Hurley J.R., Pols O.R., Tout C.A., 2000, MNRAS, 315, 543:
        .. [#] ... Comprehensive analytic formulae for stellar evolution as a function of mass and metallicity
    """
    def __init__(self, **options):
        CodeInterface.__init__(self, name_of_the_worker="bse_worker", **options)
        LiteratureRefs.__init__(self)

    @legacy_function   
    def initialize():
        function = LegacyFunctionSpecification()  
        function.addParameter('z_in', dtype='d', direction=function.IN)
        function.addParameter('neta_in', dtype='d', direction=function.IN)
        function.addParameter('bwind_in', dtype='d', direction=function.IN)
        function.addParameter('hewind_in', dtype='d', direction=function.IN)
        function.addParameter('alpha1_in', dtype='d', direction=function.IN)
        function.addParameter('CElambda_in', dtype='d', direction=function.IN)
        function.addParameter('ceflag_in', dtype='i', direction=function.IN)
        function.addParameter('tflag_in', dtype='i', direction=function.IN)
        function.addParameter('ifflag_in', dtype='i', direction=function.IN)
        function.addParameter('wdflag_in', dtype='i', direction=function.IN)
        function.addParameter('bhflag_in', dtype='i', direction=function.IN)
        function.addParameter('nsflag_in', dtype='i', direction=function.IN)
        function.addParameter('mxns_in', dtype='d', direction=function.IN)
        function.addParameter('idum_in', dtype='i', direction=function.IN)
        function.addParameter('pts1_in', dtype='d', direction=function.IN)
        function.addParameter('pts2_in', dtype='d', direction=function.IN)
        function.addParameter('pts3_in', dtype='d', direction=function.IN)
        function.addParameter('sigma_in', dtype='d', direction=function.IN)
        function.addParameter('beta_in', dtype='d', direction=function.IN)
        function.addParameter('xi_in', dtype='d', direction=function.IN)
        function.addParameter('acc2_in', dtype='d', direction=function.IN)
        function.addParameter('epsnov_in', dtype='d', direction=function.IN)
        function.addParameter('eddfac_in', dtype='d', direction=function.IN)
        function.addParameter('gamma_in', dtype='d', direction=function.IN)
        function.addParameter('status', dtype='i', direction=function.OUT)
        return function
        
    @legacy_function     
    def evolve():
        function = LegacyFunctionSpecification()  
        function.name = 'evolve_binary'
        function.can_handle_array = True 
        function.addParameter('type1', dtype='i', direction=function.INOUT)
        function.addParameter('type2', dtype='i', direction=function.INOUT)
        function.addParameter('initial_mass1', dtype='d', direction=function.INOUT)
        function.addParameter('initial_mass2', dtype='d', direction=function.INOUT)
        function.addParameter('mass1', dtype='d', direction=function.INOUT)
        function.addParameter('mass2', dtype='d', direction=function.INOUT)
        function.addParameter('radius1', dtype='d', direction=function.INOUT)
        function.addParameter('radius2', dtype='d', direction=function.INOUT)
        function.addParameter('luminosity1', dtype='d', direction=function.INOUT)
        function.addParameter('luminosity2', dtype='d', direction=function.INOUT)
        function.addParameter('core_mass1', dtype='d', direction=function.INOUT)
        function.addParameter('core_mass2', dtype='d', direction=function.INOUT)
        function.addParameter('core_radius1', dtype='d', direction=function.INOUT)
        function.addParameter('core_radius2', dtype='d', direction=function.INOUT)
        function.addParameter('envelope_mass1', dtype='d', direction=function.INOUT)
        function.addParameter('envelope_mass2', dtype='d', direction=function.INOUT)
        function.addParameter('envelope_radius1', dtype='d', direction=function.INOUT)
        function.addParameter('envelope_radius2', dtype='d', direction=function.INOUT)
        function.addParameter('spin1', dtype='d', direction=function.INOUT)
        function.addParameter('spin2', dtype='d', direction=function.INOUT)
        function.addParameter('epoch1', dtype='d', direction=function.INOUT)
        function.addParameter('epoch2', dtype='d', direction=function.INOUT)
        function.addParameter('MS_lifetime1', dtype='d', direction=function.INOUT)
        function.addParameter('MS_lifetime2', dtype='d', direction=function.INOUT)
        function.addParameter('age', dtype='d', direction=function.INOUT)
        function.addParameter('orbital_period', dtype='d', direction=function.INOUT)
        function.addParameter('eccentricity', dtype='d', direction=function.INOUT)
        function.addParameter('end_time', dtype='d', direction=function.INOUT)
        return function
        
    @legacy_function      
    def get_time_step():
        function = LegacyFunctionSpecification() 
        function.can_handle_array = True
        function.addParameter('type1', dtype='i', direction=function.IN)
        function.addParameter('type2', dtype='i', direction=function.IN)
        function.addParameter('initial_mass1', dtype='d', direction=function.IN)
        function.addParameter('initial_mass2', dtype='d', direction=function.IN)
        function.addParameter('mass1', dtype='d', direction=function.IN)
        function.addParameter('mass2', dtype='d', direction=function.IN)
        function.addParameter('MS_lifetime1', dtype='d', direction=function.IN)
        function.addParameter('MS_lifetime2', dtype='d', direction=function.IN)
        function.addParameter('epoch1', dtype='d', direction=function.IN)
        function.addParameter('epoch2', dtype='d', direction=function.IN)
        function.addParameter('age', dtype='d', direction=function.IN)
        function.addParameter('time_step', dtype='d', direction=function.OUT)
        return function
        
    def get_time_step_for_binary(self, binary):
        
        current_values = {}
        current_values['type1'] = binary.type1.value_in(units.stellar_type)
        current_values['type2'] = binary.type2.value_in(units.stellar_type)
        current_values['initial_mass1'] = binary.initial_mass1.value_in(units.MSun)
        current_values['initial_mass2'] = binary.initial_mass2.value_in(units.MSun)
        current_values['mass1'] = binary.mass1.value_in(units.MSun)
        current_values['mass2'] = binary.mass2.value_in(units.MSun)
        current_values['MS_lifetime1'] = binary.MS_lifetime1.value_in(units.Myr)
        current_values['MS_lifetime2'] = binary.MS_lifetime2.value_in(units.Myr)
        current_values['epoch1'] = binary.epoch1.value_in(units.Myr)
        current_values['epoch2'] = binary.epoch2.value_in(units.Myr)
        current_values['age'] = binary.age.value_in(units.Myr)
        
        result = self.get_time_step(**current_values)
        
        return result | units.Myr
        
        
    def evolve_particle(self, particle, time_end):
        t = particle.current_time
        if particle.type.value_in(units.none) == 15:
            return
        while t < time_end:
            t0 = t
            t  = t0 + self.get_time_step_for_binary(particle)
            if t > time_end:
                t = time_end
            self.evolve_star(particle, t)
            t1 = particle.current_time
            dt = t1 - t0
            t0 = t1
            if dt.value_in(units.Myr) == 0.0:
                print t, t0, t1, dt, "BREAK BREAK BREAK!"
                return
            if particle.type.value_in(units.none) == 15:
                return
    
        
class BSEParticles(Particles):
    
    def __init__(self, code_interface, storage = None):
        Particles.__init__(self, storage = storage)
        self._private.code_interface = code_interface 
        
    def _add_particles(self, keys, attributes = [], values = []):
        if len(keys) == 0:
            return
            
        all_attributes = []
        all_attributes.extend(attributes)
        all_values = []
        all_values.extend(values)
        
        mapping_from_attribute_to_default_value = {
            "type1" : 1 | units.stellar_type,
            "type2" : 1 | units.stellar_type,
            "radius1":  0 | units.RSun,
            "radius2":  0 | units.RSun,
            "luminosity1":  0 | units.LSun,
            "luminosity2":  0 | units.LSun,
            "core_mass1": 0 | units.MSun,
            "core_mass2": 0 | units.MSun,
            "core_radius1": 0 | units.RSun,
            "core_radius2": 0 | units.RSun,
            "envelope_mass1": 0 | units.MSun,
            "envelope_mass2": 0 | units.MSun,
            "envelope_radius1": 0 | units.RSun,
            "envelope_radius2": 0 | units.RSun,
            "epoch1": 0 | units.Myr,
            "epoch2": 0 | units.Myr,
            "spin1": 0 | units.none,
            "spin2": 0 | units.none,
            "MS_lifetime1": 0 | units.Myr,
            "MS_lifetime2": 0 | units.Myr,
#            "orbital_period": 200.0 | units.day,
            "eccentricity": 0.0 | units.none,
            "age": 0 | units.Myr
        }
        
        given_attributes = set(attributes)
        
        if not "initial_mass1" in given_attributes:
            index_of_mass_attibute = attributes.index("mass1")
            all_attributes.append("initial_mass1")
            all_values.append(values[index_of_mass_attibute] * 1.0)
        if not "initial_mass2" in given_attributes:
            index_of_mass_attibute = attributes.index("mass2")
            all_attributes.append("initial_mass2")
            all_values.append(values[index_of_mass_attibute] * 1.0)
        
        for attribute, default_value in mapping_from_attribute_to_default_value.iteritems():
            if not attribute in given_attributes:
                all_attributes.append(attribute)
                all_values.append(default_value.as_vector_with_length(len(keys)))
        
        super(BSEParticles, self)._add_particles(keys, all_attributes, all_values)
        
        added_particles = ParticlesSubset(self, keys)

        self._private.code_interface._evolve_particles(added_particles, 1e-06 | units.Myr)
        
    def _state_attributes(self):
        return ["mass1", "mass2", "radius1", "radius2"]
    
class BSE(InCodeComponentImplementation):
    
    def __init__(self, **options):
        InCodeComponentImplementation.__init__(self, BSEInterface(**options), **options)

        self.parameters.set_defaults()
        
    
    def define_parameters(self, object):
    
        object.add_caching_parameter(
            "initialize",
            "z_in",
            "metallicity",
            "Metallicity of all stars",
            units.none,
            0.02 | units.none
        )
                
        object.add_caching_parameter(
            "initialize",
            "neta_in",
            "reimers_mass_loss_coefficient",
            "Reimers mass-loss coefficient (neta*4x10^-13; 0.5 normally)",
            units.none,
            0.5 | units.none
        )
        
        object.add_caching_parameter(
            "initialize",
            "bwind_in",
            "binary_enhanced_mass_loss_parameter",
            "The binary enhanced mass loss parameter (inactive for single).",
            units.none,
            0.0 | units.none
        )
        
        object.add_caching_parameter(
            "initialize",
            "hewind_in",
            "helium_star_mass_loss_factor",
            "Helium star mass loss factor",
            units.none,
            1.0 | units.none
        )
        
        object.add_caching_parameter(
            "initialize",
            "alpha1_in",
            "common_envelope_efficiency",
            "The common-envelope efficiency parameter",
            units.none,
            1.0 | units.none
        )
        
        object.add_caching_parameter(
            "initialize",
            "CElambda_in",
            "common_envelope_binding_energy_factor",
            "The binding energy factor for common envelope evolution",
            units.none,
            0.5 | units.none
        )
        
        object.add_caching_parameter(
            "initialize",
            "ceflag_in",
            "common_envelope_model_flag", 
            "ceflag > 0 activates spin-energy correction in common-envelope. ceflag = 3 activates de Kool common-envelope model (0).",
            units.none, 
            0 | units.none
        )
        
        object.add_caching_parameter(
            "initialize",
            "tflag_in",
            "tidal_circularisation_flag", 
            "tflag > 0 activates tidal circularisation (1).",
            units.none, 
            1 | units.none
        )
        
        object.add_caching_parameter(
            "initialize",
            "ifflag_in",
            "white_dwarf_IFMR_flag", 
            "ifflag > 0 uses white dwarf IFMR (initial-final mass relation) of HPE, 1995, MNRAS, 272, 800 (0).",
            units.none, 
            0 | units.none
        )
        
        object.add_caching_parameter(
            "initialize",
            "wdflag_in",
            "white_dwarf_cooling_flag", 
            "wdflag > 0 uses modified-Mestel cooling for WDs (0).",
            units.none, 
            1 | units.none
        )
        
        object.add_caching_parameter(
            "initialize",
            "bhflag_in",
            "black_hole_kick_flag",
            "bhflag > 0 allows velocity kick at BH formation (0).",
            units.none,
            0 | units.none
        )
        
        object.add_caching_parameter(
            "initialize",
            "nsflag_in",
            "neutron_star_mass_flag",
            "nsflag > 0 takes NS/BH mass from Belczynski et al. 2002, ApJ, 572, 407 (1).",
            units.none,
            1 | units.none
        )
        
        object.add_caching_parameter(
            "initialize",
            "mxns_in",
            "maximum_neutron_star_mass",
            "The maximum neutron star mass (1.8, nsflag=0; 3.0, nsflag=1).",
            units.MSun,
            3.0 | units.MSun
        )
        
        object.add_caching_parameter(
            "initialize",
            "idum_in",
            "SN_kick_random_seed", 
            "The random number seed used in the kick routine.",
            units.none, 
            29769 | units.none
        )
        
        object.add_caching_parameter(
            "initialize",
            "pts1_in",
            "fractional_time_step_1", 
            "The timesteps chosen in each evolution phase as decimal fractions of the time taken in that phase: MS (0.05)",
            units.none, 
            0.05 | units.none
        )
        
        object.add_caching_parameter(
            "initialize",
            "pts2_in",
            "fractional_time_step_2", 
            "The timesteps chosen in each evolution phase as decimal fractions of the time taken in that phase: GB, CHeB, AGB, HeGB (0.01)",
            units.none, 
            0.01 | units.none
        )
        
        object.add_caching_parameter(
            "initialize",
            "pts3_in",
            "fractional_time_step_3", 
            "The timesteps chosen in each evolution phase as decimal fractions of the time taken in that phase: HG, HeMS (0.02)",
            units.none, 
            0.02 | units.none
        )
        
        object.add_caching_parameter(
            "initialize",
            "sigma_in",
            "SN_kick_speed_dispersion",
            "The dispersion in the Maxwellian for the SN kick speed (190 km/s).",
            units.km / units.s,
            190.0 | units.km / units.s
        )
        
        object.add_caching_parameter(
            "initialize",
            "beta_in",
            "wind_velocity_factor",
            "The wind velocity factor: proportional to vwind**2 (1/8).",
            units.none,
            0.125 | units.none
        )
        
        object.add_caching_parameter(
            "initialize",
            "xi_in",
            "wind_accretion_efficiency",
            "The wind accretion efficiency factor (1.0).",
            units.none,
            1.0 | units.none
        )
        
        object.add_caching_parameter(
            "initialize",
            "acc2_in",
            "wind_accretion_factor",
            "The Bondi-Hoyle wind accretion factor (3/2).",
            units.none,
            1.5 | units.none
        )
        
        object.add_caching_parameter(
            "initialize",
            "epsnov_in",
            "nova_retained_accreted_matter_fraction",
            "The fraction of accreted matter retained in nova eruption (0.001).",
            units.none,
            0.001 | units.none
        )
        
        object.add_caching_parameter(
            "initialize",
            "eddfac_in",
            "Eddington_mass_transfer_limit_factor",
            "The Eddington limit factor for mass transfer (1.0).",
            units.none,
            1.0 | units.none
        )
        
        object.add_caching_parameter(
            "initialize",
            "gamma_in",
            "Roche_angular_momentum_factor",
            "The angular momentum factor for mass lost during Roche (-1.0). ",
            units.none,
            -1.0 | units.none
        )
    
    
    def define_methods(self, object):
        
        object.add_method( 
            "get_time_step", 
            (
                units.stellar_type,
                units.stellar_type,
                units.MSun, 
                units.MSun, 
                units.MSun, 
                units.MSun, 
                units.Myr,  
                units.Myr,  
                units.Myr,  
                units.Myr,  
                units.Myr
            ),
            (units.Myr,)
        )
        
        
        p = (
            units.stellar_type,
            units.stellar_type,
            units.MSun,
            units.MSun,
            units.MSun,
            units.MSun,
            units.RSun,
            units.RSun,
            units.LSun,
            units.LSun,
            units.MSun,
            units.MSun,
            units.RSun,
            units.RSun,
            units.MSun,
            units.MSun,
            units.RSun,
            units.RSun,
            units.none,
            units.none,
            units.Myr,
            units.Myr,
            units.Myr,
            units.Myr,
            units.Myr,
            units.day,
            units.none,
            units.Myr,
        )
        
        object.add_method( "evolve", p, p)
        
        object.add_method(
            "initialize",
            (
                units.none,
                units.none, 
                units.none, 
                units.none, 
                units.none, 
                units.none, 
                units.none, 
                units.none, 
                units.none, 
                units.none, 
                units.none, 
                units.none, 
                units.MSun,
                units.none, 
                units.none, 
                units.none, 
                units.none,
                units.km / units.s,
                units.none, 
                units.none, 
                units.none, 
                units.none, 
                units.none, 
                units.none
            ),
            public_name = "initialize_"
        )
         
    def define_particle_sets(self, object):
        object.define_inmemory_set('particles', BSEParticles)
        
        object.add_attribute(
            'particles',
            'time_step', 
            'get_time_step', 
            ('type1', 'type2', 
             'initial_mass1', 'initial_mass2', 
             'mass1', 'mass2',
             'MS_lifetime1', 'MS_lifetime2',
             'epoch1', 'epoch2',
             'age')
        )
        
        
    def _evolve_particles(self, particles, end_time):
        attributes = (
            "type1",
            "type2", 
            "initial_mass1", 
            "initial_mass2",
            "mass1", 
            "mass2", 
            "radius1",
            "radius2", 
            "luminosity1", 
            "luminosity2",
            "core_mass1", 
            "core_mass2", 
            "core_radius1", 
            "core_radius2", 
            "envelope_mass1", 
            "envelope_mass2", 
            "envelope_radius1", 
            "envelope_radius2", 
            "spin1", 
            "spin2", 
            "epoch1", 
            "epoch2", 
            "MS_lifetime1", 
            "MS_lifetime2", 
            "age", 
            "orbital_period", 
            "eccentricity"
        )
        
        arguments = particles._get_values(particles._get_keys(), attributes)
        
        arguments.append(end_time.as_vector_with_length(len(particles)))
        
        result = self.evolve(*arguments)
        
        particles._set_values(particles._get_keys(), attributes, result)
        
        
    def evolve_model(self, end_time = None):
        if end_time is None:
            end_time = self.particles.time_step + self.particles.age
            
        self._evolve_particles(self.particles, end_time)
        

    
    def initialize_stars(self):
        pass

    def update_time_steps(self):
        pass
        
    
    def initialize_module_with_current_parameters(self):
        self.parameters.send_cached_parameters_to_code()
        
    def initialize_module_with_default_parameters(self):
        """
        * neta is the Reimers mass-loss coefficent (neta*4x10^-13; 0.5 normally).
        * bwind is the binary enhanced mass loss parameter (inactive for single).
        * hewind is a helium star mass loss factor (1.0 normally). 
        * sigma is the dispersion in the Maxwellian for the SN kick speed (190 km/s). 
        *
        * ifflag > 0 uses WD IFMR of HPE, 1995, MNRAS, 272, 800 (0). 
        * wdflag > 0 uses modified-Mestel cooling for WDs (0). 
        * bhflag > 0 allows velocity kick at BH formation (0). 
        * nsflag > 0 takes NS/BH mass from Belczynski et al. 2002, ApJ, 572, 407 (1). 
        * mxns is the maximum NS mass (1.8, nsflag=0; 3.0, nsflag=1). 
        * idum is the random number seed used in the kick routine. 
        *
        * Next come the parameters that determine the timesteps chosen in each
        * evolution phase:
        *                 pts1 - MS                  (0.05)
        *                 pts2 - GB, CHeB, AGB, HeGB (0.01)
        *                 pts3 - HG, HeMS            (0.02)
        * as decimal fractions of the time taken in that phase.
        """
        self.parameters.set_defaults()
        self.initialize_module_with_current_parameters()

        
        
         
        
        
