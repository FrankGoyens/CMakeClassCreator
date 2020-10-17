""" Module to interpret a cmake list item string as a path """

from abc import ABC, abstractmethod

class ListItemStringAsPathException(Exception):
    pass

class _FilenameProviderTrait(ABC):
    @abstractmethod
    def source_file_name(self):
        pass

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