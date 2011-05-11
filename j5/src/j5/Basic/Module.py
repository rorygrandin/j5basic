#!/usr/bin/env python

import imp
import logging
import os

importedmodules = {}

def find_module(modulename):
    """finds the filename of the module with the given name (supports submodules)"""
    module_parts = modulename.split(".")
    search_path = None
    for part in module_parts:
        next_path = imp.find_module(part, search_path)[1]
        if next_path is None:
            raise ValueError("Could not find %s (reached %s at %s)" % (modulename, part, search_path))
        search_path = [next_path]
    return search_path[0]

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
        except Exception, error:
            logging.log(loglevel, "Error attempting to import %s: %s" % (parentmodulename, error))
            raise
    try:
        module = __import__(modulename)
        return module
    except ImportError, error:
        if component_depth > 1:
            logging.debug("Import Error attempting to import %s (but have parent module to return): %s" % (modulename, error))
            return parentmodule
        logging.log(loglevel, "Error attempting to import %s: %s" % (modulename, error))
        raise
    except Exception, error:
        logging.log(loglevel, "Error attempting to import %s: %s" % (modulename, error))
        raise

def getpart(module, partname):
    components = partname.split('.')
    for component in components[1:]:
        module = getattr(module, component)
    return module

def get_all_distinct_hierarchical_targets(obj, functionname):
    """Gets a list of all distinct instances of functionname in the mro"""
    for t in reversed(obj.__mro__):
        base_hook_fn = getattr(t, functionname, None)
        if base_hook_fn:
            t_f = base_hook_fn.im_func
            if t_f not in sources:
                sources[t_f] = t
                sources[t] = (t_f, base_hook_fn)
                targets.append(base_hook_fn)
                for base in t.__mro__[1:]:
                    if base in sources:
                        r_f, r_m = sources[base]
                        if r_m in targets:
                            targets.remove(r_m)
    return list(reversed(targets))

