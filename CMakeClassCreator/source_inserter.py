import CMakeClassCreator.ast as ast
from abc import ABC, abstractmethod

class SourceInserterException(Exception):
    pass

class InsertAction(object):
    def __init__(self, position, content):
        self.position = position
        self.content = content

    def do(self, full_cmake_source):
        content_before = full_cmake_source[:self.position-1]
        content_after = full_cmake_source[self.position-1:]
        return content_before + self.content + content_after

class _SourceInsertTrait(ABC):
    @abstractmethod
    def insert_source(self, source_item):
        pass

class _TargetNameTrait(ABC):
    @abstractmethod
    def get_name(self, cmake_ast):
        pass

class _SingleCMakeListAstTrait(ABC):
    @abstractmethod
    def get_cmake_list_ast(self):
        pass

class __SingleCMakeListInserter(_SourceInsertTrait, _SingleCMakeListAstTrait):
    def __init__(self, cmake_string_list):
        self.cmake_string_list = cmake_string_list

    def get_cmake_list_ast(self):
        return self.cmake_string_list

    def insert_source(self, source_item):
        position = _get_position_after_last_list_item(self.cmake_string_list)
        return InsertAction(position, " " + source_item)

class _AddLibraryInserter(_TargetNameTrait, __SingleCMakeListInserter):
    def __init__(self, add_library_ast):
        super().__init__(add_library_ast.cmake_string_list)
        self.add_library_ast = add_library_ast

    def get_name(self):
        return self.add_library_ast.library_name

class _AddExecutableInserter(_TargetNameTrait, __SingleCMakeListInserter):
    def __init__(self, add_executable_ast):
        super().__init__(add_executable_ast.cmake_string_list)
        self.add_executable_ast = add_executable_ast

    def get_name(self):
        return self.add_executable_ast.executable_name

class _SetNormalVariableInserter(__SingleCMakeListInserter):
    def __init__(self, set_normal_variable_ast):
        super().__init__(set_normal_variable_ast.cmake_string_list)
        self.set_normal_variable_ast = set_normal_variable_ast

class _TargetSourcesInserter(_TargetNameTrait, __SingleCMakeListInserter):
    def __init__(self, target_sources_ast):
        super().__init__(target_sources_ast.cmake_string_list)
        self.target_sources_ast = target_sources_ast

    def get_name(self):
        return self.target_sources_ast.target_name

def _get_position_after_last_list_item(cmake_string_list_ast):
    last_item = cmake_string_list_ast.items[-1]
    return last_item.location + 1 + len(last_item.list_item_string)

def insert_source_item_directly_in_target(cmake_ast, source_item, cmake_target):
    """ Sets up the action to add a source file directly to the add_{library|executable} statement of a given target """
    inserter = _make_inserter_for_target(cmake_ast, cmake_target)
    return inserter.insert_source(source_item)

def _make_inserter_for_target(cmake_ast, cmake_target):
    add_library_ast_items = [ast_item for ast_item in _get_all_library_targets(cmake_ast) if ast_item.library_name == cmake_target]
    add_executable_ast_items = [ast_item for ast_item in _get_all_executable_targets(cmake_ast) if ast_item.executable_name == cmake_target]

    inserters = [_AddLibraryInserter(add_library_ast) for add_library_ast in add_library_ast_items]
    inserters += [_AddExecutableInserter(add_executable_ast) for add_executable_ast in add_executable_ast_items]

    if len(inserters) == 0:
        raise SourceInserterException("The target {} is not found in the given cmake ast".format(cmake_target))

    if len(inserters) > 1:
        raise SourceInserterException("There are too many add_{executable, library} statements for target {}".format(cmake_target))

    return inserters[0]

def _get_all_library_targets(cmake_ast):
    return [ast_item for ast_item in cmake_ast if isinstance(ast_item, ast.AddLibrary)]

def _get_all_executable_targets(cmake_ast):
    return [ast_item for ast_item in cmake_ast if isinstance(ast_item, ast.AddExecutable)]

def insert_source_item_in_variable_from_target(cmake_ast, source_item, cmake_target, variable_name):
    """ Sets up the action to add a source file to the given variable of the given target """
    target_inserter = _make_inserter_for_target(cmake_ast, cmake_target)
    relevant_variable_declarations_in_target = [declaration for declaration in target_inserter.get_cmake_list_ast().items if isinstance(declaration, ast.VariableUse) and declaration.var_name == variable_name]

    if len(relevant_variable_declarations_in_target) == 0:
        raise SourceInserterException("The variable {0} is not used in target {1}".format(variable_name, cmake_target))

    variable_inserter = _make_inserter_for_variable_declaration(cmake_ast, variable_name)
    return variable_inserter.insert_source(source_item)

def insert_source_item_in_variable(cmake_ast, source_item, variable_name):
    """ Sets up the action to add a source file to the given variable

    Does the same thing as insert_source_item_in_variable_from_target without asserting the source belongs to a target
    """
    inserter = _make_inserter_for_variable_declaration(cmake_ast, variable_name)
    return inserter.insert_source(source_item)

def _make_inserter_for_variable_declaration(cmake_ast, variable_name):
    set_normal_variable_ast_items = _find_all_variable_declarations(cmake_ast)

    inserters = [_SetNormalVariableInserter(declaration) for declaration in set_normal_variable_ast_items if declaration.var_name == variable_name]
    
    if len(inserters) == 0:
        raise SourceInserterException("The variable declaration {} is not found in the given cmake ast".format(variable_name))

    if len(inserters) > 1:
        raise SourceInserterException("There is more than one variable declaration statements with variable name {}".format(variable_name))

    return inserters[0]

def _find_all_variable_declarations(cmake_ast):
    return [ast_item for ast_item in cmake_ast if isinstance(ast_item, ast.SetNormalVariable)]

def insert_source_item_next_to_other_source(cmake_ast, source_item, reference_item):
    """ Sets up the action to add a source file in the same way as the reference source file

    The reference source file should already exist in the cmake source
    """
    try:
        target = _find_reference_directly_in_target_declaration(cmake_ast, reference_item)
        inserter =  _AddLibraryInserter(target) if isinstance(target, ast.AddLibrary) else _AddExecutableInserter(target)
        return inserter.insert_source(source_item)
    except SourceInserterException:
        pass

    try:
        declaration = _find_reference_in_variable_declaration(cmake_ast, reference_item)
        return _SetNormalVariableInserter(declaration).insert_source(source_item)
    except SourceInserterException:
        pass

    try:
        target_sources_stmt = _find_reference_in_target_sources_stmt(cmake_ast, reference_item)
        return _TargetSourcesInserter(target_sources_stmt).insert_source(source_item)
    except SourceInserterException:
        pass

    raise SourceInserterException("The reference item {} is not declared in any (supported) cmake statement".format(reference_item))


def _find_reference_directly_in_target_declaration(cmake_ast, reference_item):
    all_targets = _get_all_library_targets(cmake_ast) + _get_all_executable_targets(cmake_ast)
    cmake_lists_with_target = [(target.cmake_string_list, target) for target in all_targets]
    relevant_cmake_lists_with_target = [cmake_lists_with_target for cmake_lists_with_target in cmake_lists_with_target if _contains_source_item(cmake_lists_with_target[0], reference_item)]

    if len(relevant_cmake_lists_with_target) == 0:
        raise SourceInserterException("The reference item {} is not declared in a target".format(reference_item))
    if len(relevant_cmake_lists_with_target) > 1:
        raise SourceInserterException("The reference item {0} is defined in multiple targets: {1}".format(reference_item, \
            [cmake_list_with_target[0] for cmake_list_with_target in cmake_lists_with_target]))

    return relevant_cmake_lists_with_target[0][1]

def _find_reference_in_variable_declaration(cmake_ast, reference_item):
    relevant_variable_declarations = [declaration for declaration in cmake_ast if isinstance(declaration, ast.SetNormalVariable) \
        and _contains_source_item(declaration.cmake_string_list, reference_item)]
    
    if len(relevant_variable_declarations) == 0:
        raise SourceInserterException("The reference item {} is not declared in a variable declaration".format(reference_item))
    if len(relevant_variable_declarations) > 1:
        raise SourceInserterException("The reference item {0} is defined in multiple variable declarations: {1}".format(reference_item, \
            [declaration.var_name for declaration in relevant_variable_declarations]))

    return relevant_variable_declarations[0]

def _find_reference_in_target_sources_stmt(cmake_ast, reference_item):
    relevant_target_sources = [target_sources_stmt for target_sources_stmt in cmake_ast if isinstance(target_sources_stmt, ast.TargetSources) \
        and _contains_source_item(target_sources_stmt.cmake_string_list, reference_item)]
    
    if len(relevant_target_sources) == 0:
        raise SourceInserterException("The reference item {} is not declared in a target_sources statement".format(reference_item))
    if len(relevant_target_sources) > 1:
        raise SourceInserterException("The reference item {0} is defined in multiple target_sources statements: {1}".format(reference_item, \
            ["target_sources({})".format(target_sources_stmt.target_name) for target_sources_stmt in relevant_target_sources]))

    return relevant_target_sources[0]

def _contains_source_item(cmake_string_list, source_item):
    try:
        next(list_item for list_item in cmake_string_list.items if isinstance(list_item, ast.ListItemString) and list_item.list_item_string == source_item)
        return True
    except StopIteration:
        return False
