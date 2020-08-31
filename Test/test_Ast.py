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
        result = givenAst.parse("set(TabsPls_Source ${other_var})")

        expected_result = ast.SetNormalVariable("TabsPls_Source", ast.CMakeStringList([ast.VariableUse("other_var")])) 

        self.assertTrue(list(result)[0].is_same(expected_result))

    def test_parse_set_normal_variable_using_other_variable_in_quotes(self):
        givenAst = ast.Ast()
        result = givenAst.parse("set(TabsPls_Source \"${other_var}\")")

        expected_result = ast.SetNormalVariable("TabsPls_Source", ast.CMakeStringList([ast.VariableUse("other_var")])) 

        self.assertTrue(list(result)[0].is_same(expected_result))

    def test_parse_quoted_list_item(self):
        givenAst = ast.Ast()
        result = givenAst.parse("set(TabsPls_Source \"anything can be put here, and it will be only one item\")")

        expected_result = ast.SetNormalVariable("TabsPls_Source", ast.CMakeStringList([ast.ListItemString("\"anything can be put here, and it will be only one item\"")])) 

        self.assertTrue(list(result)[0].is_same(expected_result))

    def test_parse_quoted_list_item_containing_variable_use(self):
        givenAst = ast.Ast()
        result = givenAst.parse("set(TabsPls_Source \"anything can be put here, and it will be only one item, even with a ${variable}\")")

        expected_result = ast.SetNormalVariable("TabsPls_Source", ast.CMakeStringList([ast.ListItemString("\"anything can be put here, and it will be only one item, even with a ${variable}\"")])) 

        self.assertTrue(list(result)[0].is_same(expected_result))
        
    def test_parse_quoted_list_item_containing_multiple_items(self):
        givenAst = ast.Ast()
        result = givenAst.parse("set(TabsPls_Source " \
                + "\"anything can be put here, and it will be only one item, even with a ${variable}\"\n"
                + "main.cpp\n" \
                + "${other_var}\n" \
                + "\"${another_var_in_quotes}\"\n" \
                + "#a comment that will be ignored\n" \
                + '"a complete line with only text"\n' \
                + ")"
                )

        expected_result = ast.SetNormalVariable("TabsPls_Source", ast.CMakeStringList( 
            [ast.ListItemString("\"anything can be put here, and it will be only one item, even with a ${variable}\""), 
                    ast.ListItemString("main.cpp"), 
                    ast.VariableUse("other_var"), 
                    ast.VariableUse("another_var_in_quotes"),
                    ast.ListItemString('"a complete line with only text"')])) 

        self.assertTrue(list(result)[0].is_same(expected_result))

    def test_parse_add_library(self):
        givenAst = ast.Ast()
        result = givenAst.parse("add_library(TabsPlsLib file.h file.cpp)")

        expected_result = ast.AddLibrary("TabsPlsLib", ast.CMakeStringList([ast.ListItemString("file.h"), ast.ListItemString("file.cpp")])) 

        self.assertTrue(list(result)[0].is_same(expected_result))

    def test_parse_add_library_with_type(self):
        givenAst = ast.Ast()
        result = givenAst.parse("add_library(TabsPlsLib STATIC file.h file.cpp)")

        expected_result = ast.AddLibrary("TabsPlsLib", ast.CMakeStringList([ast.ListItemString("file.h"), ast.ListItemString("file.cpp")])) 

        self.assertTrue(list(result)[0].is_same(expected_result))

    def test_parse_add_library_with_type_and_flag(self):
        givenAst = ast.Ast()
        result = givenAst.parse("add_library(TabsPlsLib STATIC EXCLUDE_FROM_ALL file.h file.cpp)")

        expected_result = ast.AddLibrary("TabsPlsLib", ast.CMakeStringList([ast.ListItemString("file.h"), ast.ListItemString("file.cpp")])) 

        self.assertTrue(list(result)[0].is_same(expected_result))

    def test_parse_add_executable(self):
        givenAst = ast.Ast()
        result = givenAst.parse("add_executable(TabsPls ${TabsPls_Headers} ${TabsPls_Sources} main.cpp)")
        
        expected_result = ast.AddExecutable("TabsPls", ast.CMakeStringList([ast.VariableUse("TabsPls_Headers"), ast.VariableUse("TabsPls_Sources"), ast.ListItemString("main.cpp")]))

        self.assertTrue(list(result)[0].is_same(expected_result))

    def test_parse_add_executable_win32_flag(self):
        givenAst = ast.Ast()
        result = givenAst.parse("add_executable(TabsPls WIN32 ${TabsPls_Headers} ${TabsPls_Sources} main.cpp)")
        
        expected_result = ast.AddExecutable("TabsPls", ast.CMakeStringList([ast.VariableUse("TabsPls_Headers"), ast.VariableUse("TabsPls_Sources"), ast.ListItemString("main.cpp")]))

        self.assertTrue(list(result)[0].is_same(expected_result))

    def test_parse_add_executable_osx_bundle_flag(self):
        givenAst = ast.Ast()
        result = givenAst.parse("add_executable(TabsPls MACOSX_BUNDLE ${TabsPls_Headers} ${TabsPls_Sources} main.cpp)")
        
        expected_result = ast.AddExecutable("TabsPls", ast.CMakeStringList([ast.VariableUse("TabsPls_Headers"), ast.VariableUse("TabsPls_Sources"), ast.ListItemString("main.cpp")]))

        self.assertTrue(list(result)[0].is_same(expected_result))

    def test_parse_add_executable_exclude_from_all_flag(self):
        givenAst = ast.Ast()
        result = givenAst.parse("add_executable(TabsPls MACOSX_BUNDLE EXCLUDE_FROM_ALL ${TabsPls_Headers} ${TabsPls_Sources} main.cpp)")
        
        expected_result = ast.AddExecutable("TabsPls", ast.CMakeStringList([ast.VariableUse("TabsPls_Headers"), ast.VariableUse("TabsPls_Sources"), ast.ListItemString("main.cpp")]))

        self.assertTrue(list(result)[0].is_same(expected_result))

    def test_parse_target_sources(self):
        givenAst = ast.Ast()
        result = givenAst.parse("target_sources(TabsPls PRIVATE file_linux.h file_linux.cpp ${TabsPls_Sources_Linux} PUBLIC linux_extras.h)")
        
        expected_result = ast.TargetSources("TabsPls", ast.CMakeStringList([ast.ListItemString("file_linux.h"), ast.ListItemString("file_linux.cpp"), ast.VariableUse("TabsPls_Sources_Linux"), ast.ListItemString("linux_extras.h")]))

        self.assertTrue(list(result)[0].is_same(expected_result))


if __name__ == '__main__':
    unittest.main()
