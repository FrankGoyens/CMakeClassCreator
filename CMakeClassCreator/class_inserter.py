from CMakeClassCreator import source_inserter

class ClassInserterException(Exception):
    pass

_implementation_extensions = [".c", ".C", ".c++", ".cc", ".cpp", ".cxx"]
_header_extensions = [".hpp", ".h", ".hh", ".h++", ".hpp", ".hxx"]

def insert_class_next_to_other_class(cmake_ast, class_name, reference_class_name):
    def inserter_and_source_to_action_considering_whitespace(inserter_with_reference, extension):
        return inserter_with_reference.inserter.insert_source(class_name + extension)

    return _insert_class_next_to_other_class_with_inserter_enhancement(cmake_ast, class_name, reference_class_name, \
        inserter_and_source_to_action_considering_whitespace)

def insert_class_next_to_other_class_with_whitespace_enhancement(full_cmake_source, cmake_ast, class_name, reference_class_name):
    def inserter_and_source_to_action_considering_whitespace(inserter_with_reference, extension):
        return source_inserter.insert_source_considering_existing_whitespace(inserter_with_reference, class_name + extension, full_cmake_source)

    return _insert_class_next_to_other_class_with_inserter_enhancement(cmake_ast, class_name, reference_class_name, \
        inserter_and_source_to_action_considering_whitespace)

def _insert_class_next_to_other_class_with_inserter_enhancement(cmake_ast, class_name, reference_class_name, inserter_and_extension_to_action):
    """ This function is agnostic about which enhancement will be done. 
    
    Customize the enhancement by providing a function as argument 'inserter_and_extension_to_action' and apply the enhancement therein"""
    header_inserter, header_extension = _make_inserter_for_item_next_to_other_source(cmake_ast, reference_class_name, _header_extensions)

    if not header_inserter:
        raise ClassInserterException("The header file of reference class {0} can't be found in (supported) cmake statements, tried extensions {1}".format( \
            reference_class_name, _header_extensions))

    implementation_inserter, implementation_extension = _make_inserter_for_item_next_to_other_source(cmake_ast, reference_class_name, _implementation_extensions)

    if not implementation_inserter:
        raise ClassInserterException("The implementation file of reference class {0} can't be found in (supported) cmake statements, tried extensions {1}".format( \
            reference_class_name, _implementation_extensions))

    return (inserter_and_extension_to_action(header_inserter, header_extension), 
        inserter_and_extension_to_action(implementation_inserter, implementation_extension))

def _make_inserter_for_item_next_to_other_source(cmake_ast, reference_source_name, extensions):
    for extension in extensions:
        try:
            inserter = source_inserter._make_inserter_for_item_next_to_other_source(cmake_ast, reference_source_name + extension)
            return inserter, extension
            break
        except source_inserter.SourceInserterException:
            pass
    return (None, None)