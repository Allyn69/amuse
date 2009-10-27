__revision__ = "$Id:$"

import sys, os, re, subprocess
from stat import ST_MODE
from distutils import sysconfig
from distutils.core import Command
from distutils.dep_util import newer
from distutils.util import convert_path
from distutils import log
from distutils import spawn
from subprocess import call, Popen, PIPE
from numpy.distutils import fcompiler
# check if Python is called on the first line with this expression
first_line_re = re.compile('^#!.*python[0-9.]*([ \t].*)?$')

class LegacyCommand(Command):
    user_options = [
        ('legacy-dir', 'd', "directory containing legacy codes"),
        ]

    boolean_options = ['force']

    def initialize_options (self):
        self.legacy_dir = None
        self.amuse_src_dir =  os.path.join('src','amuse')
        self.environment = {}
        self.environment_notset = {}
        self.found_cuda = False
        self.found_sapporo = False
        
    def finalize_options (self):
        if self.legacy_dir is None:
            self.legacy_dir = os.path.join(self.amuse_src_dir,'legacy')
        
        self.set_fortran_variables()
        self.set_cuda_variables()
        self.set_libdir_variables()
        
    def set_fortran_variables(self):
        if 'FORTRAN' in os.environ:
            self.environment['FORTRAN'] = os.environ['FORTRAN']
            return
        
        if 'FC' in os.environ:
            self.environment['FORTRAN'] = os.environ['FC']
            return
            
        if 'FORT' in os.environ:
            self.environment['FORTRAN'] = os.environ['FORT']
            return

        compiler = fcompiler.new_fcompiler(requiref90=True)
        fortran_executable = compiler.executables['compiler_f90'][0]
        self.environment['FORTRAN'] = fortran_executable
    
    def set_cuda_variables(self):
        dir = spawn.find_executable('nvcc')
        if dir is None:
            self.found_cuda = False
            return
        cuda_dir = os.path.dirname(os.path.dirname(dir))
        self.environment['CUDA_LIBDIRS'] = '-L'+cuda_dir+'/lib'
        self.environment['CUDA_LIBS'] = '-lcudart'
        self.found_cuda = True

    
    def set_libdir_variables(self):
        for varname in ('SAPPORO_LIBDIRS', 'GRAPE6_LIBDIRS'):
            if varname in os.environ:
                self.environment[varname] = os.environ[varname]
            else:
                self.environment_notset[varname] ='-L<directory>'
     
    
            
    def subdirs_in_legacy_dir(self):
        names = os.listdir(self.legacy_dir)
        for name in names:
            path = os.path.join(self.legacy_dir, name)
            if os.path.isdir(path):
                yield path
                
    def makefile_paths(self):
        for x in self.subdirs_in_legacy_dir():
            for name in ('makefile', 'Makefile'):
                makefile_path = os.path.join(x, name)
                if os.path.exists(makefile_path):
                    yield x
    

class BuildLegacy(LegacyCommand):

    description = "build interfaces to legacy codes"
    
    def run (self):
        not_build = []
        build = []
        environment = os.environ.copy()
        environment.update(self.environment)
        for x in list(self.makefile_paths()):
            self.announce("building " + x)
            shortname = x[len(self.legacy_dir) + 1:]
            returncode = call(['make','-C', x, 'all'], env = environment)
            if returncode == 2:
                not_build.append(shortname)
            else:
                build.append(shortname)
            
            special_targets = self.get_special_targets(x, environment)
            for target,target_name in special_targets:
                self.announce("building " + x + " version: " + target_name)
                returncode = call(['make','-C', x, target], env = environment)
                if returncode == 2:
                    not_build.append(shortname + " - " + target_name)
                else:
                    build.append(shortname + " - " + target_name)
                
        sorted_keys = sorted(self.environment_notset.keys())
        print
        print "Environment variables not set"
        print "============================="
        for x in sorted_keys:
            print "%s\t%s" % (x , self.environment_notset[x] )
        print
        sorted_keys = sorted(self.environment.keys())
        print
        print "Environment variables"
        print "====================="
        for x in sorted_keys:
            print "%s\t%s" % (x , self.environment[x] )
        print
        if not_build:
            print
            print
            print "legacy codes not build (because of errors):"
            print "==========================================="
            for x in not_build:
                print '*' , x
        if build:
            print
            print
            print "legacy codes build"
            print "=================="
            for x in build:
                print '*' , x
        
    def get_special_targets(self, directory, environment):
        process = Popen(['make','-p' , '-C', directory], env = environment, stdout = PIPE, stderr = PIPE)
        stdoutstring, stderrstring = process.communicate()
        print stdoutstring
        print stderrstring
        lines = stdoutstring.splitlines()
        result = []
        for line in lines:
            if line.startswith('muse_worker_gpu:'):
                result.append(('muse_worker_gpu', 'GPU',))
            if line.startswith('muse_worker_grape:'):
                result.append(('muse_worker_grape', 'GRAPE6',))
        return result
        
 
class CleanLegacy(LegacyCommand):

    description = "clean build products in legacy codes"

    def run (self):
        for x in self.makefile_paths():
            self.announce("cleaning " + x)
            call(['make','-C', x, 'clean'])
            
            
            
            
            
    
            
           
            
            
            
            
    
            
