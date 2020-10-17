import unittest
from collections import namedtuple

import context

from CMakeClassCreator import list_item_string_path

class TestListItemStringPath(unittest.TestCase):
    def test_is_cmake_path(self):
        self.assertTrue(list_item_string_path.is_cmake_path("include/testlib/testlib.h"))
        self.assertTrue(list_item_string_path.is_cmake_path("${dir}/testlib/testlib.h"))
        self.assertFalse(list_item_string_path.is_cmake_path("testlib.h"))

    def test_interpret_list_item_string_as_path(self):
        given_ast = namedtuple("ListItemAst", ["list_item_string"])

        given_ast.list_item_string = "include/testlib/testlib.h"
        self.assertEqual(list_item_string_path.interpret_list_item_string_as_path(given_ast).source_file_name, "testlib.h")

        given_ast.list_item_string = "${dir}/testlib/testlib.h"
        self.assertEqual(list_item_string_path.interpret_list_item_string_as_path(given_ast).source_file_name, "testlib.h")

    def test_interpret_list_item_string_requires_list_item_string(self):
        self.assertRaises(list_item_string_path.ListItemStringAsPathException, list_item_string_path.interpret_list_item_string_as_path, None)

if __name__ == "__main__":
    unittest.main()