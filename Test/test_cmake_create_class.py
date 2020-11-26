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
    
    def test_class_mode_source_cant_be_path(self):
        given_args = FakeArgs()

        given_args.name = "source/file.cpp"
        given_args.reference_class = "source/dir.cpp"

        self.assertRaises(cmake_create_class.CMakeClassCreatorException, cmake_create_class.validate_args, given_args)

        given_args.name = "file.cpp"
        cmake_create_class.validate_args(given_args)

    def test_adding_single_file_may_be_path_unless_using_reference(self):
        given_args = FakeArgs()

        given_args.single_file = True
        given_args.name = "source/file.cpp"
        given_args.variable = "sources"

        cmake_create_class.validate_args(given_args)

        given_args.reference_class = "source/dir.cpp"
        self.assertRaises(cmake_create_class.CMakeClassCreatorException, cmake_create_class.validate_args, given_args)

    def test_paths_with_backslashes_are_invalid_in_any_configuration(self):
        given_args = FakeArgs()

        given_args.name = "source\\file.cpp"
        given_args.reference_class = "dir.cpp"

        self.assertRaises(cmake_create_class.CMakeClassCreatorException, cmake_create_class.validate_args, given_args)

        given_args.name = "file.cpp"
        given_args.reference_class = "source\\dir.cpp"

        self.assertRaises(cmake_create_class.CMakeClassCreatorException, cmake_create_class.validate_args, given_args)

class TestCMakeCreateClassSingleFileMode(unittest.TestCase):
    def test_insert_single_source_next_to_reference_in_full_cmake_source(self):
        given_full_source = \
            """
            project(TabsPlsTest)

            set(TabsPlsTest_Sources
                Test1.cpp
                Test2.cpp
            )

            add_executable(TabsPlsTest ${TabsPlsTest_Sources})
            """
        result_cmake_source = cmake_create_class._insert_single_source_next_to_reference_in_full_cmake_source(given_full_source, "Test3.cpp", "Test2.cpp")

        expected_cmake_source = \
            """
            project(TabsPlsTest)

            set(TabsPlsTest_Sources
                Test1.cpp
                Test2.cpp
                Test3.cpp
            )

            add_executable(TabsPlsTest ${TabsPlsTest_Sources})
            """
        
        self.assertEqual(expected_cmake_source, result_cmake_source)

    def test_insert_single_source_next_to_reference_in_full_cmake_source_path_aware(self):
        given_full_source = \
            """
            project(TabsPlsTest)

            set(TabsPlsTest_Sources
                Source/Test1.cpp
                Source/Test2.cpp
            )

            add_executable(TabsPlsTest ${TabsPlsTest_Sources})
            """
        result_cmake_source = cmake_create_class._insert_single_source_next_to_reference_in_full_cmake_source(given_full_source, "Test3.cpp", "Test2.cpp")

        expected_cmake_source = \
            """
            project(TabsPlsTest)

            set(TabsPlsTest_Sources
                Source/Test1.cpp
                Source/Test2.cpp
                Source/Test3.cpp
            )

            add_executable(TabsPlsTest ${TabsPlsTest_Sources})
            """
        
        self.assertEqual(expected_cmake_source, result_cmake_source)

if __name__ == "__main__":
    unittest.main()