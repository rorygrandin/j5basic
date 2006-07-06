#!/usr/bin/env python

import logging
import inspect
import sys

importedmodules = {}

def resolvemodule(modulename, loglevel=logging.WARN):
    """Imports a.b.c as far as possible then returns the value of a.b.c.d.e"""
    if importedmodules.has_key(modulename):
        logging.debug("Returning cached object %s for %s" % (importedmodules[modulename],modulename))
        return importedmodules[modulename]

    try:
        parentmodule = getimportablemodule(modulename)
    except (ImportError, SyntaxError), e:
        logging.log(loglevel, "Could not import module %s" % (modulename))
        raise AttributeError(str(e))
    logging.debug("parentmodule for %s is %s" % (modulename, str(parentmodule)))
    try:
        module = getpart(parentmodule, modulename)
    except AttributeError, e:
        logging.log(loglevel, "Could not resolve modulename %s" % (modulename))
        raise
    importedmodules[modulename] = module
    logging.debug("Returning object %s for %s" % (module, modulename))
    return module

def getimportablemodule(modulename):
    """Attempts to import successive modules on the a.b.c route - first a.b.c, then a.b, etc"""
    components = modulename.split('.')
    module = None
    currentattempt = len(components)
    errormessage = ""
    while currentattempt > 0:
        try:
            attemptedname = '.'.join(components[:currentattempt])
            module = __import__(attemptedname)
            return module
        except ImportError, error:
            # FIXME: if the given module is found, but could not be imported, an error should be raised here
            logging.debug("Import Error attempting to import %s: %s" % (attemptedname, error))
            currentattempt -= 1
            errormessage = error
        except Exception, error:
            logging.debug("Error attempting to import %s: %s" % (attemptedname, error))
            raise
    raise ImportError("Error importing module %r: %s\nPython path is %r" % (modulename, errormessage, sys.path))

def getpart(module, partname):
    components = partname.split('.')
    for component in components[1:]:
        logging.debug("Getting part %s from module %s" % (component, str(module)))
        module = getattr(module, component)
    return module

def getcallingframe():
    try:
        # TODO: check whether this is ever needed - if not, use the exception code below
        stack = inspect.stack()
        return stack[2][0]
    except:
        return inspect.currentframe().f_back


