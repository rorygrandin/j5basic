#!/usr/bin/env python

from j5.Basic import Decorators

def f(self, x=1, y=2, *args, **kw):
    """sample function for testing signatures etc"""
    pass

def chatty(f, *args, **kw):
    """sample decorator that logs calls on f.calls"""
    if not hasattr(f, "calls"):
        f.calls = []
    f.calls.append("Calling %r" % f.__name__)
    return f(*args, **kw)

def extdec(f, x, y, z):
    """decorator extending underlying function"""
    if not hasattr(f, "calls"):
        f.calls = []
    f.calls.append("Called with x=%r, y=%r, z=%r" % (x, y, z))
    return f(x + y * z)

def g(x):
    """returns x plus 25"""
    return x + 25

def extdec2(f, *args, **kw):
    """decorator extending underlying function, and using args and kwargs"""
    if not hasattr(f, "calls"):
        f.calls = []
    args = list(args)
    def poparg(argname):
        if argname in kw:
            return kw.pop(argname)
        else:
            return args.pop()
    y = poparg("y")
    z = poparg("z")
    x = poparg("x")
    f.calls.append("Called with x=%r, y=%r, z=%r" % (x, y, z))
    return f(x + y * z, z)

def g2(x, z=4):
    """returns x plus z plus 25"""
    return x + z + 25

def test_getinfo():
    """tests that the getinfo function returns the correct information about a function signature"""
    info = Decorators.getinfo(f)
    assert info["name"] == 'f'
    assert info["argnames"] == ['self', 'x', 'y', 'args', 'kw']
    assert info["defarg"] == (1, 2)
    assert info["shortsign"] == 'self, x, y, *args, **kw'
    assert info["fullsign"] == 'self, x=defarg[0], y=defarg[1], *args, **kw'
    assert (info["arg0"], info["arg1"], info["arg2"], info["arg3"], info["arg4"]) == ('self', 'x', 'y', 'args', 'kw')

def test_decorator():
    """test that a decorator is called, and properly calls the underlying function"""
    chatty_decorator = Decorators.decorator(chatty)
    chatty_g = chatty_decorator(g)
    result = chatty_g(3)
    assert result == 28
    assert g.calls[-1] == "Calling 'g'"

def test_decorator_lambda():
    """test that a decorator is called, and properly calls the underlying function"""
    l = lambda x: x + 21
    assert l(3) == 24
    chatty_decorator = Decorators.decorator(chatty)
    chatty_l = chatty_decorator(l)
    assert chatty_l(3) == 24

def test_decorator_signature():
    """tests that a decorated function retains the signature of the underlying function"""
    chatty_decorator = Decorators.decorator(chatty)
    chatty_f = chatty_decorator(f)
    info = Decorators.getinfo(f)
    chatty_info = Decorators.getinfo(chatty_f)
    assert info == chatty_info
    assert info.__doc__ == chatty_info.__doc__

def test_extend_decorator():
    """tests that a decorated function can extend the underlying function"""
    ext_decorator = Decorators.decorator(extdec, ['y', ('z', 3)])
    ext_g = ext_decorator(g)
    assert ext_g(100, 4) == 100 + 12 + 25
    assert g.calls[-1] == "Called with x=100, y=4, z=3"

def test_extend_decorator_signature():
    """tests that a decorated function can extend the signature of the underlying function"""
    ext_decorator = Decorators.decorator(extdec, ['y', ('z', 3)])
    ext_g = ext_decorator(g)
    info = Decorators.getinfo(g)
    ext_info = Decorators.getinfo(ext_g)
    assert ext_info.__doc__ == info.__doc__
    assert ext_info["name"] == info["name"]
    assert ext_info["argnames"] == ['x', 'y', 'z']
    assert ext_info["defarg"] == (3,)
    assert ext_info["shortsign"] == 'x, y, z'
    assert ext_info["fullsign"] == 'x, y, z=defarg[0]'
    assert ext_info["arg0"] == 'x'
    assert ext_info["arg1"] == 'y'
    assert ext_info["arg2"] == 'z'

def test_extend_decorator_existing():
    """tests that a decorated function can extend the underlying function, handling existing arguments right"""
    ext_decorator = Decorators.decorator(extdec2, [('y', 5), ('z', 3), ('x', 0)])
    ext_g = ext_decorator(g2)
    info = Decorators.getinfo(g2)
    ext_info = Decorators.getinfo(ext_g)
    assert ext_info.__doc__ == info.__doc__
    assert ext_info["name"] == info["name"]
    assert ext_info["argnames"] == ['x', 'z', 'y']
    assert ext_info["defarg"] == (0, 3, 5)
    assert ext_info["shortsign"] == 'x, z, y'
    assert ext_info["fullsign"] == 'x=defarg[0], z=defarg[1], y=defarg[2]'
    assert ext_info["arg0"] == 'x'
    assert ext_info["arg1"] == 'z'
    assert ext_info["arg2"] == 'y'
    result = ext_g()
    assert result == (0 + 3*5) + 3 + 25
    assert g2.calls[-1] == "Called with x=0, y=5, z=3"

