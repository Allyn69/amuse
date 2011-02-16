
// ***************
// * diagnostics *
// ***************
//
// Global functions:
//
//	real get_elapsed_time()
//	real get_cpu_time(real& user_time, real& system_time)
//	vec jdata::get_center()
//	void jdata::print_percentiles(vec center)

#include "jdata.h"
#include <sys/time.h>
#include <sys/resource.h>

#include <vector>
#include <algorithm>

// Note: the first call to a timer function sets its zero point.

static bool etset = false;
static timeval et0;
real get_elapsed_time()
{
    if (!etset) {
	gettimeofday(&et0, NULL);
	etset = true;
	cout << "initialized elapsed time counter" << endl << flush;
	return 0;
    } else {
	timeval et;			// et.tv_set = time(NULL), note
	gettimeofday(&et, NULL);
	return et.tv_sec - et0.tv_sec + 1.e-6*(et.tv_usec - et0.tv_usec);
    }
}

static bool ctset = false;
static real user0, sys0;
void get_cpu_time(real& user_time, real& system_time)
{
    struct rusage tim;
    getrusage(RUSAGE_SELF, &tim);

    if (!ctset) {
	user0 = tim.ru_utime.tv_sec + 1.e-6*tim.ru_utime.tv_usec;
	sys0 = tim.ru_stime.tv_sec + 1.e-6*tim.ru_stime.tv_usec;
	user_time = system_time = 0;
	ctset = true;
	cout << "initialized CPU time counter" << endl << flush;
    } else {
	user_time = tim.ru_utime.tv_sec + 1.e-6*tim.ru_utime.tv_usec - user0;
	system_time = tim.ru_stime.tv_sec + 1.e-6*tim.ru_stime.tv_usec - sys0;
    }
}

void jdata::get_com(vec& cmpos, vec& cmvel)
{
    // Compute the center of mass of the system.

    cmpos = cmvel = 0;
    real mtot = 0;
    for (int j = 0; j < nj; j++) {
	mtot += mass[j];
	for (int k = 0; k < 3; k++) {
	    cmpos[k] += mass[j]*pos[j][k];
	    cmvel[k] += mass[j]*vel[j][k];
	}
    }
    cmpos /= mtot;
    cmvel /= mtot;
}

// Data structure mrdata does double duty for calculation of both the
// modified center of mass and lagrangian radii.

class mrdata {
  public:
    int index;
    real mass;
    real r_sq;
    mrdata(int ii, real mm, real rr) {index = ii; mass = mm; r_sq = rr;}
};

bool operator < (const mrdata& x, const mrdata& y) {return x.r_sq < y.r_sq;}

void jdata::get_mcom(vec& cmpos, vec& cmvel,
		     real cutoff,		// default = 0.9
		     int n_iter)		// default = 2
{
    // Compute the modified center of mass of the system.  Code stolen
    // from Starlab and modified to use STL vectors.

    // Use center of mass pos and vel as the starting point for
    // computing the modified com.

    get_com(cmpos, cmvel);

    vector<mrdata> mrlist;
    bool loop;
    int count = n_iter;

    if (cutoff > 1) cutoff = 1;
    if (cutoff == 1) count = 0;

    int j_max = (int) (cutoff*nj);

    do {
	loop = false;

	// Set up an array of radii relative to the current center.

	for (int j = 0; j < nj; j++) {
	    real r_sq = 0;
	    for (int k = 0; k < 3; k++)
		r_sq += pow(pos[j][k] - cmpos[k], 2);
	    mrlist.push_back(mrdata(j, mass[j], r_sq));
	}

	// Sort the array by radius.

	sort(mrlist.begin(), mrlist.end());

	// Compute mpos and mvel by removing outliers (defined as a
	// fixed fraction by number) and recomputing the center of
	// mass.

	// Currently, apply mass-independent weighting to all stars, but
	// let the weighting function go to zero at the cutoff.

	real r_sq_maxi = 1/mrlist[j_max].r_sq;
	real weighted_mass = 0;
	vec new_pos = 0, new_vel = 0;
	for (int jlist = 0; jlist < j_max; jlist++) {
	    int j = mrlist[jlist].index;
	    real r_sq = mrlist[jlist].r_sq;
	    real rfac = 1 - r_sq*r_sq_maxi;
	    if (rfac < 0) rfac = 0;
	    real weight = mrlist[jlist].mass * rfac;
	    weighted_mass += weight;
	    for (int k = 0; k < 3; k++) {
		new_pos[k] += weight * pos[j][k];
		new_vel[k] += weight * vel[j][k];
	    }
	}

	if (weighted_mass > 0) {
	    cmpos = new_pos / weighted_mass;
	    cmvel = new_vel / weighted_mass;
	    if (count-- > 0) loop = true;
	}

    } while (loop);
}

vec jdata::get_center()
{
    vec cmpos, cmvel;
    get_mcom(cmpos, cmvel);
    return cmpos;
}



void jdata::get_lagrangian_radii(vector<real>& mlist,
				 vector<real>& rlist,
				 vec center)	// default = (0,0,0)
{
    // Compute lagrangian radii corresponding to the input lagrangian
    // masses.  Probably should parallelize this...

    vector<mrdata> mrlist;
    real total_mass = 0;
    for (int j = 0; j < nj; j++) {
	total_mass += mass[j];
	real r_sq = 0;
	for (int k = 0; k < 3; k++)
	    r_sq += pow(pos[j][k] - center[k], 2);
	mrlist.push_back(mrdata(id[j], mass[j], r_sq));
    }

    sort(mrlist.begin(), mrlist.end());

    // Extract the desired radii.

    vector<real>::const_iterator miter = mlist.begin();
    real mcurr = 0;
    rlist.clear();

    for (vector<mrdata>::const_iterator mriter = mrlist.begin();
	 mriter != mrlist.end(); mriter++) {
	mcurr += mriter->mass;

	if (mcurr >= *miter) {
	    rlist.push_back(sqrt(mriter->r_sq));
	    miter++;
	    if (miter == mlist.end()) break;
	}
    }
    mpi_comm.Barrier();
}

void jdata::print_percentiles(vec center)	// default = (0,0,0)
{
    // Print selected percentiles.

    vector<real> mlist, rlist;

    mlist.push_back(0.01);
    mlist.push_back(0.02);
    mlist.push_back(0.05);
    mlist.push_back(0.10);
    mlist.push_back(0.25);
    mlist.push_back(0.50);
    mlist.push_back(0.75);
    mlist.push_back(0.90);
    rlist.clear();

    get_lagrangian_radii(mlist, rlist, center);

    cout << "lagrangian radii (";
    for (unsigned int ip = 0; ip < mlist.size(); ip++) {
	if (ip > 0) cout << " ";
	printf("%.2f", mlist[ip]);
    }
    cout << "):" << endl << "   " << flush;
    for (unsigned int ip = 0; ip < mlist.size(); ip++)
	printf(" %.4f", rlist[ip]);
    cout << endl << flush;
}
