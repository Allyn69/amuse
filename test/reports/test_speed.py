from amuse.legacy.support.core import *

from amuse.support.data import core
from amuse.support.units import nbody_system
from amuse.support.units import units
from amuse.legacy.support import channel

from path_to_test_results import get_path_to_test_results
from amuse.legacy.support import create_c

import subprocess
import os
import numpy
import time

codestring = """

#include <stdio.h>
#include <mpi.h>
#include <new>
#include <iostream>


struct data {
    double x;
    double y;
    double z;
};

int number_of_points_in_one_dimension = 0;
data * model = 0;

int set_data(int index, double vx, double vy, double vz)
{
    if(!model)
    {
        return -1;
    }
    
    if(index > (number_of_points_in_one_dimension * number_of_points_in_one_dimension * number_of_points_in_one_dimension))
    {
        return -2;
    }
    data & m = model[index];
    m.x = vx;
    m.y = vy;
    m.z = vz;
    return 0;
}


int get_data(int index, double * vx, double  * vy, double  * vz)
{
    double data_in[6], data_out[6];
    int status_in,status_out;
    if(!model)
    {
        return -1;
    }
    
    if(index > (number_of_points_in_one_dimension * number_of_points_in_one_dimension * number_of_points_in_one_dimension))
    {
        return -2;
    }
    data & m = model[index];
    *vx = m.x;
    *vy = m.y;
    *vz = m.z;
    data_in[0] = data_in[1] = data_in[2] = 0.0;
    data_in[3] = data_in[4] = data_in[5] = 0.0;
    data_out[0] = data_out[1] = data_out[2] = 0.0;
    data_out[3] = data_out[4] = data_out[5] = 0.0;
    status_in = status_out = 0;
    /*
    MPI::COMM_WORLD.Allreduce(data_in, data_out, 6, MPI::DOUBLE,MPI::SUM);
    MPI::COMM_WORLD.Barrier();
    MPI::COMM_WORLD.Allreduce(&status_in, &status_out, 1, MPI::DOUBLE,MPI::SUM);
    */
    return 0;
}
  
int step() 
{
    if(!model) {
        return -1;
    }
    for(int xindex ; xindex < number_of_points_in_one_dimension; xindex++)
    {
        for(int yindex ; yindex < number_of_points_in_one_dimension; yindex++)
        {
            for(int zindex ; zindex < number_of_points_in_one_dimension; zindex++)
            {
                int index = xindex * number_of_points_in_one_dimension * number_of_points_in_one_dimension;
                index += yindex * number_of_points_in_one_dimension;
                index += zindex;
                
                model[index].x = index;
                model[index].y = model[index].x / (1.0 + model[index].y);
                model[index].z = model[index].x  * model[index].y / (model[index].z + 1e-7);
            }
        }
    }
    return 0;
}    
  
int set_number_of_points_in_one_dimension(int value)
{
    if(model) {
        delete model;
    }
    
    try {
        model = new data[value*value*value];
    } catch (std::bad_alloc &e) {
        number_of_points_in_one_dimension = 0;
        return -1;
    }
    number_of_points_in_one_dimension = value;
    
    return 0;
    
}

int reset()
{
    if(model) {
        delete model;
    }
    model = 0;
    return 0;
}
"""

class TestCode(LegacyInterface):
    
    def __init__(self, exefile):
        LegacyInterface.__init__(self, exefile)
         
         
    @legacy_function
    def set_number_of_points_in_one_dimension():
        """
        Set the set number of points in one dimension (N), the total model
        size will be qubed (N*N*N)
        """
        function = LegacyFunctionSpecification()  
        function.addParameter('value',
            dtype='int32',
            direction=function.IN,
            description =  
                "The number of points in one direction")
        function.result_type = 'int32'
        return function  
        
    @legacy_function
    def step():
        """
        Do one step over the N * N * N grid
        """
        function = LegacyFunctionSpecification()  
        function.result_type = 'int32'
        return function
        
    
    @legacy_function
    def reset():
        """
        Restore the model to its original state
        """
        function = LegacyFunctionSpecification()  
        function.result_type = 'int32'
        return function  
        
    @legacy_function
    def set_data():
        """
        set example vector data
        """
        function = LegacyFunctionSpecification()  
        function.addParameter('index',
            dtype='int32',
            direction=function.IN,
            description =  
                "index in the array in range 0 <= index < (N*3)")
        function.addParameter('vx',
            dtype='float64',
            direction=function.IN,
            description =  
                "x component of the vector")
        function.addParameter('vy',
            dtype='float64',
            direction=function.IN,
            description =  
                "y component of the vector")
        function.addParameter('vz',
            dtype='float64',
            direction=function.IN,
            description =  
                "z component of the vector")
        function.can_handle_array = True
        function.result_type = 'int32'
        return function
        
    @legacy_function
    def get_data():
        """
        retrieve example vector data
        """
        function = LegacyFunctionSpecification()  
        function.addParameter('index',
            dtype='int32',
            direction=function.IN,
            description =  
                "index in the array in range 0 <= index < (N*3)")
        function.addParameter('vx',
            dtype='float64',
            direction=function.OUT,
            description =  
                "x component of the vector")
        function.addParameter('vy',
            dtype='float64',
            direction=function.OUT,
            description =  
                "y component of the vector")
        function.addParameter('vz',
            dtype='float64',
            direction=function.OUT,
            description =  
                "z component of the vector")
        function.can_handle_array = True
        function.result_type = 'int32'
        return function  



class RunSpeedTests(object):
    
    def __init__(self):
        self.number_of_gridpoints = [8]
        
    def c_compile(self, objectname, string):
        process = subprocess.Popen(
            ["mpicxx", "-g", "-x", "c++", "-c",  "-o", objectname, "-",],
            stdin = subprocess.PIPE,
            stdout = subprocess.PIPE,
            stderr = subprocess.PIPE
        )
        stdout, stderr = process.communicate(string)
        if process.returncode != 0:
            raise Exception("Could not compile {0}, error = {1}".format(objectname, stderr))
            
    def cxx_compile(self, objectname, string):
        process = subprocess.Popen(
            ["mpicxx", "-g","-x","c++", "-c",  "-o", objectname, "-",],
            stdin = subprocess.PIPE,
            stdout = subprocess.PIPE,
            stderr = subprocess.PIPE
        )
        stdout, stderr = process.communicate(string)
        if process.returncode != 0:
            raise Exception("Could not compile {0}, error = {1}".format(objectname, stderr))
            
    
    def c_build(self, exename, objectnames):
        arguments = ["mpicxx"]
        arguments.extend(objectnames)
        arguments.append("-g")
        arguments.append("-o")
        arguments.append(exename)
        
        process = subprocess.Popen(
            arguments,
            stdin = subprocess.PIPE,
            stdout = subprocess.PIPE,
            stderr = subprocess.PIPE
        )
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            raise Exception("Could not build {0}, error = {1}".format(exename, stderr))
    
    def build_worker(self):
        
        path = os.path.abspath(get_path_to_test_results())
        codefile = os.path.join(path,"code.o")
        interfacefile = os.path.join(path,"interface.o")
        self.exefile = os.path.join(path,"c_worker")
        
        self.c_compile(codefile, codestring)
        
        uc = create_c.MakeACHeaderStringOfAClassWithLegacyFunctions()
        uc.class_with_legacy_functions = TestCode
        uc.make_extern_c = False
        header =  uc.result
        
        
        uc = create_c.MakeACStringOfAClassWithLegacyFunctions()
        uc.class_with_legacy_functions = TestCode
        code =  uc.result
        
        string = '\n\n'.join([header, code])
        
        #print string
        
        self.cxx_compile(interfacefile, string)
        self.c_build(self.exefile, [interfacefile, codefile] )
    
    def start(self):
        self.build_worker()
        
        
        for number_of_points_in_one_dimension in self.number_of_gridpoints:
            number_of_seconds, total_number_of_points, number_of_mb_per_second = self.run(number_of_points_in_one_dimension)
    
            print ', '.join([
                str(number_of_points_in_one_dimension),
                str(total_number_of_points),
                str(number_of_seconds),
                str(number_of_mb_per_second),
            ])
                
    def run(self, number_of_points_in_one_dimension):
    
        instance = TestCode(self.exefile)

        total_number_of_points = number_of_points_in_one_dimension ** 3
        number_of_bytes = 4 + 8 + 8 + 8
        total_number_of_bytes = total_number_of_points * (number_of_bytes + 4)
        indices = numpy.array(range(total_number_of_points), dtype='int32')

        data_x = numpy.array(range(total_number_of_points), dtype='float64')
        data_y = numpy.array(range(total_number_of_points), dtype='float64')
        data_z = numpy.array(range(total_number_of_points), dtype='float64')

        errorcode = instance.set_number_of_points_in_one_dimension(number_of_points_in_one_dimension)
        if errorcode < 0:
            raise Excption("Could not allocate memory")

        t0 = time.time()
        instance.set_data(indices, data_x, data_y, data_z)
        t1 = time.time()
        dt = t1 - t0
        mbytes_per_second = total_number_of_bytes / dt / (1000.0 * 1000.0)
        instance.reset()

        del instance
        
        return dt, total_number_of_points, mbytes_per_second        
        
        
def test_speed():
    x = RunSpeedTests()
    x.number_of_gridpoints = [8]
    x.start()

if __name__ == '__main__':
    #channel.MessageChannel.DEBUGGER = channel.MessageChannel.DDD
    x = RunSpeedTests()
    x.number_of_gridpoints = [8, 16, 32, 64, 128, 192]
    x.start()
