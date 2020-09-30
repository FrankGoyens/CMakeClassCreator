from CMakeClassCreator import source_inserter

class ClassInserterException(Exception):
    pass

_implementation_extensions = [".c", ".C", ".c++", ".cc", ".cpp", ".cxx"]
_header_extensions = [".hpp", ".h", ".hh", ".h++", ".hpp", ".hxx"]

def insert_class_next_to_other_class(cmake_ast, class_name, reference_class_name):
    header_insert_action = _insert_source_next_to_other_source(cmake_ast, class_name, reference_class_name, _header_extensions)

    if not header_insert_action:
        raise ClassInserterException("The header file of reference class {0} can't be found in (supported) cmake statements, tried extensions {1}".format( \
            reference_class_name, _header_extensions))

    implementation_insert_action = _insert_source_next_to_other_source(cmake_ast, class_name, reference_class_name, _implementation_extensions)

    if not implementation_insert_action:
        raise ClassInserterException("The implementation file of reference class {0} can't be found in (supported) cmake statements, tried extensions {1}".format( \
            reference_class_name, _implementation_extensions))

    return (header_insert_action, implementation_insert_action)

def _insert_source_next_to_other_source(cmake_ast, source_name, reference_source_name, extensions):
    insert_action = None
    for extension in extensions:
        try:
            insert_action = source_inserter.insert_source_item_next_to_other_source(cmake_ast, source_name + extension, reference_source_name + extension)
            break
        except source_inserter.SourceInserterException:
            pass
    return insert_action