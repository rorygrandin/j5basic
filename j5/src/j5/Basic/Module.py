#!/usr/bin/env python

import logging
import os

importedmodules = {}

def resolvemodule(modulename, loglevel=logging.WARN):
    """Imports a.b.c as far as possible then returns the value of a.b.c.d.e"""
    if importedmodules.has_key(modulename):
        return importedmodules[modulename]

    try:
        parentmodule = getimportablemodule(modulename, loglevel)
    except (ImportError, SyntaxError), e:
        logging.log(loglevel, "Could not import module for %s" % (modulename))
        raise
    try:
        module = getpart(parentmodule, modulename)
    except AttributeError, e:
        logging.log(loglevel, "Could not resolve modulename %s" % (modulename))
        raise
    importedmodules[modulename] = module
    return module

def canonicalize(path):
    """returns the canonical reference to the path that can be used for comparison to other paths"""
    return os.path.normpath(os.path.realpath(os.path.abspath(path)))

thisfilename = canonicalize(__file__)
if thisfilename.endswith(".pyc") or thisfilename.endswith(".pyo"):
    thisfilename = thisfilename[:-1]

def getimportablemodule(modulename, loglevel=logging.WARN):
    """Attempts to import successive modules on the a.b.c route - first a.b.c, then a.b, etc. Only goes one level up"""
    components = modulename.split('.')
    module = None
    component_depth = len(components)
    errormessage = ""
    if component_depth > 1:
        parentmodulename = ".".join(components[:-1])
        try:
            parentmodule = __import__(parentmodulename)
        except ImportError, error:
            # if we get an import error on the parent module, we're unlikely to be able to import the child
            logging.log(loglevel, "Import Error attempting to import %s (parent of %s): %s" % (parentmodulename, modulename, error))
            raise
        except StandardError, error:
            logging.debug("Error attempting to import %s: %s" % (parentmodulename, error))
            raise
    try:
        module = __import__(modulename)
        return module
    except ImportError, error:
        logging.debug("Import Error attempting to import %s (but have parent module to return): %s" % (modulename, error))
        if component_depth > 1:
            return parentmodule
        raise
    except StandardError, error:
        logging.debug("Error attempting to import %s: %s" % (modulename, error))
        raise

def getpart(module, partname):
    components = partname.split('.')
    for component in components[1:]:
        module = getattr(module, component)
    return module


