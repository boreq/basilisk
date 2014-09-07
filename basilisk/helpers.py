import os
import shutil


def replace_ext(path, old, new):
    """Replaces extension in the path from old to new."""
    return path[:-len(old)] + new


def import_by_name(name):
    """Imports an object from a module. For example if passed name is
    `example.module.thing` this function will return an object called `thing`
    located in `example.module`. This behaviour is similar to normal import
    statement `from example.module import thing`.
    """
    name = name.split('.')
    obj = name[-1]
    module = '.'.join(name[:-1])
    return getattr(__import__(name=module, fromlist=[obj]), obj)


def remove_directory_contents(path):
    """Removes files and subdirectories located in a directory."""
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        if os.path.isdir(item_path):
            shutil.rmtree(item_path)
        else:
            os.remove(item_path)
