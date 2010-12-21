
// ***************************
// * GRAPE/GPU specific code *
// ***************************
//
// Global functions:
//
//	void jdata::initialize_gpu()
//	void idata::update_gpu(jdata& jd)
//	void idata::get_partial_acc_and_jerk_on_gpu(jdata& jd)
//	void jdata::get_densities_on_gpu(idata& id)  (UNDER DEVELOPMENT)  MPI

#include "jdata.h"
#include "idata.h"

#ifdef GPU
#include "grape.h"
#endif

// No need to check jdata::use_gpu here, as the GPU functions will
// only be called if use_gpu = true.

static int clusterid = 0;

void jdata::initialize_gpu(bool reinitialize)	// default = false
{
#ifdef GPU

    const char *in_function = "jdata::initialize_gpu";
    if (DEBUG > 2 && mpi_rank == 0) PRL(in_function);

    // Initialize the local GPU(s).
   
    if (!reinitialize) {
	g6_open(clusterid);
	// g6_set_tunit(new_tunit);
	// g6_set_xunit(new_xunit);
    }

    static int n = 0, j_start, j_end;
    static real a2[3] = {0,0,0}, j6[3] = {0,0,0}, k18[3] = {0,0,0};

    if (reinitialize) n = 0;

    if (n == 0) {

	// Define my j-range.

	n = nj/mpi_size;
	if (n*mpi_size < nj) n++;
	j_start = mpi_rank*n;
	j_end = j_start + n;
	if (mpi_rank == mpi_size-1) j_end = nj;
    }

    // Load local particles into the GPU.

    for (int j = j_start; j < j_end; j++)
	g6_set_j_particle(clusterid, j-j_start, id[j],	// note the use of ID
			  time[j], timestep[j],		// as GRAPE index
			  mass[j], k18, j6, a2, vel[j], pos[j]);

#endif
}



void jdata::update_gpu(int jlist[], int njlist)
{
#ifdef GPU

    const char *in_function = "jdata::update_gpu";
    if (DEBUG > 2 && mpi_rank == 0) PRL(in_function);

    // Load new position and velocity for selected j-particles into
    // the GPU.

    static int n = 0, j_start;
    static real a2[3], j6[3], k18[3] = {0,0,0};

    if (n == 0) {

	// Define my j-range.

	n = nj/mpi_size;
	if (n*mpi_size < nj) n++;
	j_start = mpi_rank*n;
    }

    for (int jj = 0; jj < njlist; jj++) {
	int j = jlist[jj];
	int curr_rank = j/n;
	if (curr_rank == mpi_rank) {
	    for (int k = 0; k < 3; k++) {
		a2[k] = acc[j][k]/2;
		j6[k] = jerk[j][k]/6;
	    }
	    g6_set_j_particle(clusterid, j-j_start, id[j],
			      time[j], timestep[j],
			      mass[j], k18, j6, a2, vel[j], pos[j]);
	}
    }
#endif
}

void idata::update_gpu(jdata& jd)
{
#ifdef GPU

    const char *in_function = "idata::update_gpu";
    if (DEBUG > 2 && jd.mpi_rank == 0) PRL(in_function);

    // Load corrected data for i-particles into the local GPUs.

    static int n = 0, j_start;
    static real a2[3], j6[3], k18[3] = {0,0,0};

    if (n == 0) {

	// Define my j-range.

	n = jd.get_nj()/jd.mpi_size;
	if (n*jd.mpi_size < jd.get_nj()) n++;
	j_start = jd.mpi_rank*n;
    }

    for (int i = 0; i < ni; i++) {
	int j = ilist[i];
	int curr_rank = j/n;
	if (curr_rank == jd.mpi_rank) {
	    for (int k = 0; k < 3; k++) {
		a2[k] = iacc[i][k]/2;
		j6[k] = ijerk[i][k]/6;
	    }
	    g6_set_j_particle(clusterid, j-j_start, iid[i],	// ?= id[j]
			      itime[i], itimestep[i],
			      imass[i], k18, j6, a2, ivel[i], ipos[i]);
	}
    }

#endif
}



void idata::get_partial_acc_and_jerk_on_gpu(jdata& jd,
					    bool pot)	// default = false
{
    // Compute the partial forces on all i-particles due to this
    // j-domain.

#ifdef GPU

    const char *in_function = "idata::get_partial_acc_and_jerk_on_gpu";
    if (DEBUG > 2 && jd.mpi_rank == 0) PRL(in_function);

    static int npipes = 0, localnj;
    static int *lnn;
    static real *h2, *lpot, *ldnn;
    static real2 a2, j6, lacc, ljerk;

    if (npipes == 0) {

	//Initialize local data.

	npipes = g6_npipes();
	h2 = new real[npipes];
	a2 = new real[npipes][3];
	j6 = new real[npipes][3];
	for (int i = 0; i < npipes; i++) h2[i] = jd.eps2;

	// Define my j-range.

	int n = jd.get_nj()/jd.mpi_size;
	if (n*jd.mpi_size < jd.get_nj()) n++;
	int j_start = jd.mpi_rank*n;
	int j_end = j_start + n;
	if (jd.mpi_rank == jd.mpi_size-1) j_end = jd.get_nj();
	localnj = j_end - j_start;

	// Define accumulator arrays.

	if (jd.mpi_size == 1) {
	    lpot = ipot;
	    lacc = iacc;
	    ljerk = ijerk;
	    lnn = inn;
	    ldnn = idnn;
	} else {
	    lpot = ppot;
	    lacc = pacc;
	    ljerk = pjerk;
	    lnn = pnn;
	    ldnn = pdnn;
	}
    }

    // Calculate the gravitational forces on the i-particles.

    g6_set_ti(clusterid, ti);
 
    for (int i = 0; i < ni; i += npipes) {
	int nni = npipes;
	if (ni - i < npipes) nni = ni - i;

	// Never compute the nearest neighbor index if NN = 0.  Always
	// compute the nearest neighbor index if NN = 1.  (Seems to
	// cost ~10%.  Maybe we don't need neighbors in most cases?)
	// Conditionally compute the nearest neighbor index if NN = 2
	// and we think a member of this group of particles is having
	// a close encounter.  Criterion is essentially that used by
	// Aarseth: dt < dtmin.

	bool want_neighbors = (NN == 1);

	for (int ii = 0; ii < nni; ii++) {
	    lnn[i+ii] = -1;
	    ldnn[i+ii] = huge;
	    for (int k = 0; k < 3; k++) {
		a2[ii][k] = old_acc[i+ii][k]/2;
		j6[ii][k] = old_jerk[i+ii][k]/6;
	    }
	    if (NN == 2 && itimestep[i+ii] < jd.dtmin)
		want_neighbors = true;
	}

	g6calc_firsthalf(clusterid, localnj, nni, iid+i,
			 ipos+i, ivel+i, a2, j6, ipot+i,
			 jd.eps2, h2);

	if (pot || !want_neighbors)

	    g6calc_lasthalf(clusterid, localnj, nni, iid+i,
			     ipos+i, ivel+i, jd.eps2, h2,
			     lacc+i, ljerk+i, lpot+i);
	else

	    g6calc_lasthalf2(clusterid, localnj, nni, iid+i,
			     ipos+i, ivel+i, jd.eps2, h2,
			     lacc+i, ljerk+i, lpot+i, lnn+i);

	jd.gpu_calls += 1;
	jd.gpu_total += nni;

	if (!pot && want_neighbors) {

	    // Note: The pnn array contains the GRAPE/GPU indices of
	    // the nearest neighbors.  The "index" sent to the GPU is
	    // just the j-index of the particle.  Computing the
	    // distances dnn requires fetching the corresponding
	    // j-data from main memory.  We should check whether this
	    // has any performance ramifications.

	    // Several things need to be improved here: (1) the
	    // distance pdnn is computed using jpos, not pred_pos, (2)
	    // ipos is used before correction, and (3) it is possible
	    // that the neighbor is on the i-list, in which case, we
	    // should use the corrected positions of both i and nn.
	    // Better to compute pdnn and complete the dnn reduction
	    // after the corrector is applied, using predicted j pos.
	    // How important this really is will depend on the use to
	    // which nn/dnn are ultimately put.  Maybe we only need
	    // refine the estimate if dnn is less than some critical
	    // value?  TODO...				(Steve 08/10)

	    for (int ii = 0; ii < nni; ii++) {

		// Note that the nn here is a GRAPE index, which is
		// the particle ID, not the j-index.  Convert it here
		// to a j-index.

		int id = lnn[i+ii];
		if (id >= 0) {		// should be true by construction...
		    int j = jd.inverse_id[id];
		    lnn[i+ii] = j;
		    ldnn[i+ii] = sqrt(pow(jd.pos[j][0]-ipos[i+ii][0],2)
				      + pow(jd.pos[j][1]-ipos[i+ii][1],2)
				      + pow(jd.pos[j][2]-ipos[i+ii][2],2));
		}
	    }
	}
    }

#endif
}



#include <vector>
#include <algorithm>

class rdata {
  public:
    int index;
    real r_sq;
};

inline bool operator < (const rdata& x, const rdata& y)
{
    return x.r_sq < y.r_sq;
}

void get_neighbors(jdata& jd, int knn)
{
    // Direct N^2 single-process neighbor computation.

    vector<rdata> rlist;
    rdata element;

    for (int j1 = 0; j1 < jd.get_nj(); j1++) {
	for (int j2 = 0; j2 < jd.get_nj(); j2++)
	    if (j2 != j1) {
		element.index = j1;
		element.r_sq = 0;
		for (int k = 0; k < 3; k++)
		    element.r_sq += pow(jd.pos[j2][k]-jd.pos[j1][k],2);
		rlist.push_back(element);
	    }
	sort(rlist.begin(), rlist.end());
	cout << "j = " << j1 << "  dnn = " << sqrt(rlist[0].r_sq)
	     << "  d12nn = " << sqrt(rlist[knn-1].r_sq)
	     << "  ratio = " << sqrt(rlist[knn-1].r_sq/rlist[0].r_sq)
	     << endl;
	rlist.clear();
    }
}

static inline void save_neighbors(jdata& jd, int j, int nlocal, int local[],
				 int nsave, int save[])
{
    // Reduce the local neighbors of particle j to a list of the nsave
    // nearest neighbors.

    vector<rdata> rlist;
    rdata element;
    for (int jl = 0; jl < nlocal; jl++) {
	int jj = local[jl];
	if (jj != j) {
	    element.index = jj;
	    element.r_sq = 0;
	    for (int k = 0; k < 3; k++)
		element.r_sq += pow(jd.pos[j][k]-jd.pos[jj][k],2);
	    rlist.push_back(element);
	}
    }
    sort(rlist.begin(), rlist.end());

    for (int ls = 0; ls < nsave; ls++)
	save[ls] = rlist[ls].index;	// note that the saved elements
					// are sorted by distance from j
#if 0
    cout << "j = " << j << "  dnn = " << sqrt(rlist[0].r_sq)
	 << "  d12nn = " << sqrt(rlist[nsave-1].r_sq)
	 << "  nlocal = " << nlocal << "  nsave = " << nsave
	 << endl;
    for (int ls = 0; ls < nsave; ls++) cout << save[ls] << " ";
    cout << endl;
#endif
}

void jdata::get_densities_on_gpu()	// under development
{
#ifdef GPU

    const char *in_function = "jdata::get_densities_on_gpu";
    if (DEBUG > 2 && mpi_rank == 0) PRL(in_function);

    static int npipes = 0, localnj, knn = 12, nbrmax,
	*nneighbors, *neighbors, *pneighbors, *itemp;
    static real *h2, (*a2)[3], (*j6)[3], *temp, (*temp3)[3];

    if (npipes == 0) {

	npipes = g6_npipes();
	//g6_set_neighbour_list_sort_mode(0);

	h2 = new real[npipes];
	a2 = new real[npipes][3];
	j6 = new real[npipes][3];
	itemp = new int[npipes];
	temp = new real[npipes];
	temp3 = new real[npipes][3];

	// Define my j-range.

	int n = nj/mpi_size;
	if (n*mpi_size < nj) n++;
	int j_start = mpi_rank*n;
	int j_end = j_start + n;
	if (mpi_rank == mpi_size-1) j_end = nj;
	localnj = j_end - j_start;

	nneighbors = new int[npipes];
	nbrmax = localnj;
	if (localnj < npipes) nbrmax = npipes;	// seems to be necessary
	neighbors = new int[npipes*nbrmax];
	if (2*(mpi_rank/2) == mpi_rank && mpi_rank < mpi_size-1)
	    pneighbors = new int[2*nj*knn];	// extra space for merging
	else
	    pneighbors = new int[nj*knn];
    }

    // get_neighbors(*this, knn);

    // Calculate partial neighbor lists of all particles relative to
    // my j-domain.  Assume that nearest neighbor distances are
    // current and usable.

    g6_set_ti(clusterid, system_time);
 
    for (int j = 0; j < nj; j += npipes) {
	int np = npipes;
	if (nj - j < npipes) np = nj - j;

	for (int jj = 0; jj < np; jj++) {
	    h2[jj] = 8*dnn[j+jj]*dnn[j+jj];	// coefficient is ~empirical
	    if (h2[jj] > 1) h2[jj] = 1;		// limit is ~empirical
	    for (int k = 0; k < 3; k++) {
		a2[jj][k] = acc[j+jj][k]/2;
		j6[jj][k] = jerk[j+jj][k]/6;
	    }
	}
	if (np < npipes)
	    for (int jj = np; jj < npipes; jj++)
		h2[jj] = tiny;

	bool ok = false;
	while (!ok) {

	    if (DEBUG) {
		cout << "calling g6calc";
		if (mpi_rank > 0) cout << " on " << mpi_rank;
		cout << ": ";
		PRC(j); PRL(np);
	    }

	    g6calc_firsthalf(clusterid, localnj, np, id+j,
			     pos+j, vel+j, a2, j6, pot+j,
			     eps2, h2);
	    g6calc_lasthalf2(clusterid, localnj, np, id+j,
			     pos+j, vel+j, eps2, h2,
			     temp3, temp3, temp, itemp);

	    // Extract neighbor lists and make sure there are at least
	    // knn+1 particles on each (note that, unlike the GRAPE,
	    // the GPU neighbor list for particle j includes j).
	    //
	    // *** To be clarified, as the details have changed
	    //     between sapporo 1.5 and 1.6. ***
	    //
	    // A better strategy would be to process acceptable lists
	    // as we find them and move new particles in, as in kira.

	    ok = true;
	    int status = g6_read_neighbour_list(clusterid);

	    if (status) {

		ok = false;
		cout << "g6_read_neighbour_list";
		if (mpi_size > 1) cout << " on " << mpi_rank;
		cout << ": ";
		PRL(status);

		// Reduce the largest h2 values.

		real h2min = huge, h2max = 0, h2bar = 0;
		int jmin, jmax;
		for (int jj = 0; jj < np; jj++) {
		    if (h2[jj] < h2min) {h2min = h2[jj]; jmin = jj;}
		    if (h2[jj] > h2max) {h2max = h2[jj]; jmax = jj;}
		    h2bar += h2[jj];
		}
		h2bar /= np;
		for (int jj = 0; jj < np; jj++) {
		    if (h2[jj] > h2bar) h2[jj] = h2bar + 0.5*(h2[jj]-h2bar);
		}
		if (DEBUG) {
		    jmax += j;
		    int njmax = 0;
		    for (int jj = 0; jj < nj; jj++)
			if (jj != jmax) {
			    real r2 = 0;
			    for (int k = 0; k < 3; k++)
				r2 += pow(pos[jmax][k]-pos[jj][k], 2);
			    if (r2 < h2max) njmax++;
			}
		    if (mpi_size > 1) PRC(mpi_rank);
		    PRC(h2min); PRC(h2max); PRC(jmax); PRL(njmax);
		    cout << "decreased h for some pipes" << endl << flush;
		}

	    } else {

		for (int jj = 0; jj < np; jj++) {
		    status = g6_get_neighbour_list(clusterid, jj, nbrmax,
						   nneighbors+jj,
						   neighbors+jj*nbrmax);

		    // *** TODO: lists contain particle IDs, not
		    // *** j-indices.  Must convert before using...

		    if (status)	{

			ok = false;
			cout << "g6_get_neighbour_list";
			if (mpi_size > 1) cout << " on " << mpi_rank;
			cout << ": ";
			PRL(status);

			// Reduce h2.

			h2[jj] /= 2;

			if (DEBUG)
			    cout << "decreased h for " << id[j+jj]
				 << " to " << sqrt(h2[jj])
				 << "  dnn = " << dnn[j+jj]
				 << endl;

		    } else {

			if (nneighbors[jj] < knn+1) {

			    ok = false;
			    h2[jj] *= pow(2*knn/(real)nneighbors[jj],
					  0.666667);

			    if (DEBUG)
				cout << "increased h for " << id[j+jj]
				     << " to " << sqrt(h2[jj])
				     << "  dnn = " << dnn[j+jj]
				     << "  nneighbors = " << nneighbors[jj]
				     << endl;
			}
		    }
		}
	    }

	    if (!ok && DEBUG) cout << "retrying" << endl << flush;
	}

#if 0
	// Check the integrity of the neighbor lists.

	for (int jj = 0; jj < np; jj++) {
	    int nnbr = nneighbors[jj];
	    for (int jnbr1 = 0; jnbr1 < nnbr; jnbr1++)
		for (int jnbr_sq = jnbr1+1; jnbr_sq < nnbr; jnbr_sq++)
		    if (neighbors[jj*nbrmax+jnbr1]
			 == neighbors[jj*nbrmax+jnbr_sq])
			cout << "duplicate neighbor "
			     << neighbors[jj*nbrmax+jnbr1]
			     << " for " << j+jj
			     << " at " << jnbr1 << " and " << jnbr_sq
			     << " nnbr = " << nnbr
			     << endl;
	}
#endif

	// All the neighbor lists are acceptable.  Reduce them to knn
	// nearest neighbors and save them.

	for (int jj = 0; jj < np; jj++)
	    save_neighbors(*this, j+jj, nneighbors[jj], neighbors+jj*nbrmax,
			   knn, pneighbors+(j+jj)*knn);
    }

    mpi_comm.Barrier();

    // Each process now has a partial (p)neighbor list for all nj
    // j-particles relative to its own j-domain, of length knn per
    // j-particle.  Combine these partial lists and compute the
    // densities.

    // Strategy: even ranked nodes receive and merge data from the odd
    // nodes.  Then rank --> rank/2 and iterate until node 0 has the
    // final list.

#if 1
    int irank = mpi_rank, irank2 = mpi_rank/2, offset = 1, s = mpi_size;
    while (s > 1) {

	// Combine lists in pairs.  Even irank receives from irank+1;
	// odd irank sends to irank-1; an even irank at the end does
	// nothing.

	if (2*irank2 < irank) {

	    // Send data to rank-offset...

	    cout << mpi_rank << " sending neighbors to" << mpi_rank-offset
		 << endl << flush;
	    mpi_comm.Send(pneighbors, nj*knn, MPI_INT,
			  mpi_rank-offset, 42);
	    cout << mpi_rank << " send done" << endl << flush;

	    // ...and become inactive.

	    s = 0;

	} else {

	    if (irank < s-1) {

		// Receive data from mpi_rank+offset.

		cout << mpi_rank << " receiving neighbors from"
		     << mpi_rank+offset
		     << endl << flush;
		mpi_comm.Recv(pneighbors+nj*knn, nj*knn, MPI_INT,
			      mpi_rank+offset, 42);
		cout << mpi_rank << " receive done" << endl << flush;

		// Merge lists.

		int nbrlist[2*knn];
		for (int j = 0; j < nj; j++) {
		    for (int k = 0; k < knn; k++) {
			nbrlist[k] = pneighbors[j*knn+k];
			nbrlist[knn+k] = pneighbors[(nj+j)*knn+k];
		    }
		    save_neighbors(*this, j, 2*knn, nbrlist,
				   knn, pneighbors+j*knn);
		}
	    }

	    // Update counters and continue.

	    irank = irank2;
	    irank2 = irank/2;
	    offset *= 2;
	    s = (s+1)/2;
	}

	PRC(mpi_rank); PRL(s);
	mpi_comm.Barrier();
    }
#endif

#endif
}
