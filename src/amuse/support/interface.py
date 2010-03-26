
from amuse.support.data import parameters
from amuse.support.data import core
from amuse.support.data import values
from amuse.support.data import code_particles
from amuse.support.units import nbody_system

from amuse.support.methods import CodeMethodWrapper, CodeMethodWrapperDefinition

from amuse.support.core import late

import inspect

class OldObjectsBindingMixin(object):
                
    def setup_particles(self, particles):
        self.particles.add_particles(particles)
        
    def update_particles(self, particles):
        self.particles.copy_values_of_state_attributes_to(particles)
    
    def set_attribute(self, attribute_name, particles):
        particles.copy_values_of_attribute_to(attribute_name, self.particles)
        
    def update_attribute(self, attribute_name, particles):
        self.particles.copy_values_of_attribute_to(attribute_name, particles) 
        
        
        
class CodeInterfaceOld(OldObjectsBindingMixin):
    """Base class of next level interfaces to codes
    """
    
    parameter_definitions = []
    
    def __init__(self):
        self.parameters = parameters.Parameters(self.parameter_definitions, self)
 
class CodeAttributeWrapper(object):
    
    def __init__(self):
        pass
        
class HandleCodeInterfaceAttributeAccess(object):
    
    def supports(self, name, was_found):
        return False
        
    def get_attribute(self, name, result):
        return result
    
    def attribute_names(self):
        return set([])
        
        
    def setup(self, object):
        pass
    
    def has_name(self, name):
        return False
        
class LegacyInterfaceHandler(HandleCodeInterfaceAttributeAccess):
    
    def __init__(self, legacy_interface):
        self.legacy_interface = legacy_interface
        
    def supports(self, name, was_found):
        return hasattr(self.legacy_interface, name)
        
    def get_attribute(self, name, result):
        return getattr(self.legacy_interface, name)
    
    def attribute_names(self):
        return set(dir(self.legacy_interface))
        
    
    def has_name(self, name):
        return name == 'LEGACY'
    
    

class HandleConvertUnits(HandleCodeInterfaceAttributeAccess, CodeMethodWrapperDefinition):
    
    def __init__(self, handler):
        self.handler = handler
        self.converter = None
        
    def supports(self, name, was_found):
        return was_found and not self.converter is None
        
    def get_attribute(self, name, attribute):
        if inspect.ismethod(attribute):
            result = attribute #UnitsConvertionMethod(attribute, self.converter)
        elif isinstance(attribute, core.AbstractParticleSet):
            result = attribute #core.ParticlesWithUnitsConverted(attribute, self.converter)
        elif isinstance(attribute, values.Quantity):
            result = self.converter.from_target_to_source(attribute)
        elif isinstance(attribute, CodeMethodWrapper):
            result = CodeMethodWrapper(attribute, self)
        elif isinstance(attribute, parameters.Parameters):
            result = parameters.ParametersWithUnitsConverted(attribute, self.converter)
        elif hasattr(attribute, '__iter__'):
            result = self.convert_and_iterate(attribute)
        else:
            result = attribute
        return result
            
    def convert_and_iterate(self, iterable):
        for x in iterable:
            yield self.converter.from_target_to_source(x)
            
    
    def set_converter(self, converter):
        self.converter = converter
    
    def set_nbody_converter(self, nbody_converter):
        self.set_converter(nbody_converter.as_converter_from_si_to_nbody())
        
    def has_name(self, name):
        return name == 'UNIT'
        
    def setup(self, object):
        object.define_converter(self)
        
    def convert_arguments(self, method,  list_arguments, keyword_arguments):
        converted_list_arguments = [self.from_source_to_target(x) for x in list_arguments]
        converted_keyword_arguments = {}
        for key, value in keyword_arguments.iteritems():
            converted_keyword_arguments[key] = self.from_source_to_target(value)
            
        return converted_list_arguments, converted_keyword_arguments
        
    def convert_result(self, method, result):
        return self.from_target_to_source(result)
        
    def from_source_to_target(self, x):
        if isinstance(x, values.Quantity):
            return self.converter.from_source_to_target(x)
        else:
            return x
            
    def from_target_to_source(self, x):
        if isinstance(x, values.Quantity):
            return self.converter.from_target_to_source(x)
        elif hasattr(x, '__iter__'):
            return list(self.convert_and_iterate(x))
        else:
            return x
    
class StateMethodDefinition(CodeMethodWrapperDefinition):
    def __init__(self, handler, from_state, to_state, function_name):
        self.handler = handler
        self.transitions = []
        self.add_transition(from_state, to_state)
        self.function_name = function_name
    
    def add_transition(self, from_state, to_state):
        self.transitions.append((from_state, to_state))
    
    def new_method(self, method = None):
        if method == None:
            method = getattr(self.handler.interface, self.function_name)
        return CodeMethodWrapper(method, self)
        
    def precall(self, method):
        stored_transitions = []
        for from_state, to_state in self.transitions:
            if from_state is None:
                return to_state
            elif from_state == self.handler._current_state:
                return to_state
            else:
                stored_transitions.append((from_state, to_state))
        
        for from_state, to_state  in stored_transitions:
            try:
                self.handler._do_state_transition_to(from_state)
                return to_state
            except Exception, ex:
                pass
        
        # do again to get an exception.
        self.handler._do_state_transition_to(stored_transitions[0][0])
    
    def postcall(self, method, to_state):
        if to_state is None:
            return
        elif to_state == self.handler._current_state:
            return
        else:
            self.handler._current_state = to_state

            
class HandleState(HandleCodeInterfaceAttributeAccess):
    class State(object):
        def __init__(self, handler, name):
            self.handler = handler
            self.name = name
            self.from_transitions = []
            self.to_transitions = []
            
        def __str__(self):
            return "state '{0}'".format(self.name)
                        
    class StateTransition(object):
        def __init__(self, handler, from_state, to_state, method = None, is_auto = True):
            self.method = method
            self.to_state = to_state
            self.from_state = from_state
            self.is_auto = is_auto
            self.handler = handler
            
        def __str__(self):
            return "transition from {0} to {1}".format(self.from_state, self.to_state)
            
        def do(self):
            if self.method is None:
                self.handler.current_state = self.to_state
            else:
                self.method.new_method()() 
            
    def __init__(self, interface):
        self._mapping_from_name_to_state_method = {}
        self._current_state = None
        self._do_automatic_state_transitions = True
        self.states = {}
        self.interface = interface
        
    
    def supports(self, name, was_found):
        return name in self._mapping_from_name_to_state_method
        
    def get_attribute(self, name, value):
        return self._mapping_from_name_to_state_method[name].new_method(value)
        
    
    def attribute_names(self):
        return set(self._mapping_from_name_to_state_method.keys())
        
    def define_state(self, name):
        if name in self.states:
            return        
        self.states[name] = self.State(self, name)
         
    def _do_state_transition_to(self, state):
        transitions = self._get_transitions_path_from_to(self._current_state, state)
        if transitions is None:
            raise Exception("No transition from current state {0} to {1} possible".format(self._current_state, state))
        
        transitions_with_methods = filter(lambda x : not x.method is None,transitions)
        if not self._do_automatic_state_transitions and len(transitions_with_methods) > 0:
            lines = []
            lines.append("Interface is not in {0}, should transition from {1} to {0} first.\n". format(state, self._current_state))
            for x in transitions:
                if x.method is None:
                    lines.append("{0}, automatic". format(x))
                else:
                    lines.append("{0}, calling '{1}'". format(x, x.method.function_name))
            exception = Exception('\n'.join(lines))
            exception.transitions = transitions
            raise exception
            
        for transition in transitions:
            transition.do()
        
    
    def _get_transitions_path_from_to(self, from_state, to_state):
        transitions = filter(lambda x : x.is_auto, to_state.to_transitions)
        
        paths = map(lambda x : [x], transitions)
        
        def has_no_circle(path):
            seen_states = set([])
            for transition in path:
                if transition.to_state in seen_states:
                    return False
                seen_states.add(transition.to_state)
            return True
                    
            
        while paths:
            current = paths.pop()
            first = current[0]
            if first.from_state == from_state:
                return current
            elif first.from_state is None:
                return current
            else:
                transitions = filter(lambda x : x.is_auto, first.from_state.to_transitions)
                new_paths = map(lambda x : [x], transitions)

                for new_path in new_paths:
                    new_path.extend(current)
            
                new_paths = filter(has_no_circle, new_paths)
            
                paths.extend(new_paths)
            
                
        return None
        
    def _add_state_method(self, from_state, to_state, function_name):
        if not function_name in self._mapping_from_name_to_state_method:
            state_method = StateMethodDefinition(self, from_state, to_state, function_name)
            self._mapping_from_name_to_state_method[function_name] = state_method
        else:
            state_method = self._mapping_from_name_to_state_method[function_name]
            state_method.add_transition(from_state, to_state)
            


    def add_method(self, state_name, function_name):
        """
        Define a method that can run when the interface is in the
        provided state.
        """
        self.define_state(state_name)
        
        state = self.states[state_name]
        
        self._add_state_method( state, None, function_name)
            
    
    def add_transition(self, from_name, to_name, function_name, is_auto = True):
        self.define_state(from_name)
        self.define_state(to_name)
        
        from_state = self.states[from_name]
        to_state   = self.states[to_name]
        definition = StateMethodDefinition(self, from_state, to_state, function_name)
        
        transition = self.StateTransition(self, from_state, to_state, definition, is_auto)
        
        from_state.from_transitions.append(transition)
        to_state.to_transitions.append(transition)
        
        self._add_state_method(from_state, to_state, function_name)
        
        
    def add_transition_to_method(self, state_name, function_name, is_auto = True):
        """
        Define a method that can run in any state and will transition the interface
        to the provided state.
        """
        self.define_state(state_name)
        
        state = self.states[state_name]
        
        definition = StateMethodDefinition(self, None, state, function_name)
        transition = self.StateTransition(self, None, state, definition, is_auto)
        
        state.to_transitions.append(transition)
        
        self._add_state_method(None, state, function_name)

        
    def do_automatic_state_transitions(self, boolean):
        self._do_automatic_state_transitions = boolean
        
    def set_initial_state(self, name):
        self.define_state(name)
        self._current_state = self.states[name]
        
    
    def setup(self, object):
        object.define_state(self)
            
    
    def has_name(self, name):
        return name == 'STATE'
        


class MethodWithUnits(CodeMethodWrapper):

    def __init__(self, original_method, definition):
        CodeMethodWrapper.__init__(self, original_method, definition)
         
    @late
    def index_input_attributes(self):
        return self.definition.index_input_attributes
        
    @late
    def index_output_attributes(self):
        return self.definition.index_output_attributes
        
            
        
class MethodWithUnitsDefinition(CodeMethodWrapperDefinition):
    
    ERROR_CODE =  object()
    NO_UNIT = object()
    INDEX = object()

    def __init__(self, handler, function_name, units, return_units, return_value_handler, name):
        self.function_name = function_name
        
        if hasattr(units, '__iter__'):
            self.units = units
        else:
            self.units = (units,)
            
        self.return_units = return_units
        self.handler = handler
        self.name = name
        if return_units is None:
            if return_value_handler is None:
                self.handle_return_value = self.handle_as_errorcode
            else:
                self.handle_return_value = return_value_handler
        else:
            self.handle_return_value = self.handle_as_unit
    
    def new_method(self, original_method):
        if self.has_same_name_as_original:
            return MethodWithUnits(original_method, self)
        else:
            return MethodWithUnits(getattr(self.handler.interface, self.function_name), self)

    def handle_errorcode(self, errorcode):
        if errorcode in self.handler.interface.errorcodes:
            raise Exception("Error when calling '{0}' of a '{1}', errorcode is {2}, error is '{3}'".format(self.name, type(self.handler.interface).__name__, errorcode,  self.handler.interface.errorcodes[errorcode]))
        elif errorcode < 0:
            raise Exception("Error when calling '{0}' of a '{1}', errorcode is {2}".format(self.name, type(self.handler.interface).__name__, errorcode))
        else:
            return errorcode 
            
    def handle_as_errorcode(self, errorcode):
        if hasattr(errorcode, '__iter__'):
            for x in errorcode:
                self.handle_errorcode(x)
        else:
            self.handle_errorcode(errorcode)     
    
    def handle_as_unit(self, return_value):
        if not hasattr(self.return_units, '__iter__'):
            if self.return_units == self.NO_UNIT or self.return_units == self.INDEX:
                return return_value
            elif self.return_units == self.ERROR_CODE:
                self.handle_as_errorcode(return_value)
            else:
                return self.return_units.new_quantity(return_value)
        else:
            if not hasattr(return_value, '__iter__'):
                return_value = [return_value]
            result = []
            for value, unit in zip(return_value, self.return_units):
                if unit == self.ERROR_CODE:
                    self.handle_as_errorcode(value)
                elif unit == self.NO_UNIT:
                    result.append(value)
                elif unit == self.INDEX:
                    result.append(value)
                else:
                    result.append(unit.new_quantity(value))
            if len(result) == 1:
                return result[0]
            else:
                return result
    
    
    def convert_arguments(self, method , list_arguments, keyword_arguments):
        result = {}
        input_parameters = method.method_input_argument_names
        
        for index, parameter in enumerate(input_parameters):
            if parameter in keyword_arguments:
                if self.units[index] == self.NO_UNIT or self.units[index] == self.INDEX:
                    result[parameter] = keyword_arguments[parameter.name]
                else:
                    result[parameter] = keyword_arguments[parameter.name].value_in(self.units[index])
        
        for index, argument in enumerate(list_arguments):
            parameter = input_parameters[index]
            if self.units[index] == self.NO_UNIT or self.units[index] == self.INDEX:
                result[parameter] = argument
            else:
                result[parameter] = argument.value_in(self.units[index])
        
        return (), result
        
    def convert_result(self, method, result):
        return self.handle_return_value(result)
    
    @late
    def has_same_name_as_original(self):
        return self.function_name == self.name
    
        
    @late
    def index_input_attributes(self):
        return map(lambda x : x == self.INDEX, self.units)
        
    @late
    def index_output_attributes(self):
        if not hasattr(self.return_units, '__iter__'):
            return [self.return_units == self.INDEX]
        else:
            return map(lambda x : x == self.INDEX, self.return_units)

class HandleMethodsWithUnits(object):
    ERROR_CODE = MethodWithUnitsDefinition.ERROR_CODE
    NO_UNIT = MethodWithUnitsDefinition.NO_UNIT
    INDEX = MethodWithUnitsDefinition.INDEX
    
    def __init__(self, interface):
        self.method_definitions = {}
        self.interface = interface

    def supports(self, name, was_found):
        return name in self.method_definitions
        
    def get_attribute(self, name, value):
        return self.method_definitions[name].new_method(value)
    
    
    def attribute_names(self):
        return set(self.method_definitions.keys())
        
    def add_method(self, original_name, units, return_unit = None,  public_name = None, return_value_handler = None):
        if public_name is None:
            public_name = original_name
        
        definition = MethodWithUnitsDefinition(
            self,
            original_name, 
            units, 
            return_unit, 
            return_value_handler, 
            public_name
        )
        self.method_definitions[public_name] = definition
    
    def has_name(self, name):
        return name == 'METHOD'
        
    def setup(self, object):
        object.define_methods(self)
    


class PropertyWithUnitsDefinition(object):
    
    def __init__(self, handler, function_or_attribute_name, unit, public_name):
        self.function_or_attribute_name = function_or_attribute_name
        self.unit = unit
        self.public_name = public_name
        self.handler = handler
    
    def get_value(self, original):
        if self.has_same_name_as_original:
            function_or_attribute = original
        else:
            function_or_attribute = getattr(self.handler.interface, self.function_or_attribute_name)
            
        if hasattr(function_or_attribute, '__call__'):
            return_value = function_or_attribute()
            if hasattr(return_value, '__iter__'):
                value, errorcode = return_value
                if errorcode < 0:
                    raise Exception("calling '{0}' to get the value for property '{1}' resulted in an error (errorcode {2})".format(self.function_or_attribute_name, self.public_name, errorcode))
                else:
                    return self.unit.new_quantity(value)
            else:
                return self.unit.new_quantity(return_value)
        else:
            return self.unit.new_quantity(function_or_attribute)
            
    
    @late
    def has_same_name_as_original(self):
        return self.function_or_attribute_name == self.public_name


class HandlePropertiesWithUnits(HandleCodeInterfaceAttributeAccess):
    def __init__(self, interface):
        self.property_definitions = {}
        self.interface = interface

    def supports(self, name, was_found):
        return name in self.property_definitions
        
    def get_attribute(self, name, value):
        return self.property_definitions[name].get_value(value)
        
    def attribute_names(self):
        return set(self.property_definitions.keys())
        
    def add_property(self, function_name, unit, public_name = None):
        if public_name is None:
            if function_name.startswith('get_'):
                public_name = function_name[4:]
            else:
                public_name = function_name
                        
        definition = PropertyWithUnitsDefinition(
            self,
            function_name, 
            unit,
            public_name
        )
        self.property_definitions[public_name] = definition
    
    def has_name(self, name):
        return name == 'PROPERTY'
        
    def setup(self, object):
        object.define_properties(self)
        

class HandleParameters(HandleCodeInterfaceAttributeAccess):
    def __init__(self, interface):
        self.property_definitions = {}
        self.interface = interface
        self.definitions = []

    def supports(self, name, was_found):
        return name == 'parameters'
        
    def get_attribute(self, name, value):
        return parameters.Parameters(self.definitions, self.interface.legacy_interface)
        
    
    def attribute_names(self):
        return set(['parameters'])
        
    def add_attribute_parameter(self, attribute_name, name, description, unit, default_value = None):
        definition = parameters.ModuleAttributeParameterDefinition(
            attribute_name,
            name, 
            description, 
            unit, 
            default_value
        )
        self.definitions.append(definition) 
    
    def add_method_parameter(self, get_method, set_method, name, description, unit, default_value = None):
        definition = parameters.ModuleMethodParameterDefinition_Next(
            get_method, 
            set_method, 
            name, 
            description, 
            unit, 
            default_value
        )
        self.definitions.append(definition) 
        
        
    def add_caching_parameter(self, parameter_name, name, description, unit, default_value = None):
        definition = parameters.ModuleCachingParameterDefinition(
            parameter_name, 
            name, 
            description, 
            unit, 
            default_value
        )
        self.definitions.append(definition) 
    
    def has_name(self, name):
        return name == 'PARAMETER'
        
    def setup(self, object):
        object.define_parameters(self)
        

class HandleErrorCodes(HandleCodeInterfaceAttributeAccess):
    def __init__(self, interface):
        self.error_codes = {}
        self.interface = interface

    def supports(self, name, was_found):
        return name == 'errorcodes'
        
    def get_attribute(self, name, value):
        return self.error_codes
        
    def attribute_names(self):
        return set(['errorcodes'])
        
    def add_errorcode(self, number, string):
        self.error_codes[number] = string 
    
    def has_name(self, name):
        return name == 'ERRORCODE'
        
    def setup(self, object):
        object.define_errorcodes(self)
    
        
class ParticleSetDefinition(object):
    
    def __init__(self, handler):
        self.handler = handler
        self.name_of_indexing_attribute = 'index_of_the_particle'
        self.new_particle_method = ('new_particle',(), None)
        self.name_of_delete_particle_method = 'delete_particle'
        self.name_of_number_of_particles_method = 'get_number_of_particles'
        self.setters = []
        self.getters = []
        self.queries = []
        self.attributes = []
        
        self.selects_form_particle = []
        self.methods = []
        self.is_inmemory = False
        self.particles_factory = core.Particles
    
    def new_storage(self, interface):
        
        if self.is_inmemory:
            return core.InMemoryAttributeStorage()
            
        setters = []
        for name, mapping, names in self.setters:
            x = code_particles.ParticleSetAttributesMethod(getattr(interface, name), mapping, names)
            setters.append(x)
            
        getters = []
        for name, mapping, names in self.getters:
            x = code_particles.ParticleGetAttributesMethod(getattr(interface, name), mapping, names)
            getters.append(x)
            
            
        name, mapping, names = self.new_particle_method
        new_particle_method = code_particles.NewParticleMethod(getattr(interface, name), mapping, names)
        
        delete_particle_method = getattr(interface, self.name_of_delete_particle_method)
        number_of_particles_method = None #getattr(interface, self.name_of_number_of_particles_method)
        
        return code_particles.InCodeAttributeStorage(
            interface,
            new_particle_method, 
            delete_particle_method, 
            number_of_particles_method, 
            setters,
            getters,
            self.name_of_indexing_attribute
        )
        
    def new_queries(self, interface):
        queries = []
        for name, names, public_name in self.queries:
            x = code_particles.ParticleQueryMethod(getattr(interface, name), names, public_name)
            queries.append(x)
        
        return queries
        
    def new_selects_from_particle(self, interface):
        results = []
        for name, names, public_name in self.selects_form_particle:
            x = code_particles.ParticleSpecificSelectMethod(getattr(interface, name), names, public_name)
            results.append(x)
        
        return results
        
    def new_particle_methods(self, interface):
        results = []
        for name, public_name in self.methods:
            x = code_particles.ParticleMethod(getattr(interface, name), public_name)
            results.append(x)
        
        return results
        

class CodeInMemoryParticles(core.Particles):
    
    def __init__(self, code_interface = None, storage = None):
        core.Particles.__init__(self, storage = storage)
        self._private.code_interface = code_interface 
        
class HandleParticles(HandleCodeInterfaceAttributeAccess):
    def __init__(self, interface):
        self.interface = interface
        self.sets = {}
        self.particle_sets = {}
        

    def supports(self, name, was_found):
        return name in self.sets
        
    def get_attribute(self, name, value):
        if name in self.particle_sets:
            return self.particle_sets[name]
        else:
            storage = self.sets[name].new_storage(self.interface)
            if self.sets[name].is_inmemory:
                result = self.sets[name].particles_factory(self.interface, storage = storage)
            else:
                result = self.sets[name].particles_factory(storage = storage)
            queries = self.sets[name].new_queries(self.interface)
            for x in queries:
                result.add_function_attribute(x.public_name, x.apply)
            
            selects = self.sets[name].new_selects_from_particle(self.interface)
            for x in selects:
                result.add_function_attribute(x.public_name, x.apply_on_all)
                result.add_particle_function_attribute(x.public_name, x.apply_on_one)
            
            
            selects = self.sets[name].new_particle_methods(self.interface)
            for x in selects:
                result.add_function_attribute(x.public_name, x.apply_on_all, x.apply_on_one)
            
            attributes = self.sets[name].attributes
            for name_of_the_attribute, name_of_the_method, names in attributes:
                result.add_calculated_attribute(name_of_the_attribute, getattr(self.interface, name_of_the_method), names)
                
            self.particle_sets[name] = result
            return result
    
    def attribute_names(self):
        return set(self.sets.keys())
        
        
    def has_name(self, name):
        return name == 'PARTICLES'
        
    def setup(self, object):
        object.define_particle_sets(self)
     
    def define_set(self, name, name_of_indexing_attribute = 'index_of_the_particle'):
        definition = ParticleSetDefinition(self)
        definition.name_of_indexing_attribute = name_of_indexing_attribute
        self.sets[name] = definition
        
    def define_inmemory_set(self, name, particles_factory = CodeInMemoryParticles):
        definition = ParticleSetDefinition(self)
        definition.is_inmemory = True
        definition.particles_factory = particles_factory
        self.sets[name] = definition

    def set_new(self, name_of_the_set, name_of_new_particle_method, mapping = (), names = None):
        self.sets[name_of_the_set].new_particle_method = (name_of_new_particle_method, mapping, names)
        
    def set_delete(self, name_of_the_set, name_of_delete_particle_method):
        self.sets[name_of_the_set].name_of_delete_particle_method = name_of_delete_particle_method
        
    def add_getter(self, name_of_the_set, name_of_the_getter, mapping = (), names = None):
        
        self.sets[name_of_the_set].getters.append((name_of_the_getter, mapping, names))

    def add_setter(self, name_of_the_set, name_of_the_setter, mapping = (), names = None):
        
        self.sets[name_of_the_set].setters.append((name_of_the_setter,mapping, names))
        
    def add_attribute(self, name_of_the_set, name_of_the_attribute, name_of_the_method, names = None):
        
        self.sets[name_of_the_set].attributes.append((name_of_the_attribute,name_of_the_method, names))
        
    def add_query(self, name_of_the_set, name_of_the_query, names = (), public_name = None):
        if not public_name:
            public_name = name_of_the_query
            
        self.sets[name_of_the_set].queries.append((name_of_the_query, names, public_name))
        
    
    def add_method(self, name_of_the_set, name_of_the_method, public_name = None):
        if not public_name:
            public_name = name_of_the_method
            
        self.sets[name_of_the_set].methods.append((name_of_the_method, public_name))
        
    
    def add_select_from_particle(self, name_of_the_set, name, names = (), public_name = None):
        if not public_name:
            public_name = name
            
        self.sets[name_of_the_set].selects_form_particle.append((name, names, public_name))
        

class OverriddenCodeInterface(object):
    
    def __init__(self, code_interface):
        self.code_interface = code_interface
    
    def __getattr__(self, name):
        return self.code_interface.__getattr__(name)
        
class CodeInterface(OldObjectsBindingMixin):
    
    def __init__(self, legacy_interface):
        object.__setattr__(self, 'legacy_interface', legacy_interface)
        object.__setattr__(self, '_handlers', [])
         
        
        self._handlers.append(LegacyInterfaceHandler(legacy_interface))
        self._handlers.append(HandleMethodsWithUnits(self))
        self._handlers.append(HandlePropertiesWithUnits(self))
        self._handlers.append(HandleParameters(self))
        self._handlers.append(HandleParticles(self))
        self._handlers.append(HandleState(self))
        self._handlers.append(HandleConvertUnits(self))
        self._handlers.append(HandleErrorCodes(self))
        
        self.setup()
        
    def setup(self):
        for x in self._handlers:
            x.setup(self)

    def define_state(self, handler):
        pass
    
    def define_methods(self, handler):
        pass
        
    def define_properties(self, handler):
        pass
        
    def define_converter(self, handler):
        pass
        
    def define_parameters(self, handler):
        pass
    
    def define_particle_sets(self, handler):
        pass
        
    def define_errorcodes(self, handler):
        pass
        
    def get_handler(self, name):
        for x in self._handlers:
            if x.has_name(name):
                return x
        return None
        
    def __getattr__(self, name):
        result = None
        found = False
        for handler in self._handlers:
            if handler.supports(name, found):
                result = handler.get_attribute(name, result)
                found = True
        if not found:
            raise AttributeError(name)
        return result
        
    
    def __dir__(self):
        result = set(dir(type(self)))
        result |= set(self.__dict__.keys())
        for handler in self._handlers:
            result |= handler.attribute_names()
        return list(result)
        
    def overridden(self):
        return OverriddenCodeInterface(self)
        
    def get_name_of_current_state(self):
        return self.get_handler('STATE')._current_state.name
        
