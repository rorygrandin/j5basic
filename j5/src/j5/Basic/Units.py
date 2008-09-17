# -*- coding: utf-8 -*-

from __future__ import division
import operator
import decimal

numbers = (int, long, float, decimal.Decimal)

def Identity(x):
    """Returns the object given to it"""
    return x

class Conversion(object):
    """Operation that converts a number from one unit to another"""
    def __init__(self, f, *args):
        self.f = f
        self.args = args

    def __call__(self, x):
        """Actually perform the conversion"""
        return self.f(x, *self.args)

    def __eq__(self, other):
        """Compare to another Conversion"""
        if type(other) != Conversion:
            raise NotImplementedError("Cannot compare %r and %r" % (self, other))
        return self.f == other.f and self.args == other.args

    def __repr__(self):
        """Represents the conversion"""
        return "%s(%s, *%r)" % (type(self).__name__, self.f, self.args)

    def __mul__(self, other):
        """Returns a related Conversion"""
        if not isinstance(other, Conversion):
            raise NotImplementedError("Cannot divide %r and %r" % (self, other))
        return SequentialConversion(self, other)

    def __truediv__(self, other):
        """Returns a related Conversion"""
        if not isinstance(other, Conversion):
            raise NotImplementedError("Cannot divide %r and %r" % (self, other))
        return SequentialConversion(self, DivideBy(other))

def DivideBy(conversion):
    """Returns the inverse of a Conversion if possible"""
    if isinstance(conversion, SequentialConversion):
        return SequentialConversion(*[DivideBy(c) for c in conversion.conversions])
    if conversion.f == operator.mul:
        return Conversion(operator.truediv, *conversion.args)
    if conversion.f == operator.truediv:
        return Conversion(operator.mul, *conversion.args)
    if conversion.f == Identity:
        return conversion
    raise ValueError("Could not calculate the inverse of %r" % (conversion,))

class SequentialConversion(Conversion):
    """Performs conversions in sequence"""
    def __init__(self, *conversions):
        self.conversions = []
        for c in conversions:
            if c != identity:
                self.conversions.append(c)
        self.simplify()

    def simplify(self):
        """Perform the most basic simplifications"""
        # reduced nested sequences
        new_conversions = []
        for c in self.conversions:
            if type(c) == Conversion:
                new_conversions.append(c)
            elif type(c) == SequentialConversion:
                new_conversions.extend(c.conversions)
            else:
                break
        else:
            self.conversions = new_conversions
        # reduce sequences of multiplications and divisions
        while True:
            n, d = 1, 1
            have_sequence = False
            new_conversions = []
            for c in self.conversions:
                if type(c) == Conversion and c.f == operator.mul:
                    n = n * c.args[0]
                    have_sequence = True
                elif type(c) == Conversion and c.f == operator.truediv:
                    d = d * c.args[0]
                    have_sequence = True
                else:
                    if have_sequence:
                        if n == d:
                            pass
                        elif abs(n / d) > 1:
                            new_conversions.append(Conversion(operator.mul, n / d))
                        else:
                            new_conversions.append(Conversion(operator.truediv, d / n))
                        have_sequence = False
                        n, d = 1, 1
                    new_conversions.append(c)
            else:
                if have_sequence:
                    if n == d:
                        pass
                    elif abs(n / d) > 1:
                        new_conversions.append(Conversion(operator.mul, n / d))
                    else:
                        new_conversions.append(Conversion(operator.truediv, d / n))
            if len(new_conversions) >= len(self.conversions):
                break
            self.conversions = new_conversions

    def __call__(self, x):
        """Actually perform the conversions"""
        for c in self.conversions:
            x = c(x)
        return x

    def __repr__(self):
        """Represents the conversion"""
        return "%s(%s)" % (type(self).__name__, ",".join([repr(c) for c in self.conversions]))

    def __eq__(self, other):
        """Compare to another Conversion"""
        if type(other) == Conversion:
            if not self.conversions:
                return other.f == Identity
            if len(self.conversions) != 1:
                return False
            return self.conversions[0] == other
        elif type(other) == SequentialConversion:
            if len(self.conversions) != len(other.conversions):
                return False
            for sc, oc in zip(self.conversions, other.conversions):
                if sc != oc:
                    return False
            return True
        else:
            raise NotImplementedError("Cannot compare %r and %r" % (self, other))

    def __ne__(self, other):
        """Compares self to other and returns whether they are unequal"""
        return not self.__eq__(other)

identity = Conversion(Identity)

class Unit(object):
    """A Base Unit that can be used in calculations"""
    def __init__(self, name, base_units, op):
        """Constructs a Unit with the given name"""
        self.name = name
        self.base_units = base_units
        self.op = op

    def __repr__(self):
        """Returns a representation of the type"""
        n, d = [], []
        for base, exponent in self.base_units.items():
            if exponent == 1:
                n.append(base.name)
            elif exponent > 0:
                n.append("%s ** %s" % (base.name, exponent))
            elif exponent == -1:
                d.append(base.name)
            elif exponent < 0:
                d.append("%s ** %s" % (base.name, exponent))
        if not n:
            n = ["1"]
        s = " * ".join(n)
        if d:
            if len(d) > 1:
                s += "/ (%s)" % (" * ".join(d))
            else:
                s += "/ %s" % (d[0])
        return "%s(%s, %s)" % (type(self).__name__, s, self.op)

    def __eq__(self, other):
        """Compares self to other and returns whether they are equal"""
        if not isinstance(other, Unit):
            return False
        if list(sorted(self.base_units.items())) != list(sorted(other.base_units.items())):
            return False
        if self.op != other.op:
            return False
        return True

    def __ne__(self, other):
        """Compares self to other and returns whether they are unequal"""
        return not self.__eq__(other)

    def __truediv__(self, other):
        """Calculates a derived unit by division"""
        if isinstance(other, numbers):
            return Unit("%s/%r" % (self.name, other), self.base_units, SequentialConversion(self.op, Conversion(operator.truediv, other)))
        elif isinstance(other, Unit):
            new_units = self.base_units.copy()
            for base_unit, exponent in other.base_units.items():
                new_units[base_unit] = new_units.get(base_unit, 0) - exponent
                if new_units[base_unit] == 0:
                    del new_units[base_unit]
            new_op = self.op / other.op
            return Unit("%s/%s" % (self.name, other.name), new_units, new_op)
        else:
            raise NotImplementedError("Cannot calculate division of %r by %r" % (type(self), type(other)))

    def __mul__(self, other):
        """Calculates a derived unit by multiplication"""
        if isinstance(other, numbers):
            return Unit("%s*%r" % (self.name, other), self.base_units, SequentialConversion(self.op, Conversion(operator.mul, other)))
        elif isinstance(other, Unit):
            new_units = self.base_units.copy()
            for base_unit, exponent in other.base_units.items():
                new_units[base_unit] = new_units.get(base_unit, 0) + exponent
                if new_units[base_unit] == 0:
                    del new_units[base_unit]
            new_op = self.op * other.op
            return Unit("%s*%s" % (self.name, other.name), new_units, new_op)
        else:
            raise NotImplementedError("Cannot calculate multiplication of %r by %r" % (type(self), type(other)))

    def __rmul__(self, other):
        """Calculates a derived unit by multiplication"""
        if isinstance(other, numbers):
            return self.__mul__(other)
        else:
            raise NotImplementedError("Cannot calculate multiplication of %r by %r" % (type(other), type(self)))

    def __call__(self, value):
        """Generates a Scalar from this Unit"""
        if isinstance(value, numbers):
            return Scalar(value, self)
        else:
            raise NotImplementedError("Can only generate Scalars for %r with numbers" % (self,))

class BaseUnit(Unit):
    """A simply constructed Scalar Unit"""
    def __init__(self, name):
        super(BaseUnit, self).__init__(name, {self: 1}, identity)

class Scalar(object):
    """An object representing a value with units"""
    def __init__(self, value, unit):
        """Construct a scalar with the given value and units"""
        self.value = value
        self.unit = unit

    def __repr__(self):
        return "%s(%s, %s)" % (type(self).__name__, self.value, self.unit)

    def __eq__(self, other):
        """Checks whether this has a value equivalent to that represented by other"""
        if not type(other) == type(self):
            raise NotImplementedError("Cannot compare %r with %r" % (self, other))
        units_ratio = self.unit / other.unit
        if units_ratio.base_units:
            return False
        adjusted_value = units_ratio.op(self.value)
        return adjusted_value == other.value

    def __ne__(self, other):
        """Checks whether this is a different value to other"""
        return not self.__eq__(other)

    def __cmp__(self, other):
        """Compares the two values"""
        if not type(other) == type(self):
            raise NotImplementedError("Cannot compare %r with %r" % (self, other))
        units_ratio = self.unit / other.unit
        if units_ratio.base_units:
            return False
        adjusted_value = units_ratio.op(self.value)
        return cmp(adjusted_value, other.value)

