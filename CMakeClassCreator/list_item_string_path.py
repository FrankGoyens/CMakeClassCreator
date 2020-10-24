""" Module to interpret a cmake list item string as a path """

from abc import ABC, abstractmethod

separator = "/"

class ListItemStringAsPathException(Exception):
    pass

class _FilenameProviderTrait(ABC):
    @abstractmethod
    def source_file_name(self):
        pass

class _ParentPathProviderTrait(ABC):
    @abstractmethod
    def parent_path(self):
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

    def __add__(self, other):
        if isinstance(other, PathAwareListItemString):
            return PathAwareListItemString(self.list_item_string_reference + other.list_item_string_reference)
        elif isinstance(other, str):
            return PathAwareListItemString(self.list_item_string_reference + other)
        else:
            return super().__add__(other)

class ListItemStringAsPath(_FilenameProviderTrait, _ParentPathProviderTrait):
    def __init__(self, list_item_string):
        self.list_item_string = list_item_string

    @property
    def source_file_name(self):
        return self.list_item_string.split(separator)[-1]

    @property
    def parent_path(self):
        source_file_name = self.source_file_name
        return self.list_item_string[:len(self.list_item_string) - len(self.source_file_name)]

def interpret_list_item_string_as_path(list_item_ast):
    if not hasattr(list_item_ast, "list_item_string"):
        raise ListItemStringAsPathException("Only a list item string can be interpreted as a path")

    return ListItemStringAsPath(list_item_ast.list_item_string)

def is_cmake_path(list_item_string):
    return separator in list_item_string.lstrip(separator).rstrip(separator)

def strip_trailing_separator(list_item_string):
    return list_item_string.rstrip(separator)