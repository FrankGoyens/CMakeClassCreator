from CMakeClassCreator.parser import Parser
from abc import ABC, abstractmethod

class _LocationTrait(ABC):
    @abstractmethod
    def get_location(self):
        pass

class _EndLocationTrait(ABC):
    @abstractmethod
    def get_end_location(self):
        pass

### AST components ###
class VariableUseTerminator(object):
    def __init__(self, location):
        self.location = location

class VariableUse(object):
    def __init__(self, var_name):
        self.var_name = var_name

    def is_same(self, other):
        return isinstance(other, VariableUse) \
                and self.var_name == other.var_name

class VariableUseWithLocation(VariableUse, _LocationTrait):
    def __init__(self, var_name, location):
        super().__init__(var_name)
        self.location = location

    def is_same(self, other):
        if not isinstance(other, VariableUseWithLocation) and isinstance(other, VariableUse):
            return super().is_same(other)

        return isinstance(other, VariableUseWithLocation) \
            and self.location == other.location \
                and super().is_same(other)

    def get_location(self):
        return self.location

class VariableUseWithStartAndEndLocation(VariableUseWithLocation, _EndLocationTrait):
    def __init__(self, var_name, location, terminator):
        super().__init__(var_name, location)
        self.terminator = terminator

    def get_end_location(self):
        return self.terminator.location

class ListItemString(object):
    def __init__(self, list_item_string):
        self.list_item_string = list_item_string
        
    def is_same(self, other):
        return isinstance(other, ListItemString) \
            and self.list_item_string == other.list_item_string 
                
class ListItemStringWithLocation(ListItemString, _LocationTrait, _EndLocationTrait):
    def __init__(self, list_item_string, location):
        super().__init__(list_item_string)
        self.location = location

    def is_same(self, other):
        if not isinstance(other, ListItemStringWithLocation) and isinstance(other, ListItemString):
            return super().is_same(other)

        return isinstance(other, ListItemStringWithLocation) \
            and self.location == other.location \
                and super().is_same(other)

    def get_location(self):
        return self.location

    def get_end_location(self):
        return self.location + len(self.list_item_string)

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

class AddLibrary(object):
    def __init__(self, library_name, cmake_string_list):
        self.library_name = library_name
        self.cmake_string_list = cmake_string_list

    def is_same(self, other):
        return isinstance(other, AddLibrary) \
            and self.library_name == other.library_name \
            and self.cmake_string_list.is_same(other.cmake_string_list)

class AddExecutable(object):
    def __init__(self, executable_name, cmake_string_list):
        self.executable_name = executable_name
        self.cmake_string_list = cmake_string_list

    def is_same(self, other):
        return isinstance(other, AddExecutable) \
            and self.executable_name == other.executable_name \
            and self.cmake_string_list.is_same(other.cmake_string_list)

class TargetSources(object):
    def __init__(self, target_name, cmake_string_list):
        self.target_name = target_name
        self.cmake_string_list = cmake_string_list

    def is_same(self, other):
        return isinstance(other, TargetSources) \
            and self.target_name == other.target_name \
            and self.cmake_string_list.is_same(other.cmake_string_list)
### AST components END ###

def _parse_variable_use_terminator(s, loc, toks):
    return VariableUseTerminator(loc+1)

def _parse_variable_use_in_quotes_terminator(s, loc, toks):
    return VariableUseTerminator(loc+1)

def _parse_standalone_variable_use_action(s, loc, toks):
    var_name = toks[1]
    terminator = toks[2]
    return VariableUseWithStartAndEndLocation(var_name, loc, terminator)

def _parse_standalone_variable_use_in_quotes_action(s, loc, toks):
    var_name = toks[2]
    terminator = toks[4]
    return VariableUseWithStartAndEndLocation(var_name, loc, terminator)

def _parse_variable_use_to_compose_list_item(s, loc, toks):
    return toks

def _parse_list_item_string_action(s, loc, toks):
    list_item_string = toks[0]
    return ListItemStringWithLocation(list_item_string, loc)

def _parse_cmake_string_list_action(s, loc, toks):
    return CMakeStringList(toks)

def _parse_set_normal_variable_action(s, loc, toks):
    var_name = toks[2]
    cmake_string_list = toks[3]
    return SetNormalVariable(var_name, cmake_string_list)

def _parse_add_library_action(s, loc, toks):
    library_name = toks[2]
    cmake_string_list = next(item for item in toks if isinstance(item, CMakeStringList))
    return AddLibrary(library_name, cmake_string_list)

def _parse_add_normal_executable_action(s, loc, toks):
    executable_name = toks[2]
    cmake_string_list = next(item for item in toks if isinstance(item, CMakeStringList))
    return AddExecutable(executable_name, cmake_string_list)

def _parse_target_sources_action(s, loc, toks):
    target_name = toks[2]
    cmake_string_list = CMakeStringList([])
    for scoped_cmake_string_list in [tok for tok in list(toks) if isinstance(tok, CMakeStringList)]:
            cmake_string_list.items += list(scoped_cmake_string_list.items) 
    return TargetSources(target_name, cmake_string_list)

class Ast(object):
    def __init__(self):
        self._parser = Parser()

        self._parser._cmake_stmt.parseWithTabs() #cmake source may contain tabs, this ensures that match locations consider tabs as one character

        self._parser._variable_use_terminator.setParseAction(_parse_variable_use_terminator)
        self._parser._variable_use_in_quotes_terminator.setParseAction(_parse_variable_use_in_quotes_terminator)

        self._parser._standalone_variable_use.setParseAction(_parse_standalone_variable_use_action)
        self._parser._equivalent_variable_use_in_quotes.setParseAction(_parse_standalone_variable_use_in_quotes_action)
        self._parser._variable_use_to_compose_list_item.setParseAction(_parse_variable_use_to_compose_list_item)

        self._parser._string_list_item.setParseAction(_parse_list_item_string_action)
        self._parser._cmake_list_content.setParseAction(_parse_cmake_string_list_action)

        self._parser._set_normal_variable_stmt.setParseAction(_parse_set_normal_variable_action)

        self._parser._add_library_stmt.setParseAction(_parse_add_library_action)
        self._parser._add_normal_executable_stmt.setParseAction(_parse_add_normal_executable_action)
        self._parser._target_sources_stmt.setParseAction(_parse_target_sources_action)


    def parse(self, string):
        return self._parser._cmake_stmt.parseString(string)

    def scan_all(self, string):
        """ Scan the given string for supported cmake grammar, ignores unsupported content and returns all matches"""
        matches = []
        for (match, start, end) in self._parser._cmake_stmt.scanString(string):
            matches.append(match)
        return matches
        
