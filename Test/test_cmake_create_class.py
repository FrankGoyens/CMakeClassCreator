import unittest

import context

import cmake_create_class

class FakeArgs(object):
    def __init__(self):
        self.single_file = None
        self.reference_class = None
        self.target = None
        self.variable = None
        self.name = "classname"

class TestCMakeCreateClass(unittest.TestCase):
    def test_single_file_mode_either_has_reference_or_variable_or_target(self):
        given_args = FakeArgs()

        given_args.single_file = True
        self.assertRaises(cmake_create_class.CMakeClassCreatorException, cmake_create_class.validate_args, given_args)
        
        given_args.target = "faketarget"
        cmake_create_class.validate_args(given_args)
        given_args.target = None

        given_args.variable = "fakevariable"
        cmake_create_class.validate_args(given_args)

        given_args.variable = None
        given_args.reference_class = "ref"
        cmake_create_class.validate_args(given_args)


    def test_single_file_mode_without_ref_cant_have_both_variable_and_target(self):
        given_args = FakeArgs()

        given_args.single_file = True
        given_args.target = "faketarget"
        given_args.variable = "fakevariable"
        self.assertRaises(cmake_create_class.CMakeClassCreatorException, cmake_create_class.validate_args, given_args)

    def test_single_file_mode_with_reference_cant_have_variable_or_target(self):
        given_args = FakeArgs()

        given_args.single_file = True
        given_args.reference_class = "fakeref"
        cmake_create_class.validate_args(given_args)
        
        given_args.variable = "fakevariable"
        self.assertRaises(cmake_create_class.CMakeClassCreatorException, cmake_create_class.validate_args, given_args)

        given_args.variable = None
        given_args.target = "faketarget"
        self.assertRaises(cmake_create_class.CMakeClassCreatorException, cmake_create_class.validate_args, given_args)

    def test_single_file_mode_with_variable_or_target_cant_have_reference(self):
        given_args = FakeArgs()

        given_args.single_file = True
        given_args.variable = "fakevariable"
        cmake_create_class.validate_args(given_args)

        given_args.reference_class = "fakeref"
        self.assertRaises(cmake_create_class.CMakeClassCreatorException, cmake_create_class.validate_args, given_args)

        given_args.variable = None
        given_args.target = "faketarget"
        self.assertRaises(cmake_create_class.CMakeClassCreatorException, cmake_create_class.validate_args, given_args)

    def test_adding_class_requires_reference(self):
        given_args = FakeArgs()

        self.assertRaises(cmake_create_class.CMakeClassCreatorException, cmake_create_class.validate_args, given_args)

        given_args.reference_class = "fakeref"
        cmake_create_class.validate_args(given_args)


if __name__ == "__main__":
    unittest.main()