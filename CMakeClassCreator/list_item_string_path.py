""" Module to interpret a cmake list item string as a path """

from abc import ABC, abstractmethod

class ListItemStringAsPathException(Exception):
    pass

class _FilenameProviderTrait(ABC):
    @abstractmethod
    def source_file_name(self):
        pass

class PathAwareListItemString(object):
    """ Use this as a reference source in the source_inserter module in order to compare file names instead of te complete paths """
    def __init__(self, list_item_string_reference):
        self.list_item_string_reference = list_item_string_reference

    def __eq__(self, other):
        if isinstance(other, str):
            return self.list_item_string_reference == \
                ListItemStringAsPath(other).source_file_name
        return super().__eq__(other)
    
    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return self.list_item_string_reference

class ListItemStringAsPath(_FilenameProviderTrait):
    def __init__(self, list_item_string):
        self.list_item_string = list_item_string

    @property
    def source_file_name(self):
        return self.list_item_string.split("/")[-1]

def interpret_list_item_string_as_path(list_item_ast):
    if not hasattr(list_item_ast, "list_item_string"):
        raise ListItemStringAsPathException("Only a list item string can be interpreted as a path")

    return ListItemStringAsPath(list_item_ast.list_item_string)

def is_cmake_path(list_item_string):
    return "/" in list_item_string