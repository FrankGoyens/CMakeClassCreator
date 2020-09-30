from CMakeClassCreator import source_inserter

class ClassInserterException(Exception):
    pass

_implementation_extensions = [".c", ".C", ".c++", ".cc", ".cpp", ".cxx"]
_header_extensions = [".h", ".hh", ".h++", ".hpp", ".hxx"]

def insert_class_next_to_other_class(cmake_ast, class_name, reference_class_name):
    header_insert_action = None
    for extension in _header_extensions:
        try:
            header_insert_action = source_inserter.insert_source_item_next_to_other_source(cmake_ast, class_name + extension, reference_class_name + extension)
            break
        except source_inserter.SourceInserterException:
            pass

    if not header_insert_action:
        raise ClassInserterException("The header file of reference class {0} can't be found in (supported) cmake statements, tried extensions {1}".format( \
            reference_class_name, _header_extensions))

    implementation_insert_action = None
    for extension in _implementation_extensions:
        try:
            implementation_insert_action = source_inserter.insert_source_item_next_to_other_source(cmake_ast, class_name + extension, reference_class_name + extension)
            break
        except source_inserter.SourceInserterException:
            pass

    if not implementation_insert_action:
        raise ClassInserterException("The implementation file of reference class {0} can't be found in (supported) cmake statements, tried extensions {1}".format( \
            reference_class_name, _implementation_extensions))

    return (header_insert_action, implementation_insert_action)