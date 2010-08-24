#ifdef __cplusplus
extern "C" {
#endif

// public methods
int enable_stopping_condition(int type);
int get_number_of_stopping_conditions_set(int * result);
int is_stopping_condition_set(int type, int * result);
int is_stopping_condition_enabled(int type, int * result);
int disable_stopping_condition(int type);
int has_stopping_condition(int type, int * result);
int get_stopping_condition_info(int index, int * index_of_the_condition);
int get_stopping_condition_particle_index(int index, int index_in_the_condition, int * index_of_particle);
int set_stopping_condition_timeout_parameter(double value);
int get_stopping_condition_timeout_parameter(double * value);
int set_stopping_condition_steps_parameter(int value);
int get_stopping_condition_steps_parameter(int *value);

#ifdef __cplusplus
}
#endif

// private methods
#define MAX_NUMBER_OF_SIMULTANIOS_CONDITIONS_SET 100
#define MAX_NUMBER_OF_PARTICLES_PER_INDEX        10

#define COLLISION_DETECTION  0
#define PAIR_DETECTION       1
#define ESCAPER_DETECTION    2
#define TIMEOUT_DETECTION    3
#define STEPS_DETECTION      4


#define COLLISION_DETECTION_BITMAP  1
#define PAIR_DETECTION_BITMAP       2
#define ESCAPER_DETECTION_BITMAP    4
#define TIMEOUT_DETECTION_BITMAP    8
#define STEPS_DETECTION_BITMAP      16

#ifdef __cplusplus
extern "C" {
#endif

extern long enabled_conditions;
extern long supported_conditions;
extern long set_conditions;

extern double timeout_parameter;
extern long steps_parameter;

int reset_stopping_conditions();
int next_index_for_stopping_condition();
int set_stopping_condition_info(int index, int type);
int set_stopping_condition_particle_index(int index, int index_in_the_condition, int index_of_particle);


int mpi_setup_stopping_conditions();
int mpi_distribute_stopping_conditions();
int mpi_collect_stopping_conditions();

#ifdef __cplusplus
}
#endif
