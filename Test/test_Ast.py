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
        
        expected_result = ast.TargetSources("TabsPls", ast.CMakeStringList([ast.ListItemStringWithLocation("file_linux.h", 31), 
            ast.ListItemStringWithLocation("file_linux.cpp", 44), 
                ast.VariableUseWithLocation("TabsPls_Sources_Linux", 59), 
                    ast.ListItemStringWithLocation("linux_extras.h", 91)]))

        self.assertTrue(list(result)[0].is_same(expected_result))

    def test_scan_all_complete_project_source(self):
        given_source = ("project(TabsPls)\n"
            + "\tset(TabsPls_Headers File.hpp\n"
            + "Directory.hpp\n"
            + ")\n\n"
            + "set(TabsPls_Sources File.cpp\n"
            + "\tDirectory.cpp\n"
            + "\tMain.cpp\n"
            + ")\n\n"
            + "add_executable(TabsPls ${TabsPls_Headers} ${TabsPls_Sources})\n\n"
            + "target_sources(TabsPls PRIVATE windows_util.h windows_util.c)")

        given_ast = ast.Ast()
        matches = given_ast.scan_all(given_source)
        self.assertEqual(len(matches), 4)

        expected_first_match = ast.SetNormalVariable("TabsPls_Headers", 
            ast.CMakeStringList([ast.ListItemStringWithLocation("File.hpp", 38), ast.ListItemStringWithLocation("Directory.hpp", 47)]))
        self.assertTrue(list(matches[0])[0].is_same(expected_first_match))

        expected_second_match = ast.SetNormalVariable("TabsPls_Sources", 
            ast.CMakeStringList([ast.ListItemStringWithLocation("File.cpp", 84), ast.ListItemStringWithLocation("Directory.cpp", 94), ast.ListItemStringWithLocation("Main.cpp", 109)]))
        self.assertTrue(list(matches[1])[0].is_same(expected_second_match))

        expected_third_match = ast.AddExecutable("TabsPls", 
            ast.CMakeStringList([ast.VariableUseWithLocation("TabsPls_Headers", 144), ast.VariableUseWithLocation("TabsPls_Sources", 163)]))
        self.assertTrue(list(matches[2])[0].is_same(expected_third_match))

        expected_fourth_match = ast.TargetSources("TabsPls", 
            ast.CMakeStringList([ast.ListItemStringWithLocation("windows_util.h", 215), ast.ListItemStringWithLocation("windows_util.c", 230)]))
        self.assertTrue(list(matches[3])[0].is_same(expected_fourth_match))
    
    def test_list_item_string_with_terminator(self):
        given_ast = ast.Ast()

        result = given_ast._parser._string_list_item.parseString("dog.hpp")
        self.assertEqual(list(result)[0].location, 0)
        self.assertEqual(list(result)[0].get_end_location(), 7)

        result = given_ast._parser._string_list_item.parseString('"dog.hpp"')
        self.assertEqual(list(result)[0].location, 0)
        self.assertEqual(list(result)[0].get_end_location(), 9)

    def test_variable_use_with_terminator(self):
        given_ast = ast.Ast()

        result = given_ast._parser._variable_use_terminator.parseString("}")
        self.assertEqual(list(result)[0].location, 1) #'location' here is not a match location but the termination location, a bit confusing I admit

        result = given_ast._parser._standalone_variable_use.parseString("${sources}")
        self.assertEqual(list(result)[0].get_end_location(), 10)

        result = given_ast._parser._equivalent_variable_use_in_quotes.parseString('"${sources}"')
        self.assertEqual(list(result)[0].get_end_location(), 12)



if __name__ == '__main__':
    unittest.main()
