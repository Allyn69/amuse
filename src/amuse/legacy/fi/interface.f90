function initialize_code() result(ret)
  integer :: ret
  call muse_start
  call muse_reset
  ret=0
end function

function cleanup_code() result(ret)
  integer :: ret
  call muse_end
  call muse_start
  call muse_reset
  ret=0
end function

function commit_particles(time) result(ret)
  integer :: ret
  real*8 :: time
  call muse_init
  call muse_set_time(time)
  call muse_finalize_init 
  ret=0
end function

function recommit_particles() result(ret)
  integer :: ret,muse_reinitialize
  ret=muse_reinitialize()
end function


function commit_parameters(time) result(ret)
  integer :: ret
  real*8 :: time
  ret=0
end function

function recommit_parameters(time) result(ret)
  integer :: ret
  real*8 :: time
  ret=0
end function

function get_number_of_particles(n) result(ret)
  integer n,muse_get_nbodies,ret
  n=muse_get_nbodies() 
  ret=0
end function

function get_index_of_first_particle(id) result(ret)
  integer :: id,ret
  integer :: muse_index_of_first_particle
  ret=muse_index_of_first_particle(id)
end function

function get_index_of_next_particle(id,id1) result(ret)
  integer :: id,id1,ret
  integer :: muse_index_of_next_particle
  ret=muse_index_of_next_particle(id,id1)
end function

function get_time(t) result(ret)
  integer :: ret
  real*8 :: t,muse_get_time
  t=muse_get_time()
  ret=0
end function

function evolve(tend) result(ret)
  integer :: ret
  real*8 :: tend
  call muse_stepsys(tend,1)
  ret=0
end function

function synchronize_model() result(ret)
  integer :: ret,amuse_synchronize_model
  real*8 :: dum1,dum2,dum3 
  ret=amuse_synchronize_model()
end function

function get_kinetic_energy(e) result(ret)
  integer :: ret
  real*8 :: e,ek,ep,eth
  call muse_energies(0,ek,ep,eth)
  e=ek
  ret=0
end function

function get_potential_energy(e) result(ret)
  integer :: ret
  real*8 :: e,ek,ep,eth
  call muse_energies(0,ek,ep,eth)
  e=ep
  ret=0
end function

function get_thermal_energy(e) result(ret)
  integer :: ret
  real*8 :: e,ek,ep,eth
  call muse_energies(0,ek,ep,eth)
  e=eth
  ret=0
end function


function new_particle(ids,mass,eps,x,y,z,vx,vy,vz) result(ret)
  integer :: ids,ret,oldnp,muse_get_nbodies
  integer :: new_id, add_dm_particle
  real*8 :: mass,eps,x,y,z,vx,vy,vz
  ids=new_id()
  oldnp=muse_get_nbodies()
  ret=add_dm_particle(ids,mass,x,y,z,vx,vy,vz,eps,1)
  if(ret.EQ.oldnp+1) then
    ret=0
  else
    ret=-1
  endif 
end function

function new_sph_particle(ids,mass,eps,x,y,z,vx,vy,vz,u) result(ret)
  integer :: ids,ret,oldnp,muse_get_nsph
  integer :: new_id, add_sph_particle
  real*8 :: mass,eps,x,y,z,vx,vy,vz,u
  ids=new_id()
  oldnp=muse_get_nsph()
  ret=add_sph_particle(ids,mass,x,y,z,vx,vy,vz,eps,u,1)
  if(ret.EQ.oldnp+1) then
    ret=0
  else
    ret=-1
  endif 
end function

function new_star_particle(ids,mass,eps,x,y,z,vx,vy,vz,tf) result(ret)
  integer :: ids,ret,oldnp,muse_get_nstar
  integer :: new_id, add_star_particle
  real*8 :: mass,eps,x,y,z,vx,vy,vz,tf
  ids=new_id()
  oldnp=muse_get_nstar()
  ret=add_star_particle(ids,mass,x,y,z,vx,vy,vz,eps,tf,1)
  if(ret.EQ.oldnp+1) then
    ret=0
  else
    ret=-1
  endif 
end function

function add_dm_particle(ids,mass,x,y,z,vx,vy,vz,eps,npart) result(n)
  integer :: npart
  integer :: ids(npart),n,muse_get_nbodies
  real*8 :: mass(npart),x(npart),y(npart),z(npart), &
    vx(npart),vy(npart),vz(npart),eps(npart)
  call muse_add_particle_dm(ids,mass,x,y,z,vx,vy,vz,eps,npart)
  n=muse_get_nbodies()
end function

function add_star_particle(ids,mass,x,y,z,vx,vy,vz,eps,tf,npart) result(n)
  integer :: npart
  integer :: ids(npart),n,muse_get_nstar
  real*8 :: mass(npart),x(npart),y(npart),z(npart), &
    vx(npart),vy(npart),vz(npart),eps(npart),tf(npart)
  call muse_add_particle_star(ids,mass,x,y,z,vx,vy,vz,eps,tf,npart)
  n=muse_get_nstar()
end function

function add_sph_particle(ids,mass,x,y,z,vx,vy,vz,eps,u,npart) result(n)
  integer :: npart
  integer :: ids(npart),n,muse_get_nsph
  real*8 :: mass(npart),x(npart),y(npart),z(npart), &
    vx(npart),vy(npart),vz(npart),eps(npart),u(npart)
  call muse_add_particle_sph(ids,mass,x,y,z,vx,vy,vz,eps,u,npart)
  n=muse_get_nsph()
end function

function set_state(id,mass,eps,x,y,z,vx,vy,vz) result(ret)
  integer id,ret,amuse_set_state
  real*8 mass,eps,x,y,z,vx,vy,vz 
  ret=amuse_set_state(id,mass,x,y,z,vx,vy,vz,eps)
end function

function set_state_sph(id,mass,eps,x,y,z,vx,vy,vz,u) result(ret)
  integer id,ret,amuse_set_state_sph
  real*8 mass,eps,x,y,z,vx,vy,vz,u 
  ret=amuse_set_state_sph(id,mass,x,y,z,vx,vy,vz,eps,u)
end function

function set_state_star(id,mass,eps,x,y,z,vx,vy,vz,tf) result(ret)
  integer id,ret,amuse_set_state_star
  real*8 mass,eps,x,y,z,vx,vy,vz,tf 
  ret=amuse_set_state_star(id,mass,x,y,z,vx,vy,vz,eps,tf)
end function

function get_state(id,mass,eps,x,y,z,vx,vy,vz) result(ret)
  integer :: id,ret,amuse_get_state
  real*8 :: mass,x,y,z,vx,vy,vz,eps
  ret=amuse_get_state(id,mass,x,y,z,vx,vy,vz,eps)
end function

function get_state_sph(id,mass,eps,x,y,z,vx,vy,vz,u) result(ret)
  integer :: id,ret,amuse_get_state_sph
  real*8 :: mass,x,y,z,vx,vy,vz,eps,u
  ret=amuse_get_state_sph(id,mass,x,y,z,vx,vy,vz,eps,u)
end function

function get_state_star(id,mass,eps,x,y,z,vx,vy,vz,tf) result(ret)
  integer :: id,ret,amuse_get_state_star
  real*8 :: mass,x,y,z,vx,vy,vz,eps,tf
  ret=amuse_get_state_star(id,mass,x,y,z,vx,vy,vz,eps,tf)
end function

function delete_particle(id) result(ret)
  integer id,ret,muse_remove_particle
  ret=muse_remove_particle(id)
end function

function get_gravity_at_point(eps, x, y, z, ax, ay, az) result(ret)
  real*8 :: eps, x, y, z, ax, ay, az
  integer :: ret  
  ax=0;ay=0;az=0
  call muse_get_gravity(eps,x,y,z,ax,ay,az,1)
  ret=0
end function

function get_potential_at_point(eps, x, y, z, phi) result(ret)
  real*8 :: eps,x, y, z, phi
  integer :: ret
  call muse_get_pot(eps,x,y,z,phi,1)
  ret=0  
end function

! setting/ getting parameters

function set_usesph(zeroiftrue) result(ret)
  integer :: zeroiftrue,ret
  if(zeroiftrue.EQ.0) call amuse_set_usesph(.TRUE.)
  if(zeroiftrue.NE.0) call amuse_set_usesph(.FALSE.)
  ret=0
end function
function get_usesph(zeroiftrue) result(ret)
  integer :: ret,zeroiftrue
  logical :: x
  zeroiftrue=1
  call amuse_get_usesph(x) 
  if(x) zeroiftrue=0
  ret=0
end function

function set_radiate(zeroiftrue) result(ret)
  integer :: zeroiftrue,ret
  if(zeroiftrue.EQ.0) call amuse_set_radiate(.TRUE.)
  if(zeroiftrue.NE.0) call amuse_set_radiate(.FALSE.)
  ret=0
end function
function get_radiate(zeroiftrue) result(ret)
  integer :: ret,zeroiftrue
  logical :: x
  zeroiftrue=1
  call amuse_get_radiate(x) 
  if(x) zeroiftrue=0
  ret=0
end function

function set_starform(zeroiftrue) result(ret)
  integer :: zeroiftrue,ret
  if(zeroiftrue.EQ.0) call amuse_set_starform(.TRUE.)
  if(zeroiftrue.NE.0) call amuse_set_starform(.FALSE.)
  ret=0
end function
function get_starform(zeroiftrue) result(ret)
  integer :: ret,zeroiftrue
  logical :: x
  zeroiftrue=1
  call amuse_get_starform(x) 
  if(x) zeroiftrue=0
  ret=0
end function

function set_cosmo(zeroiftrue) result(ret)
  integer :: zeroiftrue,ret
  if(zeroiftrue.EQ.0) call amuse_set_cosmo(.TRUE.)
  if(zeroiftrue.NE.0) call amuse_set_cosmo(.FALSE.)
  ret=0
end function
function get_cosmo(zeroiftrue) result(ret)
  integer :: ret,zeroiftrue
  logical :: x
  zeroiftrue=1
  call amuse_get_cosmo(x) 
  if(x) zeroiftrue=0
  ret=0
end function

function set_sqrttstp(zeroiftrue) result(ret)
  integer :: zeroiftrue,ret
  if(zeroiftrue.EQ.0) call amuse_set_sqrttstp(.TRUE.)
  if(zeroiftrue.NE.0) call amuse_set_sqrttstp(.FALSE.)
  ret=0
end function
function get_sqrttstp(zeroiftrue) result(ret)
  integer :: ret,zeroiftrue
  logical :: x
  zeroiftrue=1
  call amuse_get_sqrttstp(x) 
  if(x) zeroiftrue=0
  ret=0
end function

function set_acc_tstp(zeroiftrue) result(ret)
  integer :: zeroiftrue,ret
  if(zeroiftrue.EQ.0) call amuse_set_acc_tstp(.TRUE.)
  if(zeroiftrue.NE.0) call amuse_set_acc_tstp(.FALSE.)
  ret=0
end function
function get_acc_tstp(zeroiftrue) result(ret)
  integer :: ret,zeroiftrue
  logical :: x
  zeroiftrue=1
  call amuse_get_acc_tstp(x) 
  if(x) zeroiftrue=0
  ret=0
end function

function set_freetstp(zeroiftrue) result(ret)
  integer :: zeroiftrue,ret
  if(zeroiftrue.EQ.0) call amuse_set_freetstp(.TRUE.)
  if(zeroiftrue.NE.0) call amuse_set_freetstp(.FALSE.)
  ret=0
end function
function get_freetstp(zeroiftrue) result(ret)
  integer :: ret,zeroiftrue
  logical :: x
  zeroiftrue=1
  call amuse_get_freetstp(x) 
  if(x) zeroiftrue=0
  ret=0
end function

function set_usequad(zeroiftrue) result(ret)
  integer :: zeroiftrue,ret
  if(zeroiftrue.EQ.0) call amuse_set_usequad(.TRUE.)
  if(zeroiftrue.NE.0) call amuse_set_usequad(.FALSE.)
  ret=0
end function
function get_usequad(zeroiftrue) result(ret)
  integer :: ret,zeroiftrue
  logical :: x
  zeroiftrue=1
  call amuse_get_usequad(x) 
  if(x) zeroiftrue=0
  ret=0
end function

function set_directsum(zeroiftrue) result(ret)
  integer :: zeroiftrue,ret
  if(zeroiftrue.EQ.0) call amuse_set_directsum(.TRUE.)
  if(zeroiftrue.NE.0) call amuse_set_directsum(.FALSE.)
  ret=0
end function
function get_directsum(zeroiftrue) result(ret)
  integer :: ret,zeroiftrue
  logical :: x
  zeroiftrue=1
  call amuse_get_directsum(x) 
  if(x) zeroiftrue=0
  ret=0
end function

function set_selfgrav(zeroiftrue) result(ret)
  integer :: zeroiftrue,ret
  if(zeroiftrue.EQ.0) call amuse_set_selfgrav(.TRUE.)
  if(zeroiftrue.NE.0) call amuse_set_selfgrav(.FALSE.)
  ret=0
end function
function get_selfgrav(zeroiftrue) result(ret)
  integer :: ret,zeroiftrue
  logical :: x
  zeroiftrue=1
  call amuse_get_selfgrav(x) 
  if(x) zeroiftrue=0
  ret=0
end function

function set_fixthalo(zeroiftrue) result(ret)
  integer :: zeroiftrue,ret
  if(zeroiftrue.EQ.0) call amuse_set_fixthalo(.TRUE.)
  if(zeroiftrue.NE.0) call amuse_set_fixthalo(.FALSE.)
  ret=0
end function
function get_fixthalo(zeroiftrue) result(ret)
  integer :: ret,zeroiftrue
  logical :: x
  zeroiftrue=1
  call amuse_get_fixthalo(x) 
  if(x) zeroiftrue=0
  ret=0
end function

function set_adaptive_eps(zeroiftrue) result(ret)
  integer :: zeroiftrue,ret
  if(zeroiftrue.EQ.0) call amuse_set_adaptive_eps(.TRUE.)
  if(zeroiftrue.NE.0) call amuse_set_adaptive_eps(.FALSE.)
  ret=0
end function
function get_adaptive_eps(zeroiftrue) result(ret)
  integer :: ret,zeroiftrue
  logical :: x
  zeroiftrue=1
  call amuse_get_adaptive_eps(x) 
  if(x) zeroiftrue=0
  ret=0
end function

function set_gdgop(zeroiftrue) result(ret)
  integer :: zeroiftrue,ret
  if(zeroiftrue.EQ.0) call amuse_set_gdgop(.TRUE.)
  if(zeroiftrue.NE.0) call amuse_set_gdgop(.FALSE.)
  ret=0
end function
function get_gdgop(zeroiftrue) result(ret)
  integer :: ret,zeroiftrue
  logical :: x
  zeroiftrue=1
  call amuse_get_gdgop(x) 
  if(x) zeroiftrue=0
  ret=0
end function

function set_smoothinput(zeroiftrue) result(ret)
  integer :: zeroiftrue,ret
  if(zeroiftrue.EQ.0) call amuse_set_smoothinput(.TRUE.)
  if(zeroiftrue.NE.0) call amuse_set_smoothinput(.FALSE.)
  ret=0
end function
function get_smoothinput(zeroiftrue) result(ret)
  integer :: ret,zeroiftrue
  logical :: x
  zeroiftrue=1
  call amuse_get_smoothinput(x) 
  if(x) zeroiftrue=0
  ret=0
end function

function set_consph(zeroiftrue) result(ret)
  integer :: zeroiftrue,ret
  if(zeroiftrue.EQ.0) call amuse_set_consph(.TRUE.)
  if(zeroiftrue.NE.0) call amuse_set_consph(.FALSE.)
  ret=0
end function
function get_consph(zeroiftrue) result(ret)
  integer :: ret,zeroiftrue
  logical :: x
  zeroiftrue=1
  call amuse_get_consph(x) 
  if(x) zeroiftrue=0
  ret=0
end function

function set_sphinit(zeroiftrue) result(ret)
  integer :: zeroiftrue,ret
  if(zeroiftrue.EQ.0) call amuse_set_sphinit(.TRUE.)
  if(zeroiftrue.NE.0) call amuse_set_sphinit(.FALSE.)
  ret=0
end function
function get_sphinit(zeroiftrue) result(ret)
  integer :: ret,zeroiftrue
  logical :: x
  zeroiftrue=1
  call amuse_get_sphinit(x) 
  if(x) zeroiftrue=0
  ret=0
end function

function set_uentropy(zeroiftrue) result(ret)
  integer :: zeroiftrue,ret
  if(zeroiftrue.EQ.0) call amuse_set_uentropy(.TRUE.)
  if(zeroiftrue.NE.0) call amuse_set_uentropy(.FALSE.)
  ret=0
end function
function get_uentropy(zeroiftrue) result(ret)
  integer :: ret,zeroiftrue
  logical :: x
  zeroiftrue=1
  call amuse_get_uentropy(x) 
  if(x) zeroiftrue=0
  ret=0
end function

function set_isotherm(zeroiftrue) result(ret)
  integer :: zeroiftrue,ret
  if(zeroiftrue.EQ.0) call amuse_set_isotherm(.TRUE.)
  if(zeroiftrue.NE.0) call amuse_set_isotherm(.FALSE.)
  ret=0
end function
function get_isotherm(zeroiftrue) result(ret)
  integer :: ret,zeroiftrue
  logical :: x
  zeroiftrue=1
  call amuse_get_isotherm(x) 
  if(x) zeroiftrue=0
  ret=0
end function

function set_eps_is_h(zeroiftrue) result(ret)
  integer :: zeroiftrue,ret
  if(zeroiftrue.EQ.0) call amuse_set_eps_is_h(.TRUE.)
  if(zeroiftrue.NE.0) call amuse_set_eps_is_h(.FALSE.)
  ret=0
end function
function get_eps_is_h(zeroiftrue) result(ret)
  integer :: ret,zeroiftrue
  logical :: x
  zeroiftrue=1
  call amuse_get_eps_is_h(x) 
  if(x) zeroiftrue=0
  ret=0
end function


! integers

function set_firstsnap(i) result(ret)
  integer :: ret,i
  call amuse_set_firstsnap(i)
  ret=0
end function
function get_firstsnap(i) result(ret)
  integer :: ret,i
  call amuse_get_firstsnap(i) 
  ret=0
end function

function set_stepout(i) result(ret)
  integer :: ret,i
  call amuse_set_stepout(i)
  ret=0
end function
function get_stepout(i) result(ret)
  integer :: ret,i
  call amuse_get_stepout(i) 
  ret=0
end function

function set_steplog(i) result(ret)
  integer :: ret,i
  call amuse_set_steplog(i)
  ret=0
end function
function get_steplog(i) result(ret)
  integer :: ret,i
  call amuse_get_steplog(i) 
  ret=0
end function

function set_max_tbin(i) result(ret)
  integer :: ret,i
  call amuse_set_max_tbin(i)
  ret=0
end function
function get_max_tbin(i) result(ret)
  integer :: ret,i
  call amuse_get_max_tbin(i) 
  ret=0
end function

function set_minppbin(i) result(ret)
  integer :: ret,i
  call amuse_set_minppbin(i)
  ret=0
end function
function get_minppbin(i) result(ret)
  integer :: ret,i
  call amuse_get_minppbin(i) 
  ret=0
end function

function set_targetnn(i) result(ret)
  integer :: ret,i
  call amuse_set_targetnn(i)
  ret=0
end function
function get_targetnn(i) result(ret)
  integer :: ret,i
  call amuse_get_targetnn(i) 
  ret=0
end function

function set_verbosity(i) result(ret)
  integer :: ret,i
  call amuse_set_verbosity(i)
  ret=0
end function
function get_verbosity(i) result(ret)
  integer :: ret,i
  call amuse_get_verbosity(i) 
  ret=0
end function

function set_nsmooth(i) result(ret)
  integer :: ret,i
  call amuse_set_nsmooth(i)
  ret=0
end function
function get_nsmooth(i) result(ret)
  integer :: ret,i
  call amuse_get_nsmooth(i) 
  ret=0
end function

! reals

function set_pboxsize(x) result(ret)
  integer :: ret
  real*8 :: x
  call amuse_set_pboxsize(x)
  ret=0
end function
function get_pboxsize(x) result(ret)
  integer :: ret
  real*8 :: x
  call amuse_get_pboxsize(x) 
  ret=0
end function

function set_unitm_in_msun(x) result(ret)
  integer :: ret
  real*8 :: x
  call amuse_set_unitm_in_msun(x)
  ret=0
end function
function get_unitm_in_msun(x) result(ret)
  integer :: ret
  real*8 :: x
  call amuse_get_unitm_in_msun(x) 
  ret=0
end function

function set_unitl_in_kpc(x) result(ret)
  integer :: ret
  real*8 :: x
  call amuse_set_unitl_in_kpc(x)
  ret=0
end function
function get_unitl_in_kpc(x) result(ret)
  integer :: ret
  real*8 :: x
  call amuse_get_unitl_in_kpc(x) 
  ret=0
end function

function set_dtime(x) result(ret)
  integer :: ret
  real*8 :: x
  call amuse_set_dtime(x)
  ret=0
end function

function set_time_step(time_step) result(ret)
  integer :: ret,set_dtime
  real*8 :: time_step
  ret=set_dtime(time_step)
end function

function get_dtime(x) result(ret)
  integer :: ret
  real*8 :: x
  call amuse_get_dtime(x) 
  ret=0
end function

function get_time_step(time_step) result(ret)
  integer :: ret,get_dtime
  real*8 :: time_step
  ret=get_dtime(time_step) 
end function

function set_tstepcrit(x) result(ret)
  integer :: ret
  real*8 :: x
  call amuse_set_tstepcrit(x)
  ret=0
end function

function get_tstepcrit(x) result(ret)
  integer :: ret
  real*8 :: x
  call amuse_get_tstepcrit(x) 
  ret=0
end function

function set_tstpcr2(x) result(ret)
  integer :: ret
  real*8 :: x
  call amuse_set_tstpcr2(x)
  ret=0
end function
function get_tstpcr2(x) result(ret)
  integer :: ret
  real*8 :: x
  call amuse_get_tstpcr2(x) 
  ret=0
end function

function set_freev(x) result(ret)
  integer :: ret
  real*8 :: x
  call amuse_set_freev(x)
  ret=0
end function

function get_freev(x) result(ret)
  integer :: ret
  real*8 :: x
  call amuse_get_freev(x) 
  ret=0
end function

function set_freea(x) result(ret)
  integer :: ret
  real*8 :: x
  call amuse_set_freea(x)
  ret=0
end function
function get_freea(x) result(ret)
  integer :: ret
  real*8 :: x
  call amuse_get_freea(x) 
  ret=0
end function

function set_freevexp(x) result(ret)
  integer :: ret
  real*8 :: x
  call amuse_set_freevexp(x)
  ret=0
end function
function get_freevexp(x) result(ret)
  integer :: ret
  real*8 :: x
  call amuse_get_freevexp(x) 
  ret=0
end function

function set_freeaexp(x) result(ret)
  integer :: ret
  real*8 :: x
  call amuse_set_freeaexp(x)
  ret=0
end function

function get_freeaexp(x) result(ret)
  integer :: ret
  real*8 :: x
  call amuse_get_freeaexp(x) 
  ret=0
end function

function set_bh_tol(x) result(ret)
  integer :: ret
  real*8 :: x
  call amuse_set_bh_tol(x)
  ret=0
end function

function get_bh_tol(x) result(ret)
  integer :: ret
  real*8 :: x
  call amuse_get_bh_tol(x) 
  ret=0
end function

function set_eps(x) result(ret)
  integer :: ret
  real*8 :: x
  call amuse_set_eps(x)
  ret=0
end function

function get_eps(x) result(ret)
  integer :: ret
  real*8 :: x
  call amuse_get_eps(x) 
  ret=0
end function

function set_gdgtol(x) result(ret)
  integer :: ret
  real*8 :: x
  call amuse_set_gdgtol(x)
  ret=0
end function
function get_gdgtol(x) result(ret)
  integer :: ret
  real*8 :: x
  call amuse_get_gdgtol(x) 
  ret=0
end function

function set_nn_tol(x) result(ret)
  integer :: ret
  real*8 :: x
  call amuse_set_nn_tol(x)
  ret=0
end function

function get_nn_tol(x) result(ret)
  integer :: ret
  real*8 :: x
  call amuse_get_nn_tol(x) 
  ret=0
end function

function set_epsgas(x) result(ret)
  integer :: ret
  real*8 :: x
  call amuse_set_epsgas(x)
  ret=0
end function
function get_epsgas(x) result(ret)
  integer :: ret
  real*8 :: x
  call amuse_get_epsgas(x) 
  ret=0
end function

function set_gamma(x) result(ret)
  integer :: ret
  real*8 :: x
  call amuse_set_gamma(x)
  ret=0
end function
function get_gamma(x) result(ret)
  integer :: ret
  real*8 :: x
  call amuse_get_gamma(x) 
  ret=0
end function

function set_alpha(x) result(ret)
  integer :: ret
  real*8 :: x
  call amuse_set_alpha(x)
  ret=0
end function

function get_alpha(x) result(ret)
  integer :: ret
  real*8 :: x
  call amuse_get_alpha(x) 
  ret=0
end function

function set_beta(x) result(ret)
  integer :: ret
  real*8 :: x
  call amuse_set_beta(x)
  ret=0
end function
function get_beta(x) result(ret)
  integer :: ret
  real*8 :: x
  call amuse_get_beta(x) 
  ret=0
end function

function set_epssph(x) result(ret)
  integer :: ret
  real*8 :: x
  call amuse_set_epssph(x)
  ret=0
end function
function get_epssph(x) result(ret)
  integer :: ret
  real*8 :: x
  call amuse_get_epssph(x) 
  ret=0
end function

function set_courant(x) result(ret)
  integer :: ret
  real*8 :: x
  call amuse_set_courant(x)
  ret=0
end function
function get_courant(x) result(ret)
  integer :: ret
  real*8 :: x
  call amuse_get_courant(x) 
  ret=0
end function

function set_removgas(x) result(ret)
  integer :: ret
  real*8 :: x
  call amuse_set_removgas(x)
  ret=0
end function
function get_removgas(x) result(ret)
  integer :: ret
  real*8 :: x
  call amuse_get_removgas(x) 
  ret=0
end function

function set_consthsm(x) result(ret)
  integer :: ret
  real*8 :: x
  call amuse_set_consthsm(x)
  ret=0
end function
function get_consthsm(x) result(ret)
  integer :: ret
  real*8 :: x
  call amuse_get_consthsm(x) 
  ret=0
end function

function set_nsmtol(x) result(ret)
  integer :: ret
  real*8 :: x
  call amuse_set_nsmtol(x)
  ret=0
end function
function get_nsmtol(x) result(ret)
  integer :: ret
  real*8 :: x
  call amuse_get_nsmtol(x) 
  ret=0
end function

function set_graineff(x) result(ret)
  integer :: ret
  real*8 :: x
  call amuse_set_graineff(x)
  ret=0
end function
function get_graineff(x) result(ret)
  integer :: ret
  real*8 :: x
  call amuse_get_graineff(x) 
  ret=0
end function

function set_crionrate(x) result(ret)
  integer :: ret
  real*8 :: x
  call amuse_set_crionrate(x)
  ret=0
end function
function get_crionrate(x) result(ret)
  integer :: ret
  real*8 :: x
  call amuse_get_crionrate(x) 
  ret=0
end function

function set_heat_par1(x) result(ret)
  integer :: ret
  real*8 :: x
  call amuse_set_heat_par1(x)
  ret=0
end function
function get_heat_par1(x) result(ret)
  integer :: ret
  real*8 :: x
  call amuse_get_heat_par1(x) 
  ret=0
end function

function set_heat_par2(x) result(ret)
  integer :: ret
  real*8 :: x
  call amuse_set_heat_par2(x)
  ret=0
end function
function get_heat_par2(x) result(ret)
  integer :: ret
  real*8 :: x
  call amuse_get_heat_par2(x) 
  ret=0
end function

function set_cool_par(x) result(ret)
  integer :: ret
  real*8 :: x
  call amuse_set_cool_par(x)
  ret=0
end function
function get_cool_par(x) result(ret)
  integer :: ret
  real*8 :: x
  call amuse_get_cool_par(x) 
  ret=0
end function

function set_optdepth(x) result(ret)
  integer :: ret
  real*8 :: x
  call amuse_set_optdepth(x)
  ret=0
end function
function get_optdepth(x) result(ret)
  integer :: ret
  real*8 :: x
  call amuse_get_optdepth(x) 
  ret=0
end function

function set_tcollfac(x) result(ret)
  integer :: ret
  real*8 :: x
  call amuse_set_tcollfac(x)
  ret=0
end function
function get_tcollfac(x) result(ret)
  integer :: ret
  real*8 :: x
  call amuse_get_tcollfac(x) 
  ret=0
end function

function set_masscrit(x) result(ret)
  integer :: ret
  real*8 :: x
  call amuse_set_masscrit(x)
  ret=0
end function
function get_masscrit(x) result(ret)
  integer :: ret
  real*8 :: x
  call amuse_get_masscrit(x) 
  ret=0
end function

function set_sfeff(x) result(ret)
  integer :: ret
  real*8 :: x
  call amuse_set_sfeff(x)
  ret=0
end function
function get_sfeff(x) result(ret)
  integer :: ret
  real*8 :: x
  call amuse_get_sfeff(x) 
  ret=0
end function

function set_tbubble(x) result(ret)
  integer :: ret
  real*8 :: x
  call amuse_set_tbubble(x)
  ret=0
end function
function get_tbubble(x) result(ret)
  integer :: ret
  real*8 :: x
  call amuse_get_tbubble(x) 
  ret=0
end function

function set_sne_eff(x) result(ret)
  integer :: ret
  real*8 :: x
  call amuse_set_sne_eff(x)
  ret=0
end function
function get_sne_eff(x) result(ret)
  integer :: ret
  real*8 :: x
  call amuse_get_sne_eff(x) 
  ret=0
end function

function set_tsnbeg(x) result(ret)
  integer :: ret
  real*8 :: x
  call amuse_set_tsnbeg(x)
  ret=0
end function
function get_tsnbeg(x) result(ret)
  integer :: ret
  real*8 :: x
  call amuse_get_tsnbeg(x) 
  ret=0
end function

function set_rhomax(x) result(ret)
  integer :: ret
  real*8 :: x
  call amuse_set_rhomax(x)
  ret=0
end function
function get_rhomax(x) result(ret)
  integer :: ret
  real*8 :: x
  call amuse_get_rhomax(x) 
  ret=0
end function


! character

function set_halofile(x) result(ret)
  integer :: ret
  character(len=30) :: x
  call amuse_set_halofile(x)
  ret=0
end function
function get_halofile(x) result(ret)
  integer :: ret
  character(len=30) :: x
  call amuse_get_halofile(x)
  ret=0
end function

function set_feedback(x) result(ret)
  integer :: ret
  character(len=4) :: x
  call amuse_set_feedback(x)
  ret=0
end function
function get_feedback(x) result(ret)
  integer :: ret
  character(len=4) :: x
  call amuse_get_feedback(x) 
  ret=0
end function

function set_sfmode(x) result(ret)
  integer :: ret
  character(len=10) :: x
  call amuse_set_sfmode(x)
  ret=0
end function
function get_sfmode(x) result(ret)
  integer :: ret
  character(len=10) :: x
  call amuse_get_sfmode(x)
  ret=0
end function

function set_hupdatemethod(x) result(ret)
  integer :: ret
  character(len=4) :: x
  call amuse_set_hupdatemethod(x)
  ret=0
end function
function get_hupdatemethod(x) result(ret)
  integer :: ret
  character(len=4) :: x
  call amuse_get_hupdatemethod(x) 
  ret=0
end function

function set_sph_visc(x) result(ret)
  integer :: ret
  character(len=4) :: x
  call amuse_set_sph_visc(x)
  ret=0
end function
function get_sph_visc(x) result(ret)
  integer :: ret
  character(len=4) :: x
  call amuse_get_sph_visc(x)
  ret=0
end function


 
! dummies:
! (only necessary to be able to compile using old muse style interface files)

subroutine call_external_acc(eps,x,y,z,ax,ay,az,n)
  integer n
  double precision :: eps(n), x(n),y(n),z(n)
  double precision :: ax(n),ay(n),az(n)

end subroutine

subroutine call_external_pot(eps,x,y,z,phi,n)
  integer n
  double precision :: eps(n), x(n),y(n),z(n)
  double precision :: phi(n)

end subroutine

