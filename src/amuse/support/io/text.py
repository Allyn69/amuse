from amuse.support.data import core
from amuse.support.core import late
from amuse.support.units import units
from amuse.support.io import base

import re

class LineBasedFileCursor(object):
    
    def __init__(self, file):
        self._line = None
        self.file = file
        self.read_next_line()
        
    def read_next_line(self):
        try:
            line = self.file.next()
            self._line = line.rstrip('\r\n')
        except StopIteration:
            self._line = None

    def forward(self):
        if not self.is_at_end():
            self.read_next_line()
    
    def line(self):
        return self._line
        
    def is_at_end(self):
        return self._line is None
        
        
class TableFormattedText(base.FileFormatProcessor):
    """
    Process a text file containing a table of values separated by a predefined character
    """
    
    provided_formats = ['txt']
    
    def __init__(self, filename = None, stream = None, set = None, format = None):
        base.FileFormatProcessor.__init__(self, filename, set, format)
        
        self.filename = filename
        self.stream = stream
        self.set = set
    
    def forward(self):
        line = selfdata_file.readline()
        return line.rstrip('\r\n')
        
    def split_into_columns(self, line):
        if self.column_separator == ' ':
            return line.split()
        else:
            return line.split(self.column_separator)
    
    def load(self):
        if self.stream is None:
            self.stream = open(self.filename, "r")
            close_function = self.stream.close  
        else:
            close_function = lambda : None
            
        try:
            return self.load_from_stream()
        finally:
            close_function()
        
    def load_from_stream(self):
        self.cursor = LineBasedFileCursor(self.stream)
        self.read_header()
        self.read_rows()
        self.read_footer()
        return self.set
        
    def store(self):
        
        if self.stream is None:
            self.stream = open(self.filename, "w")
            close_function = self.stream.close 
        else:
            close_function = lambda : None
            
        try:
            return self.store_on_stream()
        finally:
            close_function()
            
    def store_on_stream(self):
        self.write_header()
        self.write_rows()
        self.write_footer()
        
    @base.format_option
    def attribute_names(self):
        "list of the names of the attributes to load or store"
        if self.set is None:
            return map(lambda x : "col({0})".format(x), range(len(self.quantities)))
        else:
            return self.set.stored_attributes()
        
    @base.format_option
    def attribute_types(self):
        "list of the types of the attributes to store"
        quantities = self.quantities
        if self.quantities:
            return map(lambda x : x.unit.to_simple_form(), quantities)
        elif self.set is None:
            return map(lambda x : units.none, self.attribute_names)
    
    @base.format_option
    def header_prefix_string(self):
        "lines starting with this character will be handled as part of the header"
        return '#'
        
    
    @base.format_option
    def column_separator(self):
        "separator between the columns"
        return ' '
        
    @base.format_option
    def footer_prefix_string(self):
        "lines starting with this character will be handled as part of the footer"
        return self.header_prefix_string
        
    def read_header(self):
        while not self.cursor.is_at_end() and self.cursor.line().startswith(self.header_prefix_string):
            self.read_header_line(self.cursor.line()[len(self.header_prefix_string):])
            self.cursor.forward()
    
    def read_header_line(self, line):
        pass
        
    def read_rows(self):
        values = map(lambda x : [], range(len(self.attribute_names)))
        
        number_of_particles = 0
        
        while not self.cursor.is_at_end() and not self.cursor.line().startswith(self.footer_prefix_string):
            columns = self.split_into_columns(self.cursor.line())
            if len(columns)>0:
                if len(columns) != len(self.attribute_names):
                    raise base.IoException(
                        "Number of values on line '{0}' is {1}, expected {2}".format(self.cursor.line(), len(columns), len(self.attribute_names)))
            
            
                for value_string, list_of_values in zip(columns, values):
                    list_of_values.append(self.convert_string_to_number(value_string))
                
                
                number_of_particles += 1
            self.cursor.forward()
    
        quantities = map(
            lambda value, unit : unit.new_quantity(value), 
            values, 
            self.attribute_types
        )
        self.set = self.new_set(number_of_particles)
        self.set._set_values(self.set._get_keys(), self.attribute_names, quantities)
        
        self.cursor.forward()
        
    def read_footer(self):
        while not self.cursor.is_at_end() and self.cursor.line().startswith(self.footer_prefix_string):
            self.read_footer_line(self.line()[len(self.footer_prefix_string):])
            self.cursor.forward()
    
    def read_footer_line(self, line):
        pass
        
    def write_header(self):
        for x in self.header_lines():
            self.stream.write(self.header_prefix_string)
            self.stream.write(x)
            self.stream.write('\n')
        
    def write_rows(self):
        quantities = self.quantities
        units = self.attribute_types
        numbers = map(lambda quantity, unit : quantity.value_in(unit), quantities, units)
        
        columns = []
        
        for x in numbers:
            columns.append(map(self.convert_number_to_string, x))
        
        rows = []
        for i in range(len(columns[0])):
            row = [x[i] for x in columns]
            rows.append(row)
            
        lines = map(lambda  x : self.column_separator.join(x), rows)
        
        for x in lines:
            self.stream.write(x)
            self.stream.write('\n')
            
        
    def write_footer(self):
        for x in self.footer_lines():
            self.stream.write(self.footer_prefix_string)
            self.stream.write(x)
            self.stream.write('\n')
        
    def header_lines(self):
        result = []
        result.append(self.column_separator.join(self.attribute_names))
        result.append(self.column_separator.join(map(str, self.attribute_types)))
        return result
        
    def footer_lines(self):
        return []
        
    def convert_string_to_number(self, string):
        return float(string)
        
    def new_set(self, number_of_items):
        return core.Particles(number_of_items)
        
    @late
    def quantities(self):
        if self.set is None:
            return []
        else:
            return map(lambda x:getattr(self.set, x),self.attribute_names)



        

    def convert_number_to_string(self, number):
        return str(number)
    
    

    

    @base.format_option
    def float_format_string(self):
        "format specification string to convert numbers to strings, see format_spec in python documentation"
        return ".{0}e".format(self.precision_of_number_output)
    
    

    @base.format_option
    def precision_of_number_output(self):
        "The precision is a decimal number indicating how many digits should be displayed after the decimal point"
        return 12
    
    
class CsvFileText(TableFormattedText):
    """Process comma separated files
    
    Can process test files with comma separated fields.
    """
    
    provided_formats = ['csv']
    
    @base.format_option
    def column_separator(self):
        "separator between the columns"
        return ','
    
class Athena3DText(TableFormattedText):
    
    
    def read_header_line(self, line):
        line = line.lstrip()
        if line.startswith('['):
            self.read_attribute_names_from_line(line)
            
    def read_attribute_names_from_line(self, line):
        column_definition_strings = line.split()
        mapping_from_column_index_to_name = {}
        definition_re = re.compile(r'\[(\d+)\]=(.+)')
        for x in column_definition_strings:
            match_object = definition_re.match(x)
            if match_object is None:
                return
            index, name = match_object.groups()
            index = int(index) - 1
            name = name.replace('-','_')
            mapping_from_column_index_to_name[index] = name
        
        self.attribute_names = self.convert_dictionary_to_array(mapping_from_column_index_to_name)
        
    def convert_dictionary_to_array(self, dictionary):
        result = [None] * len(dictionary)
        for key, value in dictionary.iteritems():
            result[key] = value
        
        return result
        
            
        
    
