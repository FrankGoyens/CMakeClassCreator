import argparse

from collections import namedtuple

from CMakeClassCreator import list_item_string_path

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
        validate_args_single_file_mode(args)
    else:
        validate_args_class_mode(args)

def using_single_file_mode(args):
    return args.single_file or args.variable or args.target

def validate_args_single_file_mode(args):
    if args.reference_class:
        if args.variable or args.target:
            raise CMakeClassCreatorException("In single file mode, it is not allowed to specify a reference class and also a variable or target.")
    else:
        if not args.variable and not args.target:
            raise CMakeClassCreatorException("In single file mode, please specify a cmake variable or a cmake target using -var, --variable or -t, --target respectively.")
        if args.variable and args.target:
            raise CMakeClassCreatorException("In single file mode, it is not allowed to specify both a variable and a target.")

def validate_args_class_mode(args):
    if not args.reference_class:
        raise CMakeClassCreatorException("When adding a class, a reference class is required. Please specify one with -rc, --reference-class.")
    if list_item_string_path.is_cmake_path(args.name):
        raise CMakeClassCreatorException("When adding a class, the name of the class '{}' can't be a path.".format(args.name))

if __name__ == "__main__":
    args = create_arg_parser().parse_args()

    validate_args(args)
    print("Thank you for the valid arguments! All I can do right now is print this message, more functionality coming soon. Like adding {0} to {1}.".format(args.name, args.cmakelists))
