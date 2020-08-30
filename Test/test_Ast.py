import unittest

import context

from CMakeClassCreator import ast

class TestAst(unittest.TestCase):
    def test_parse_set_normal_variable(self):
        givenAst = ast.Ast()
        result = givenAst.parse("set(TabsPls_Source main.cpp)")

        expected_result = ast.SetNormalVariable("TabsPls_Source", ast.CMakeStringList([ast.ListItemString("main.cpp")])) 

        self.assertTrue(list(result)[0].is_same(expected_result))

    def test_parse_set_normal_variable_using_other_variable(self):
        givenAst = ast.Ast()
        result = givenAst.parse("set(TabsPls_Source ${{other_var}})")

        expected_result = ast.SetNormalVariable("TabsPls_Source", ast.CMakeStringList([ast.VariableUse("other_var")])) 

        self.assertTrue(list(result)[0].is_same(expected_result))

if __name__ == '__main__':
    unittest.main()
