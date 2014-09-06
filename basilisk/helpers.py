def replace_ext(path, old, new):
    return path[:-len(old)] + new


def import_by_name(name):
    try:
        name = name.split('.')
        obj = name[-1]
        module = '.'.join(name[:-1])
        return getattr(__import__(name=module, fromlist=[obj]), obj)
    except:
        raise
