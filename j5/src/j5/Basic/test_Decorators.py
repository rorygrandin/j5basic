#!/usr/bin/env python

from j5.Basic import Decorators
import threading
import time
import py.test

class TestDecoratorDecorator(object):

    @staticmethod
    def f(self, x=1, y=2, *args, **kw):
        """sample function for testing signatures etc"""
        pass

    @staticmethod
    def chatty(f, *args, **kw):
        """sample decorator that logs calls on f.calls"""
        if not hasattr(f, "calls"):
            f.calls = []
        f.calls.append("Calling %r" % f.__name__)
        return f(*args, **kw)

    @staticmethod
    def extdec(f, x, y, z):
        """decorator extending underlying function"""
        if not hasattr(f, "calls"):
            f.calls = []
        f.calls.append("Called with x=%r, y=%r, z=%r" % (x, y, z))
        return f(x + y * z)

    @staticmethod
    def g(x):
        """returns x plus 25"""
        return x + 25

    @staticmethod
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

    @staticmethod
    def g2(x, z=4):
        """returns x plus z plus 25"""
        return x + z + 25

    def test_getinfo(self):
        """tests that the getinfo function returns the correct information about a function signature"""
        info = Decorators.decorator_helpers.getinfo(self.f)
        assert info["name"] == 'f'
        assert info["argnames"] == ['self', 'x', 'y', 'args', 'kw']
        assert info["defarg"] == (1, 2)
        assert info["shortsign"] == 'self, x, y, *args, **kw'
        assert info["fullsign"] == 'self, x=defarg[0], y=defarg[1], *args, **kw'
        assert (info["arg0"], info["arg1"], info["arg2"], info["arg3"], info["arg4"]) == ('self', 'x', 'y', 'args', 'kw')

    def test_decorator(self):
        """test that a decorator is called, and properly calls the underlying function"""
        chatty_decorator = Decorators.decorator(self.chatty)
        chatty_g = chatty_decorator(self.g)
        result = chatty_g(3)
        assert result == 28
        assert self.g.calls[-1] == "Calling 'g'"

    def test_decorator_lambda(self):
        """test that a decorator is called, and properly calls the underlying function"""
        l = lambda x: x + 21
        assert l(3) == 24
        chatty_decorator = Decorators.decorator(self.chatty)
        chatty_l = chatty_decorator(l)
        assert chatty_l(3) == 24

    def test_decorator_signature(self):
        """tests that a decorated function retains the signature of the underlying function"""
        chatty_decorator = Decorators.decorator(self.chatty)
        chatty_f = chatty_decorator(self.f)
        info = Decorators.decorator_helpers.getinfo(self.f)
        chatty_info = Decorators.decorator_helpers.getinfo(chatty_f)
        assert info == chatty_info
        assert info.__doc__ == chatty_info.__doc__

    def test_extend_decorator(self):
        """tests that a decorated function can extend the underlying function"""
        ext_decorator = Decorators.decorator(self.extdec, ['y', ('z', 3)])
        ext_g = ext_decorator(self.g)
        assert ext_g(100, 4) == 100 + 12 + 25
        assert self.g.calls[-1] == "Called with x=100, y=4, z=3"

    def test_extend_decorator_signature(self):
        """tests that a decorated function can extend the signature of the underlying function"""
        ext_decorator = Decorators.decorator(self.extdec, ['y', ('z', 3)])
        ext_g = ext_decorator(self.g)
        info = Decorators.decorator_helpers.getinfo(self.g)
        ext_info = Decorators.decorator_helpers.getinfo(ext_g)
        assert ext_info.__doc__ == info.__doc__
        assert ext_info["name"] == info["name"]
        assert ext_info["argnames"] == ['x', 'y', 'z']
        assert ext_info["defarg"] == (3,)
        assert ext_info["shortsign"] == 'x, y, z'
        assert ext_info["fullsign"] == 'x, y, z=defarg[0]'
        assert ext_info["arg0"] == 'x'
        assert ext_info["arg1"] == 'y'
        assert ext_info["arg2"] == 'z'

    def test_extend_decorator_existing(self):
        """tests that a decorated function can extend the underlying function, handling existing arguments right"""
        ext_decorator = Decorators.decorator(self.extdec2, [('y', 5), ('z', 3), ('x', 0)])
        ext_g = ext_decorator(self.g2)
        info = Decorators.decorator_helpers.getinfo(self.g2)
        ext_info = Decorators.decorator_helpers.getinfo(ext_g)
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
        assert self.g2.calls[-1] == "Called with x=0, y=5, z=3"

class TestSelfLocking(object):

    def test_foo(self):
        THREADS = 4

        class Foo(object):
            lock = threading.Lock()
            res = []

            @Decorators.SelfLocking.runwithlock
            def haslock(self,i):
                self.res.append(i)
                time.sleep(0.5)
                self.res.append(i)

        threads = []
        for i in range(THREADS):
            threads.append(threading.Thread(target=Foo().haslock,args=[i]))

        for thrd in threads:
            thrd.start()

        for thrd in threads:
            thrd.join()

        assert len(Foo.res) == 2*THREADS
        for i in range(THREADS):
            assert Foo.res[2*i] == Foo.res[2*i+1]

def TestNotImplemented(object):

    def test_noimp(self):
        @Decorators.notimplemented
        def f(x,y):
            """Should be overridden elsewhere."""
            pass

        py.test.raises(NotImplementedError,f,1,2)
