import argparse, os, pyparsing, sys

from collections import namedtuple

from CMakeClassCreator import list_item_string_path, class_inserter, ast, source_inserter

class CMakeClassCreatorException(Exception):
    pass

def create_arg_parser():
    parser = argparse.ArgumentParser(description="Create a new class by modifying CMake scripts.")
    parser.add_argument("cmakelists", help="The cmake script where the class will be added.")
    parser.add_argument("name", help="The name of the new class. In single file mode, this is the name of the file including file extension.")

    parser.add_argument("-rc", "--reference-class", help="Add the new class in the same way the reference class was added.")
    parser.add_argument("-i", "--inplace", action="store_true", help="Modify the cmake script in place instead of writing to stdout.")

    parser.add_argument("-s", "--single-file", action="store_true", help="Single file mode, only add a single file.")
    parser.add_argument("-var", "--variable", help="Implies single file mode. Add the source file to the given cmake variable.")
    parser.add_argument("-t", "--target", help="Implies single file mode. Add the source file to the given cmake target (library or executable).")
    return parser

def validate_args(args):
    if "\\" in args.name:
        raise CMakeClassCreatorException("It is not allowed to use backslashes in the class name.")

    if args.reference_class and "\\" in args.reference_class:
        raise CMakeClassCreatorException("It is not allowed to use backslashes in the reference class.")

    if using_single_file_mode(args):
        return validate_args_single_file_mode(args)
    else:
        return validate_args_class_mode(args)

def using_single_file_mode(args):
    return args.single_file or args.variable or args.target

def validate_args_single_file_mode(args):
    if args.reference_class:
        if args.variable or args.target:
            raise CMakeClassCreatorException("In single file mode, it is not allowed to specify a reference class and also a variable or target.")
        if list_item_string_path.is_cmake_path(args.name):
            raise CMakeClassCreatorException("In single file mode, when specifying a reference, the source name can't be a path.")
        return lambda args: insert_single_source_next_to_reference(args.cmakelists, args.name, args.reference_class)
    else:
        if not args.variable and not args.target:
            raise CMakeClassCreatorException("In single file mode, please specify a cmake variable or a cmake target using -var, --variable or -t, --target respectively.")
        if args.variable and args.target:
            raise CMakeClassCreatorException("In single file mode, it is not allowed to specify both a variable and a target.")
        if args.variable:
            return lambda args: insert_single_source_in_variable(args.cmakelists, args.name, args.variable)
        if args.target:
            return lambda args: insert_single_source_in_target(args.cmakelists, args.name, args.target)

def validate_args_class_mode(args):
    if not args.reference_class:
        raise CMakeClassCreatorException("When adding a class, a reference class is required. Please specify one with -rc, --reference-class.")
    if list_item_string_path.is_cmake_path(args.name):
        raise CMakeClassCreatorException("When adding a class, the name of the class '{}' can't be a path.".format(args.name))

    return lambda args: create_class(args.cmakelists, args.name, args.reference_class)

def create_class(cmakelists_path, class_name, reference_class_name):
    full_cmake_source = _read_cmakelists_contents(cmakelists_path)
    
    full_cmake_ast = _parse_cmakelists_contents(full_cmake_source)
    
    try:
        header_and_implementation_actions = class_inserter.insert_class_next_to_other_class_with_whitespace_enhancement(
            full_cmake_source, full_cmake_ast, class_name, list_item_string_path.PathAwareListItemString(reference_class_name))
    except class_inserter.ClassInserterException as e:
        raise CMakeClassCreatorException(str(e))

    full_cmake_source = _do_all_actions(list(header_and_implementation_actions), full_cmake_source)
    return full_cmake_source

def _read_cmakelists_contents(cmakelists_path):
    if not os.path.exists(cmakelists_path):
        raise CMakeClassCreatorException("{} can't be found.".format(cmakelists_path))

    with open(cmakelists_path, 'r') as cmakelists_file:
        return cmakelists_file.read()

def _parse_cmakelists_contents(full_cmake_source):
    full_cmake_ast = []
    try:
        full_cmake_ast = [match[0] for match in ast.Ast().scan_all(full_cmake_source)]
    except pyparsing.exceptions.ParseException as e:
        raise CMakeClassCreatorException("Unable to parse cmake file. Here is the pyparsing exception:\n\n{}".format(str(e)))

    if not full_cmake_ast:
        raise CMakeClassCreatorException("Unable to find any (supported) cmake statements in the given file.")

    return full_cmake_ast

def insert_single_source_next_to_reference(cmakelists_path, source_item, reference_source_item):
    full_cmake_source = _read_cmakelists_contents(cmakelists_path)
    
    _insert_single_source_next_to_reference_in_full_cmake_source(full_cmake_source, source_item, reference_source_item)

def _insert_single_source_next_to_reference_in_full_cmake_source(full_cmake_source, source_item, reference_source_item):
    full_cmake_ast = _parse_cmakelists_contents(full_cmake_source)

    reference_source_item = _make_reference_path_aware_if_needed(reference_source_item)

    inserter_with_reference = source_inserter._make_inserter_for_item_next_to_other_source(full_cmake_ast, 
        list_item_string_path.PathAwareListItemString(reference_source_item))
    try:
        insert_action = source_inserter.insert_source_considering_existing_whitespace(inserter_with_reference, source_item, full_cmake_source)
        return insert_action.do(full_cmake_source)
    except source_inserter.SourceInserterException as e:
        raise CMakeClassCreatorException(str(e))

def insert_single_source_in_variable(cmakelists_path, source_item, variable):
    full_cmake_source = _read_cmakelists_contents(cmakelists_path)
    
    full_cmake_ast = _parse_cmakelists_contents(full_cmake_source)

    try:
        inserter = source_inserter._make_inserter_for_variable_declaration(full_cmake_ast, variable)
        return source_inserter.insert_source_considering_existing_whitespace(inserter, source_item, full_cmake_source).do(full_cmake_source)
    except source_inserter.SourceInserterException as e:
        raise CMakeClassCreatorException(str(e))

def insert_single_source_in_target(cmakelists_path, source_item, target):
    full_cmake_source = _read_cmakelists_contents(cmakelists_path)
    
    full_cmake_ast = _parse_cmakelists_contents(full_cmake_source)

    try:
        inserter = source_inserter._make_inserter_for_target(full_cmake_ast, target)
        return source_inserter.insert_source_considering_existing_whitespace(inserter, source_item, full_cmake_source).do(full_cmake_source)
    except source_inserter.SourceInserterException as e:
        raise CMakeClassCreatorException(str(e))

def _make_reference_path_aware_if_needed(reference_source_item):
    return reference_source_item \
        if not list_item_string_path.is_cmake_path(reference_source_item) \
            else list_item_string_path.PathAwareListItemString(reference_source_item)

def _do_all_actions(actions, full_cmake_source):
    actions.sort(reverse=True, key=lambda action: action.position)
    for action in actions:
        full_cmake_source = action.do(full_cmake_source)
    return full_cmake_source

def main():
    args = create_arg_parser().parse_args()

    function_to_call = validate_args(args)
    if function_to_call is not None:
        try:
            output = function_to_call(args)
            if args.inplace:
                with open(args.cmakelists, 'w') as output_file:
                    output_file.write(output)
            else:
                print(output)
        except CMakeClassCreatorException as e:
            print(str(e), file=sys.stderr)
            
if __name__ == "__main__":
    main()