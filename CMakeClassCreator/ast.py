from CMakeClassCreator.parser import Parser

class VariableUse(object):
    def __init__(self, var_name):
        self.var_name = var_name

    def is_same(self, other):
        return isinstance(other, VariableUse) \
                and self.var_name == other.var_name

class ListItemString(object):
    def __init__(self, list_item_string):
        self.list_item_string = list_item_string
        
    def is_same(self, other):
        return isinstance(other, ListItemString) \
                and self.list_item_string == other.list_item_string

class CMakeStringList(object):
    def __init__(self, items):
        self.items = items

    def is_same(self, other):
        if not isinstance(other, CMakeStringList):
            return False

        if len(self.items) != len(other.items):
            return False

        for first, second in zip(self.items, other.items):
            if not first.is_same(second):
                return False
        
        return True

class SetNormalVariable(object):
    def __init__(self, var_name, cmake_string_list):
        self.var_name = var_name
        self.cmake_string_list = cmake_string_list

    def is_same(self, other):
        return isinstance(other, SetNormalVariable) \
                and self.var_name == other.var_name \
                and self.cmake_string_list.is_same(other.cmake_string_list)

class Ast(object):
    """
    This uses the parser to create parsed objects
    """
    def __init__(self):
        self._parser = Parser()

        self._parser._set_normal_variable_stmt.setParseAction(self._parse_set_normal_variable_action)
        self._parser._variable_use_in_string_list.setParseAction(self._parse_variable_use_action)
        self._parser._string_list_item.setParseAction(self._parse_list_item_string_action)
        self._parser._cmake_list_content.setParseAction(self._parse_cmake_string_list_action)

    def parse(self, string):
        return self._parser._cmake_stmt.parseString(string)

    def _parse_variable_use_action(self, s, loc, toks):
        var_name = toks[1]
        return VariableUse(var_name)

    def _parse_list_item_string_action(self, s, loc, toks):
        list_item_string = toks[0]
        return ListItemString(list_item_string)

    def _parse_cmake_string_list_action(self, s, loc, toks):
        return CMakeStringList(toks)

    def _parse_set_normal_variable_action(self, s, loc, toks):
        var_name = toks[2]
        cmake_string_list = toks[3]
        return SetNormalVariable(var_name, cmake_string_list)

        
