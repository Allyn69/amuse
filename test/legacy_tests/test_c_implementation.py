from amuse.legacy.support.core import *

from amuse.support.data import core
from amuse.support.units import nbody_system
from amuse.support.units import units
from amuse.legacy.support import channel

from legacy_support import TestWithMPI
from path_to_test_results import get_path_to_test_results
from amuse.legacy.support import create_c

import subprocess
import os

codestring = """

int echo_int(int int_in, int * int_out) {
    *int_out = int_in;
    return 0;
}

int echo_double(double in, double * out) {
    *out = in;
    return 0;
}

int echo_float(float in, float * out) {
    *out = in;
    return 0;
}
int echo_string(char * in, char ** out) {
    *out = in;
    return 0;
}

int echo_strings(char ** inout1, char ** inout2) {
    char * tmp;
    tmp = *inout1;
    *inout1 = *inout2;
    *inout2 = tmp;
    
    return 0;
}
"""

class ForTestingInterface(LegacyInterface):
    
    def __init__(self, exefile):
        LegacyInterface.__init__(self, exefile)

    @legacy_function
    def echo_int():
        function = LegacyFunctionSpecification()  
        function.addParameter('int_in', dtype='int32', direction=function.IN)
        function.addParameter('int_out', dtype='int32', direction=function.OUT)
        function.result_type = 'int32'
        function.can_handle_array = True
        return function     
        
    @legacy_function
    def echo_double():
        function = LegacyFunctionSpecification()  
        function.addParameter('double_in', dtype='float64', direction=function.IN)
        function.addParameter('double_out', dtype='float64', direction=function.OUT)
        function.result_type = 'int32'
        function.can_handle_array = True
        return function  
        
    @legacy_function
    def echo_float():
        function = LegacyFunctionSpecification()  
        function.addParameter('float_in', dtype='float32', direction=function.IN)
        function.addParameter('float_out', dtype='float32', direction=function.OUT)
        function.result_type = 'int32'
        function.can_handle_array = True
        return function  
          
    @legacy_function
    def echo_string():
        function = LegacyFunctionSpecification()  
        function.addParameter('string_in', dtype='string', direction=function.IN)
        function.addParameter('string_out', dtype='string', direction=function.OUT)
        function.result_type = 'int32'
        function.can_handle_array = True
        return function  
          
    @legacy_function
    def echo_strings():
        function = LegacyFunctionSpecification()  
        function.addParameter('string_inout1', dtype='string', direction=function.INOUT)
        function.addParameter('string_inout2', dtype='string', direction=function.INOUT)
        function.result_type = 'int32'
        function.can_handle_array = True
        return function    
    
    #@legacy_function
    def return_string():
        function = LegacyFunctionSpecification()  
        function.addParameter('string_in', dtype='string', direction=function.IN)
        function.result_type = 'string'
        function.can_handle_array = True
        return function  



class TestInterface(TestWithMPI):
    
    def c_compile(self, objectname, string):
        process = subprocess.Popen(
            ["mpicc", "-x", "c", "-c",  "-o", objectname, "-",],
            stdin = subprocess.PIPE,
            stdout = subprocess.PIPE,
            stderr = subprocess.PIPE
        )
        stdout, stderr = process.communicate(string)
        if process.returncode != 0:
            raise Exception("Could not compile {0}, error = {1}".format(objectname, stderr))
            
    def cxx_compile(self, objectname, string):
        process = subprocess.Popen(
            ["mpicxx","-x","c++", "-c",  "-o", objectname, "-",],
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
        uc.class_with_legacy_functions = ForTestingInterface
        header =  uc.result
        
        
        uc = create_c.MakeACStringOfAClassWithLegacyFunctions()
        uc.class_with_legacy_functions = ForTestingInterface
        code =  uc.result
        
        string = '\n\n'.join([header, code])
        
        #print string
        
        self.cxx_compile(interfacefile, string)
        self.c_build(self.exefile, [interfacefile, codefile] )
    
    def setUp(self):
        super(TestInterface, self).setUp()
        print "building"
        self.build_worker()
        
    def test1(self):
        instance = ForTestingInterface(self.exefile)
        int_out, error = instance.echo_int(10)
        del instance
        self.assertEquals(int_out, 10)
        self.assertEquals(error, 0)
        
    def test2(self):
        instance = ForTestingInterface(self.exefile)
        out, error = instance.echo_double(4.0)
        del instance
        self.assertEquals(out, 4.0)
        self.assertEquals(error, 0)
        
        
    def test3(self):
        instance = ForTestingInterface(self.exefile)
        input = [1,2,3,4]
        output, errors = instance.echo_int(input)
        del instance
        self.assertEquals(len(errors),4)
        for actual, expected in zip(output, input):
            self.assertEquals(actual, expected)
            
    def test4(self):
        instance = ForTestingInterface(self.exefile)
        input = [1.0,2.1,3.3,4.2]
        output, errors = instance.echo_double(input)
        del instance
        self.assertEquals(len(errors),4)
        for actual, expected in zip(output, input):
            self.assertEquals(actual, expected)
            
        
    def test5(self):
        instance = ForTestingInterface(self.exefile)
        out, error = instance.echo_float(4.0)
        del instance
        self.assertEquals(out, 4.0)
        self.assertEquals(error, 0)
        
    def test6(self):
        
        instance = ForTestingInterface(self.exefile)
        out, error = instance.echo_string("abc")
        del instance
        self.assertEquals(error, 0)
        self.assertEquals(out[0], "abc")

    def test7(self):
        instance = ForTestingInterface(self.exefile)
        out, error = instance.echo_string(["abc","def"])
        del instance
        
        self.assertEquals(error[0], 0)
        self.assertEquals(error[1], 0)
        self.assertEquals(out[0], "abc")
        self.assertEquals(out[1], "def")

    def test8(self):
        instance = ForTestingInterface(self.exefile)
        out1, out2, error = instance.echo_strings("abc","def")
        del instance
        
        self.assertEquals(error, 0)
        self.assertEquals(out1[0], "def")
        self.assertEquals(out2[0], "abc")
      
    def test9(self):
        instance = ForTestingInterface(self.exefile)
        str1_out, str2_out, error = instance.echo_strings(["abc", "def"], ["ghi", "jkl"])
        del instance
        
        self.assertEquals(error[0], 0)
        self.assertEquals(error[1], 0)
        self.assertEquals(str1_out[0], "ghi")
        self.assertEquals(str1_out[1], "jkl")
        self.assertEquals(str2_out[0], "abc")
        self.assertEquals(str2_out[1], "def")
      
    def xtest10(self):
        instance = ForTestingInterface(self.exefile)
        out = instance.return_string("abc")
        del instance
        
        self.assertEquals(out[0], "abc")

