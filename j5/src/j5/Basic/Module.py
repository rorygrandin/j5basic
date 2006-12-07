#!/usr/bin/env python

import logging
import inspect
import sys
import os
import traceback

importedmodules = {}

def resolvemodule(modulename, loglevel=logging.WARN):
    """Imports a.b.c as far as possible then returns the value of a.b.c.d.e"""
    if importedmodules.has_key(modulename):
        logging.debug("Returning cached object %s for %s" % (importedmodules[modulename],modulename))
        return importedmodules[modulename]

    try:
        parentmodule = getimportablemodule(modulename)
    except (ImportError, SyntaxError), e:
        logging.log(loglevel, "Could not import module for %s" % (modulename))
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

def canonicalize(path):
    """returns the canonical reference to the path that can be used for comparison to other paths"""
    return os.path.normpath(os.path.realpath(os.path.abspath(path)))

thisfilename = canonicalize(__file__)
if thisfilename.endswith(".pyc") or thisfilename.endswith(".pyo"):
    thisfilename = thisfilename[:-1]

def getimportablemodule(modulename):
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
            logging.warning("Import Error attempting to import %s (parent of %s): %s" % (parentmodulename, modulename, error))
            raise
        except Exception, error:
            logging.debug("Error attempting to import %s: %s" % (parentmodulename, error))
            raise
    try:
        module = __import__(modulename)
        return module
    except ImportError, error:
        # if we get an import error on the parent module, we're unlikely to be able to import the child
        logging.debug("Import Error attempting to import %s (but have parent module to return): %s" % (modulename, error))
        if component_depth > 1:
            return parentmodule
        raise
    except Exception, error:
        logging.debug("Error attempting to import %s: %s" % (modulename, error))
        raise
    # FIXME: clear out the code below - the above should be clearer and simpler and not cause problems...

    while currentattempt > 0:
        try:
            attemptedname = '.'.join(components[:currentattempt])
            module = __import__(attemptedname)
            return module
        except ImportError, error:
            # if the ImportError originated from outside this file then raise it, otherwise continue
            cls, exc, trc = sys.exc_info()
            filename, line_number, function_name, text = traceback.extract_tb(trc, 10)[-1]
            if filename.endswith(".pyc") or filename.endswith(".pyo"):
                filename = filename[:-1]
            # need to compare to the canonical version of this filename - and make it case insensitive for windows drive letters
            # FIXME: this assumes that the relative path is relative to the current directory, which fails under py2exe with .pyc files if run from another directory
            if canonicalize(filename).lower() != thisfilename.lower():
                logging.warning("Import Error attempting to import %s (%s), comes from file %s which seems to be a real module that can't be imported" % (attemptedname, error, filename))
                logging.debug("ImportError came from filename %s, this file is %s" % (filename, thisfilename))
                raise
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


