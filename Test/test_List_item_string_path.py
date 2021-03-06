import unittest
from collections import namedtuple

import context

from CMakeClassCreator import list_item_string_path

class TestListItemStringPath(unittest.TestCase):
    def test_is_cmake_path(self):
        self.assertTrue(list_item_string_path.is_cmake_path("include/testlib/testlib.h"))
        self.assertTrue(list_item_string_path.is_cmake_path("${dir}/testlib/testlib.h"))
        self.assertFalse(list_item_string_path.is_cmake_path("testlib.h"))
        self.assertFalse(list_item_string_path.is_cmake_path("/testlib.h"))

    def test_interpret_list_item_string_as_path(self):
        given_ast = namedtuple("ListItemAst", ["list_item_string"])

        given_ast.list_item_string = "include/testlib/testlib.h"
        self.assertEqual(list_item_string_path.interpret_list_item_string_as_path(given_ast).source_file_name, "testlib.h")

        given_ast.list_item_string = "${dir}/testlib/testlib.h"
        self.assertEqual(list_item_string_path.interpret_list_item_string_as_path(given_ast).source_file_name, "testlib.h")

        given_ast.list_item_string = "${dir}/testlib/"
        self.assertEqual(list_item_string_path.interpret_list_item_string_as_path(given_ast).source_file_name, "")

    def test_get_parent_path_from_list_item_string_path(self):
        given_ast = namedtuple("ListItemAst", ["list_item_string"])

        given_ast.list_item_string = "include/testlib/testlib.h"
        self.assertEqual(list_item_string_path.interpret_list_item_string_as_path(given_ast).parent_path, "include/testlib/")

        given_ast.list_item_string = "${dir}/testlib/testlib.h"
        self.assertEqual(list_item_string_path.interpret_list_item_string_as_path(given_ast).parent_path, "${dir}/testlib/")

        given_ast.list_item_string = "${dir}/testlib/"
        self.assertEqual(list_item_string_path.interpret_list_item_string_as_path(given_ast).parent_path, "${dir}/testlib/")

        given_ast.list_item_string = "${dir}/testlib"
        self.assertEqual(list_item_string_path.interpret_list_item_string_as_path(given_ast).parent_path, "${dir}/")

    def test_interpret_list_item_string_requires_list_item_string(self):
        self.assertRaises(list_item_string_path.ListItemStringAsPathException, list_item_string_path.interpret_list_item_string_as_path, None)

    def test_path_aware_list_item_string_equality(self):
        given_reference_source = "header.h"
        given_cmake_string_list_item = "include/testlib/header.h"
        self.assertEqual(list_item_string_path.PathAwareListItemString(given_reference_source), given_cmake_string_list_item)
        given_cmake_string_list_item = "include/testlib/other_header.h"
        self.assertNotEqual(list_item_string_path.PathAwareListItemString(given_reference_source), given_cmake_string_list_item)

    def test_path_aware_list_item_string_to_string(self):
        given_reference_source = "header.h"
        path_aware_reference = list_item_string_path.PathAwareListItemString(given_reference_source)
        self.assertEqual(str(path_aware_reference), "header.h")

    def test_path_aware_list_item_string_append_string(self):
        given_reference_source = "class"
        self.assertEqual(list_item_string_path.PathAwareListItemString(given_reference_source) + ".h", "class.h")

    def test_strip_trailing_separator(self):
        self.assertEqual(list_item_string_path.strip_trailing_separator("src/"), "src")
        self.assertEqual(list_item_string_path.strip_trailing_separator("src//"), "src")
        self.assertEqual(list_item_string_path.strip_trailing_separator("src"), "src")

if __name__ == "__main__":
    unittest.main()