
import unittest

import context

from CMakeClassCreator import whitespace_inserter, ast

class TestWhitespaceInserter(unittest.TestCase):
    def test_get_content_between_second_to_last_and_last_item(self):
        given_ast = ast.CMakeStringList([ast.ListItemStringWithLocation("file1.cpp", 10), ast.ListItemStringWithLocation("file2.cpp", 20)])

        given_source = "abcdefghijklmnopqrstuvwxyz"

        result_content = whitespace_inserter.get_content_between_second_to_last_and_last_item(given_source, given_ast)
        self.assertEqual(result_content, "t")

    def test_get_content_between_second_to_last_and_last_item_with_only_one_item(self):
        given_ast = ast.CMakeStringList([ast.ListItemString("file1.cpp")])
        given_ast_empty = ast.CMakeStringList([])

        self.assertRaises(whitespace_inserter.LessThanTwoItemsException, whitespace_inserter.get_content_between_second_to_last_and_last_item,"", given_ast)
        self.assertRaises(whitespace_inserter.LessThanTwoItemsException, whitespace_inserter.get_content_between_second_to_last_and_last_item,"", given_ast_empty)

if __name__ == "__main__":
    unittest.main()
    