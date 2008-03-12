#!/usr/bin/env python

class enum(object):
    @classmethod
    def identify(cls, constant):
        """returns the string identifier this class uses for the given constant"""
        if not hasattr(cls, "_constant_lookup"):
            builtin_attrs = dict.fromkeys(dir(enum))
            constant_attrs = [(attr, getattr(cls, attr, None))
                for attr in dir(cls)
                if attr not in builtin_attrs]
            cls._constant_lookup = dict(
                [(value, attr) for (attr, value) in constant_attrs if isinstance(value, int)]
                )
        if constant not in cls._constant_lookup:
            raise KeyError("%s does not define anything as the constant %s" % (cls.get_name(), constant))
        return cls._constant_lookup[constant]

    @classmethod
    def get_name(cls):
        """returns the name of the class (can be overridden)"""
        return cls.__name__
