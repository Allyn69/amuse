"""
This is the public interface to the AMUSE 
*Astrophysical Multipurpose Software Environment* framework.


"""

from amuse.support.core import late


from amuse.units import units
from amuse.units import core
from amuse.units import si
from amuse.units import constants
from amuse.units import nbody_system
from amuse.units import nbody_system as nbody
from amuse.units.quantities import zero
from amuse.units.quantities import ScalarQuantity
from amuse.units.quantities import VectorQuantity
from amuse.units.quantities import AdaptingVectorQuantity
from amuse.units.quantities import new_quantity

from amuse.io import write_set_to_file
from amuse.io import read_set_from_file
from amuse.io import get_options_for_format

from amuse.ext.solarsystem import new_solar_system_for_mercury, new_solar_system
from amuse.ext.halogen_model import new_halogen_model
from amuse.ext.galactics_model import new_galactics_model
from amuse.ext.spherical_model import new_uniform_spherical_particle_distribution, new_spherical_particle_distribution
from amuse.ext.star_to_sph import convert_stellar_model_to_SPH, pickle_stellar_model

from amuse.community.bhtree.interface import BHTree, BHTreeInterface
from amuse.community.hermite0.interface import Hermite, HermiteInterface
from amuse.community.phiGRAPE.interface import PhiGRAPE, PhiGRAPEInterface
from amuse.community.octgrav.interface import Octgrav, OctgravInterface
from amuse.community.twobody.twobody import TwoBody, TwoBodyInterface
from amuse.community.huayno.interface import Huayno, HuaynoInterface
from amuse.community.ph4.interface import ph4, ph4Interface

from amuse.community.fi.interface import Fi, FiInterface
from amuse.community.gadget2.interface import Gadget2, Gadget2Interface
from amuse.community.athena.interface import Athena, AthenaInterface
from amuse.community.capreole.interface import Capreole, CapreoleInterface
from amuse.community.mpiamrvac.interface import MpiAmrVac, MpiAmrVacInterface

from amuse.community.simplex.interface import SimpleX, SimpleXInterface
from amuse.community.mocassin.interface import Mocassin, MocassinInterface

from amuse.community.sse.interface import SSE, SSEInterface
from amuse.community.bse.interface import BSE, BSEInterface
from amuse.community.evtwin.interface import EVtwin, EVtwinInterface
from amuse.community.mesa.interface import MESA, MESAInterface
from amuse.community.mmams.interface import MakeMeAMassiveStar, MakeMeAMassiveStarInterface


from amuse.support.console import set_printing_strategy
from amuse.support.console import get_current_printing_strategy
from amuse.datamodel import particle_attributes
from amuse.datamodel import Particle
from amuse.datamodel import Particles
from amuse.datamodel import ParticlesSuperset
from amuse.datamodel import Grid

from amuse.ic.plummer import new_plummer_model
from amuse.ic.salpeter import new_salpeter_mass_distribution
from amuse.ic.salpeter import new_salpeter_mass_distribution_nbody
from amuse.ic.kingmodel import new_king_model
from amuse.ic.gasplummer import new_plummer_gas_model

def vector(value = [], unit = None):
    if unit is None:
        if isinstance(value, core.unit):
            return VectorQuantity([], unit = value)
        elif isinstance(value, ScalarQuantity):
            return value.as_vector_with_length(1)
        else:
            return AdaptingVectorQuantity(value)
    else:
        if isinstance(value, ScalarQuantity):
            return value.as_vector_with_length(1)
        else:
            return VectorQuantity(value, unit)
            
