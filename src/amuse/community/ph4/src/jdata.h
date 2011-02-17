#ifndef JDATA_H
#define JDATA_H

// Define the jdata class: data and methods operating on the entire
// N-body system.

#include "stdinc.h"
#include <vector>
#include <map>

class scheduler;
class idata;

// Note: after proper initialization:
//
//     jdata and scheduler have pointers to each other
//     jdata and idata have pointers to each other
//     idata has a pointer to scheduler
//
// Order of initialization: jdata, idata(jdata), scheduler(jdata).

#define JBUF_INC	8192

class jdata {

  public:

    int nj;
    int njbuf;

    MPI::Intracomm mpi_comm;		// communicator for the N-body system
    int mpi_size;
    int mpi_rank;

    bool have_gpu;			// will be true if -DGPU is compiled in
    bool use_gpu;			// true if actually using GPU

    real eps2, eta;
    real rmin;				// 90 degree turnaround distance
    real dtmin;				// time step for enabling nn check

    real block_steps, total_steps, gpu_calls, gpu_total;
    real system_time, predict_time;

    int close1, close2;			// close particles (within rmin)
    int coll1, coll2;			// colliding particles

    // NOTE: name and id are unique identifiers for a particle in the
    // j system; id is called "index" in AMUSE, but it doesn't directly
    // index the jdata arrays, as particles may migrate.

    string *name;
    int *id, *nn;
    map<int,int> inverse_id;
    vector<int> user_specified_id;

    real *mass, *radius, *pot, *dnn, *time, *timestep;
    real2 pos, vel, acc, jerk;
    real2 pred_pos, pred_vel;

    idata *idat;
    scheduler *sched;

    jdata() {
	nj = 0;
	njbuf = 0;
	mpi_comm = NULL;
	mpi_size = 0;
	mpi_rank = -1;
	have_gpu = false;		// correct values will be set at
	use_gpu = false;		// run time, in setup_gpu()
	eps2 = eta = rmin = dtmin = 0;
	block_steps = total_steps = gpu_calls = gpu_total = 0;
	system_time = predict_time = -1;
	coll1 = coll2 = -1;
	id = nn = NULL;
	inverse_id.clear();
	user_specified_id.clear();
	name = NULL;
	mass = radius = pot = dnn = time = timestep = NULL;
	pos = vel = acc = jerk = pred_pos = pred_vel = NULL;

	idat = NULL;
	sched = NULL;
    }

    void cleanup();		// (in jdata.cc)
    ~jdata() {cleanup();}

    // In jdata.cc:

    void setup_mpi(MPI::Intracomm comm);
    void setup_gpu();
    int get_particle_id(int offset = 0);
    int add_particle(real pmass, real pradius, vec ppos, vec pvel,
		     int pid = -1, real dt = -1);
    void remove_particle(int j);
    void initialize_arrays();
    int get_inverse_id(int i);
    void check_inverse_id();
    void set_initial_timestep();
    real get_pot(bool reeval = false);
    real get_kin(bool reeval = false);
    real get_energy(bool reeval = false);
    real get_total_mass();
    void predict(int j, real t);
    void predict_all(real t, bool full_range = false);
    void advance();
    void synchronize_all();
    void synchronize_list(int jlist[], int njlist);
    void print();
    void spec_output(const char *s = NULL);
    void to_com();

    // In gpu.cc:

    void initialize_gpu(bool reinitialize = false);
    void update_gpu(int jlist[], int njlist);
    void sync_gpu();
    void get_densities_on_gpu();

    // In diag.cc:

    void get_com(vec& pos, vec& vel);
    void get_mcom(vec& pos, vec& vel,
		  real cutoff = 0.9,
		  int n_iter = 2);
    vec get_center();
    void get_lagrangian_radii(vector<real>& mlist,
			      vector<real>& rlist,
			      vec center = 0);
    void print_percentiles(vec center = 0);

    // In close_encounter.cc:

    bool resolve_encounter();
};

void update_merger_energy(real dEmerge);

#endif
