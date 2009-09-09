

SUBROUTINE run_loop
  INCLUDE 'mpif.h'
  integer :: rank, parent, ioerror
  integer :: must_run_loop
  integer mpiStatus(MPI_STATUS_SIZE,4)
  
  integer header(5)
  
  integer :: tag_in, tag_out
  
  integer :: len_in, len_out
  integer integers_in(255)
  integer integers_out(255)
  integer :: number_of_integers_out, number_of_integers_in
  real*8 doubles_in(255)
  real*8 doubles_out(255)
  integer :: number_of_doubles_out, number_of_doubles_in
  real*4 floats_in(255)
  real*4 floats_out(255)
  integer :: number_of_floats_out, number_of_floats_in
  
  call MPI_COMM_GET_PARENT(parent, ioerror)
  call MPI_COMM_RANK(parent, rank, mpierror)
  
  must_run_loop = 1
  
  do while (must_run_loop .eq. 1)
    call MPI_BCast(header, 5, MPI_INTEGER, 0, parent,&
      ioerror)
    
    tag_in = header(1)
    
    len_in = header(2)
    number_of_doubles_in =  header(3)
    number_of_integers_in =  header(4)
    number_of_floats_in =  header(5)
    
    tag_out = tag_in
    len_out = len_in
    number_of_doubles_out = 0
    number_of_integers_out = 0
    number_of_floats_out = 0
    
    if (number_of_doubles_in .gt. 0) then
      call MPI_BCast(doubles_in, number_of_doubles_in, &
        MPI_DOUBLE_PRECISION, 0, parent,&
        ioError);
    end if
    if (number_of_integers_in .gt. 0) then
      call MPI_BCast(integers_in, number_of_integers_in, &
        MPI_INTEGER, 0, parent,&
        ioError);
    end if
    if (number_of_floats_in .gt. 0) then
      call MPI_BCast(floats_in, number_of_floats_in, &
        MPI_SINGLE_PRECISION, 0, parent,&
        ioError);
    end if
    
    SELECT CASE (tag_in)
      CASE(0)
        must_run_loop = 0
      CASE(1)
        integers_out(1) = setup_module( &
        )
        number_of_integers_out = 1
        
      CASE(2)
        integers_out(1) = cleanup_module( &
        )
        number_of_integers_out = 1
        
      CASE(3)
        integers_out(1) = initialize_particles( &
          doubles_in(1) &
        )
        number_of_integers_out = 1
        
      CASE(4)
        integers_out(1) = reinitialize_particles( &
        )
        number_of_integers_out = 1
        
      CASE(5)
        integers_out(1) = add_particle( &
          integers_in(1) ,&
          doubles_in(1) ,&
          doubles_in(2) ,&
          doubles_in(3) ,&
          doubles_in(4) ,&
          doubles_in(5) ,&
          doubles_in(6) ,&
          doubles_in(7) ,&
          doubles_in(8) &
        )
        number_of_integers_out = 1
        
      CASE(6)
        integers_out(1) = evolve( &
          doubles_in(1) ,&
          integers_in(1) &
        )
        number_of_integers_out = 1
        
      CASE(7)
        integers_out(1) = get_number( &
        )
        number_of_integers_out = 1
        
      CASE(8)
        CALL get_state( &
          integers_in(1) ,&
          doubles_out(1) ,&
          doubles_out(2) ,&
          doubles_out(3) ,&
          doubles_out(4) ,&
          doubles_out(5) ,&
          doubles_out(6) ,&
          doubles_out(7) ,&
          doubles_out(8) &
        )
        number_of_doubles_out = 8
        
      CASE(9)
        integers_out(1) = set_mass( &
          integers_in(1) ,&
          doubles_in(1) &
        )
        number_of_integers_out = 1
        
      CASE DEFAULT
        tag_out = -1
    END SELECT
    
    header(1) = tag_out
    header(2) = len_out
    header(3) = number_of_doubles_out
    header(4) = number_of_integers_out
    header(5) = number_of_floats_out
    
    call MPI_SEND(header, 5, MPI_INTEGER, 0, 999, &
      parent, mpierror);
    
    if (number_of_doubles_out .gt. 0) then
      call MPI_SEND(doubles_out, number_of_doubles_out, &
        MPI_DOUBLE_PRECISION, 0, 999, &
        parent, mpierror);
    end if
    if (number_of_integers_out .gt. 0) then
      call MPI_SEND(integers_out, number_of_integers_out, &
        MPI_INTEGER, 0, 999, &
        parent, mpierror);
    end if
    if (number_of_floats_out .gt. 0) then
      call MPI_SEND(floats_out, number_of_floats_out, &
        MPI_SINGLE_PRECISION, 0, 999, &
        parent, mpierror);
    end if
  end do
  return
end subroutine

program muse_worker
  INCLUDE 'mpif.h'
  call MPI_INIT(mpierror)
  
  call run_loop()
  
  call MPI_FINALIZE(mpierror)
end program muse_worker
