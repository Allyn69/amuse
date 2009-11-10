"""
"""
import numpy

class Quantity(object):
    """
    A Quantity objects represents a scalar or vector with a
    specific unit. Quantity is an abstract base class
    for VectorQuantity and ScalarQuantity.
    
    Quantities should be constructed using *or-operator* ("|"),
    *new_quantity* or *unit.new_quantity".
    
    Quantities emulate numeric types.
    
    Examples
    
    >>> from amuse.support.units import units
    >>> 100 | units.m
    quantity<100 m>
    >>> (100 | units.m) + (1 | units.km)
    quantity<1100.0 m>
    
    Quantities can be tested
       
    >>> from amuse.support.units import units
    >>> x = 100 | units.m
    >>> x.is_quantity()
    True
    >>> x.is_scalar()
    True
    >>> x.is_vector()
    False
    >>> v = [100, 200, 300] | units.g
    >>> v.is_quantity()
    True
    >>> v.is_scalar()
    False
    >>> v.is_vector()
    True
    
    Quantities can be converted to numbers
    
    >>> from amuse.support.units import units
    >>> x = 1000 | units.m
    >>> x.value_in(units.m)
    1000.0
    >>> x.value_in(units.km)
    1.0
    >>> x.value_in(units.g) # but only if the units are compatible!
    Traceback (most recent call last):
        File "<stdin>", line 1, in ?
    Exception: Cannot expres: g in m

    
    """
    def __init__(self, unit):
        self.unit = unit
        
    def is_quantity(self):
        """
        True for all quantities.
        """
        return True
        
    def is_scalar(self):
        """
        True for scalar quantities.
        """
        return False
        
    def is_vector(self):
        """
        True for vector quantities.
        """
        return False
        
    def __repr__(self):
        return 'quantity<'+str(self)+'>'

    def __div__(self, other):
        return new_quantity(self.number / other.number , (self.unit / other.unit).to_simple_form())
        
    def __add__(self, other):
        other_in_my_units = other.in_(self.unit)
        return new_quantity(self.number + other_in_my_units.number , self.unit)
        
    def __sub__(self, other):
        other_in_my_units = other.in_(self.unit)
        return new_quantity(self.number - other_in_my_units.number , self.unit)

    def __mul__(self, other):
        return  new_quantity(self.number * other.number , (self.unit * other.unit).to_simple_form())
        
            
    def in_(self, another_unit):
        """
        Reproduce quantity in another unit.
        The new unit must have the same basic si quantities.
        
        :argument another_unit: unit to convert quantity to
        :returns: quantity converted to new unit
        """
        value_of_unit_in_another_unit = self.unit.in_(another_unit)
        return new_quantity(self.number * value_of_unit_in_another_unit.number, another_unit)

    def value_in(self, unit):
        """
        Return a numeric value (for scalars) or array (for vectors) 
        in the given unit.
        
        A number is returned without any unit information. Use this
        function oply to transfer values to other libraries that have
        no support for quantities (for example plotting).
        
        :argument unit: wanted unit of the value
        :returns: number in the given unit
        
        >>> from amuse.support.units import units
        >>> x = 10 | units.km
        >>> x.value_in(units.m)
        10000.0
        
        """
        value_of_unit_in_another_unit = self.unit.in_(unit)
        return self.number * value_of_unit_in_another_unit.number

class ScalarQuantity(Quantity):
    """
    A ScalarQuantity objects represents a physical scalar 
    quantity.
    """
    
    def __init__(self, number, unit):
        Quantity.__init__(self, unit)
        self.number = number
                  
    def is_scalar(self):
        return True
      
    def __str__(self):
        unit_str = str(self.unit)
        if unit_str:
            return str(self.number) + ' ' + unit_str
        else:
            return str(self.number)
                                
    def __lt__(self, other):
        other_in_my_units = other.in_(self.unit)
        return self.number < other_in_my_units.number
        
    def __gt__(self, other):
        other_in_my_units = other.in_(self.unit)
        return self.number > other_in_my_units.number
        
    def __eq__(self, other):
        other_in_my_units = other.in_(self.unit)
        return self.number == other_in_my_units.number
        
    def __neq__(self, other):
        other_in_my_units = other.in_(self.unit)
        return self.number != other_in_my_units.number

    def __le__(self, other):
        return self.__eq__(other) or self.__lt__(other)

    def __ge__(self, other):
        return self.__eq__(other) or self.__gt__(other)
            
            
class VectorQuantity(Quantity):
    """
    A ScalarQuantity objects represents a physical vector 
    quantity.
    """
    def __init__(self, array, unit):
        Quantity.__init__(self, unit)
        self._number = numpy.array(array)
        
    def is_vector(self):
        return True
    
    
    def __getitem__(self, index):
        """Return the "index" component as a quantity.
        
        :argument index: index of the component, valid values
            for 3 dimensional vectors are: ``[0,1,2]``
        :returns: quantity with the same units
        
        >>> from amuse.support.units import si
        >>> vector = [0.0, 1.0, 2.0] | si.kg
        >>> print vector[1]
        1.0 kg
        """
        return new_quantity( self._number[index] , self.unit )
        
    
    def __setitem__(self, index, quantity):
        """Update the "index" component to the specified quantity.
        
        :argument index: index of the component, valid values
            for 3 dimensional vectors are: ``[0,1,2]``
        :quantity: quantity to set, will be converted to
            the unit of this vector
        
        >>> from amuse.support.units import si
        >>> vector = [0.0, 1.0, 2.0] | si.kg
        >>> g = si.kg / 1000
        >>> vector[1] = 3500 | g
        >>> print vector
        [0.0, 3.5, 2.0] kg
        """
        quantity_in_my_units = quantity.in_(self.unit)
        self._number[index] = quantity_in_my_units.number
        
    @property
    def number(self):
        return self._number
        
    @property
    def x(self):
        """The x axis component of a 3 dimensional vector.
        This is equavalent to the first component of vector.
        
        :returns: x axis component as a quantity
        
        >>> from amuse.support.units import si
        >>> vector = [1.0, 2.0, 3.0] | si.kg
        >>> print vector.x
        1.0 kg
        """
        return self[0]
        
    @property
    def y(self):
        """The y axis component of a 3 dimensional vector.
        This is equavalent to the second component of vector.
        
        :returns: y axis component as a quantity
        
        >>> from amuse.support.units import si
        >>> vector = [1.0, 2.0, 3.0] | si.kg
        >>> print vector.y
        2.0 kg
        """
        return self[1]
        
    @property
    def z(self):
        """The z axis component of a 3 dimensional vector.
        This is equavalent to the third component of vector.
        
        :returns: z axis component as a quantity
        
        >>> from amuse.support.units import si
        >>> vector = [1.0, 2.0, 3.0] | si.kg
        >>> print vector.z
        3.0 kg
        """
        return self[2]
        
    def __str__(self):
        unit_str = str(self.unit)
        array_str = '[' + ', '.join([str(x) for x in self._number]) + ']'
        if unit_str:
            return array_str + ' ' + unit_str
        else:
            return array_str
            

    def __lt__(self, other):
        other_in_my_units = other.in_(self.unit)
        return self.number < other_in_my_units.number
        
    def __gt__(self, other):
        other_in_my_units = other.in_(self.unit)
        return self.number > other_in_my_units.number
        
    def __eq__(self, other):
        other_in_my_units = other.in_(self.unit)
        return self.number == other_in_my_units.number
        
    def __neq__(self, other):
        other_in_my_units = other.in_(self.unit)
        return self.number != other_in_my_units.number   
            
    def indices(self):
        for x in len(self._number):
            yield x
                 
        
def new_quantity(value, unit):
    """Create a new Quantity object.
    
    :argument value: numeric value of the quantity, can be 
        a number or a sequence (list or ndarray)
    :argument unit: unit of the quantity
    :returns: new ScalarQuantity or VectorQuantity object
    """
    if isinstance(value, list):
       return VectorQuantity(value, unit)
    if isinstance(value, numpy.ndarray):
       return VectorQuantity(value, unit)
    return ScalarQuantity(value, unit)
       
