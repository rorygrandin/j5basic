__author__ = 'matth'

def import_def_from(other_module_name, myvars):
    for key, val in vars(__import__(other_module_name)).iteritems():
        if key.startswith('__') and key.endswith('__'):
            continue
        myvars[key] = val