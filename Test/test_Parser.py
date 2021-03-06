import unittest
import context
import pyparsing

from CMakeClassCreator.parser import Parser

class ParserTest(unittest.TestCase):
    def test_comment_stmt(self):
        givenParser = Parser()
        givenString = "#This is a comment, here's some garbage 34857039(*&)(**&%*&$%$#`~"

        result = givenParser._comment_stmt.parseString(givenString)
        self.assertEqual(list(result), ["#", "This is a comment, here's some garbage 34857039(*&)(**&%*&$%$#`~"])

    def test_normal_set_stmt(self):
        givenString = ("set(var\n" 
            + "${some_other_var}\n"
            + "cool_class.h\n"
            + "# The parser should skip these commented tokens: PARENT_SCOPE, ) \n"
            + '" and tokens between double quotes are not actual tokens: PARENT_SCOPE, )" \n'
            + '"${using_variables_should_work_between_quotes_though}" \n'
            + "cool_class.cpp\n"
            + ")")

        givenParser = Parser()

        result = givenParser._set_normal_variable_stmt.parseString(givenString)
        self.assertEqual(list(result), ["set", "(", "var",
             "${", "some_other_var", "}", "cool_class.h", 
                     '" and tokens between double quotes are not actual tokens: PARENT_SCOPE, )"', 
                     '"', "${", "using_variables_should_work_between_quotes_though", "}", '"',
                     "cool_class.cpp", ")"])

    def test_normal_set_stmt_handle_wrong_similar(self):
        givenParser = Parser()

        self.assertEqual(list(givenParser._set_normal_variable_stmt.searchString("set(x t")), [])
        self.assertEqual(list(givenParser._set_normal_variable_stmt.searchString("set x t)")), [])
        self.assertEqual(list(givenParser._set_normal_variable_stmt.searchString("set_ (x t)")), [])

    def test_normal_set_stmt_with_parent_scope(self):
        givenString = "set(var content PARENT_SCOPE)"
        givenParser = Parser()

        result = givenParser._set_normal_variable_stmt.parseString(givenString)
        self.assertEqual(list(result), ["set", "(", "var", "content", "PARENT_SCOPE", ")"])

    def test_set_env_variable_stmt(self):
        givenString = "set(ENV{ENV_VAR_NAME} value)"
        givenParser = Parser()

        result = givenParser._set_env_variable_stmt.parseString(givenString)
        self.assertEqual(list(result), ["set", "(", "ENV", "{", "ENV_VAR_NAME", "}", "value", ")"])
    
    def test_add_library_stmt(self):
        givenString = "add_library(TabsPlsLib main.cpp)"
        givenParser = Parser()

        result = givenParser._add_library_stmt.parseString(givenString)
        self.assertEqual(list(result), ["add_library", "(", "TabsPlsLib", "main.cpp", ")"])
    
    def test_add_library_stmt_with_type(self):
        givenString = "add_library(TabsPlsLib STATIC main.cpp)"
        givenParser = Parser()

        result = givenParser._add_library_stmt.parseString(givenString)
        self.assertEqual(list(result), ["add_library", "(", "TabsPlsLib", "STATIC", "main.cpp", ")"])

    def test_add_library_stmt_with_type(self):
        givenString = "add_library(TabsPlsLib STATIC main.cpp)"
        givenParser = Parser()

        result = givenParser._add_library_stmt.parseString(givenString)
        self.assertEqual(list(result), ["add_library", "(", "TabsPlsLib", "STATIC", "main.cpp", ")"])

    def test_add_library_stmt_with_exclude_from_all(self):
        givenString = "add_library(TabsPlsLib STATIC EXCLUDE_FROM_ALL main.cpp)"
        givenParser = Parser()

        result = givenParser._add_library_stmt.parseString(givenString)
        self.assertEqual(list(result), ["add_library", "(", "TabsPlsLib", "STATIC", "EXCLUDE_FROM_ALL", "main.cpp", ")"])

    def test_add_library_stmt_handle_wrong_similar(self):
        givenParser = Parser()

        self.assertEqual(list(givenParser._add_library_stmt.searchString("add_library(x t")), [])
        self.assertEqual(list(givenParser._add_library_stmt.searchString("add_library x t)")), [])
        self.assertEqual(list(givenParser._add_library_stmt.searchString("add_library_ (x t)")), [])

    def test_add_object_library_stmt(self):
        givenString = "add_library(TabsPlsLib OBJECT shared_component.hpp shared_component.cpp)"
        givenParser = Parser()

        result = givenParser._add_object_library_stmt.parseString(givenString)
        self.assertEqual(list(result), ["add_library", "(", "TabsPlsLib", "OBJECT", "shared_component.hpp", "shared_component.cpp", ")"])

    def test_add_object_library_stmt_handle_wrong_similar(self):
        givenParser = Parser()

        self.assertEqual(list(givenParser._add_object_library_stmt.searchString("add_library(x OBJECT t")), [])
        self.assertEqual(list(givenParser._add_object_library_stmt.searchString("add_library x OBJECT t)")), [])
        self.assertEqual(list(givenParser._add_object_library_stmt.searchString("add_library_ (x OBJECT t)")), [])

    def test_add_normal_executable_stmt(self):
        givenString = "add_executable(TabsPls ${TabsPls_Headers} ${TabsPls_Sources} main.cpp)"
        givenParser = Parser()

        result = givenParser._add_normal_executable_stmt.parseString(givenString)
        self.assertEqual(list(result), ["add_executable", "(", "TabsPls", "${", "TabsPls_Headers", "}", "${",  "TabsPls_Sources", "}", "main.cpp", ")"])

    def test_add_normal_executable_stmt_with_win32(self):
        givenString = "add_executable(TabsPls WIN32 ${TabsPls_Headers} ${TabsPls_Sources} main.cpp)"
        givenParser = Parser()

        result = givenParser._add_normal_executable_stmt.parseString(givenString)
        self.assertEqual(list(result), ["add_executable", "(", "TabsPls", "WIN32", "${", "TabsPls_Headers", "}", "${", "TabsPls_Sources", "}", "main.cpp", ")"])

    def test_add_normal_executable_stmt_with_macosx_bundle(self):
        givenString = "add_executable(TabsPls MACOSX_BUNDLE ${TabsPls_Headers} ${TabsPls_Sources} main.cpp)"
        givenParser = Parser()

        result = givenParser._add_normal_executable_stmt.parseString(givenString)
        self.assertEqual(list(result), ["add_executable", "(", "TabsPls", "MACOSX_BUNDLE", "${", "TabsPls_Headers", "}", "${", "TabsPls_Sources", "}", "main.cpp", ")"])
    
    def test_add_executable_stmt_handle_wrong_similar(self):
        givenParser = Parser()

        self.assertEqual(list(givenParser._add_normal_executable_stmt.searchString("add_executable(x t")), [])
        self.assertEqual(list(givenParser._add_normal_executable_stmt.searchString("add_executable x t)")), [])
        self.assertEqual(list(givenParser._add_normal_executable_stmt.searchString("add_executable_ (x t)")), [])

    def test_target_sources_stmt(self):
        givenParser = Parser()

        givenString = ("target_sources(TabsPls PRIVATE a.cpp b.cpp c.cpp PUBLIC pub_a.cpp pub_b.cpp pub_c.cpp\n"
                + "INTERFACE interface.hpp)")

        result = givenParser._target_sources_stmt.parseString(givenString)
        self.assertEqual(list(result), ["target_sources", "(", "TabsPls", "PRIVATE", "a.cpp", "b.cpp", "c.cpp", "PUBLIC", "pub_a.cpp", "pub_b.cpp", "pub_c.cpp", "INTERFACE", "interface.hpp", ")"])

    def test_target_sources_with_extra_whitespacing_stmt(self):
        givenParser = Parser()

        givenString = ("target_sources(TabsPls\n"
            + "PRIVATE\n"
            + "\ta.cpp b.cpp c.cpp\n"
            + "PUBLIC\n"
            + "\tpub_a.cpp pub_b.cpp pub_c.cpp\n"
            + "INTERFACE\n"
            + "\tinterface.hpp\n"
            + ")")

        result = givenParser._target_sources_stmt.parseString(givenString)
        self.assertEqual(list(result), ["target_sources", "(", "TabsPls", "PRIVATE", "a.cpp", "b.cpp", "c.cpp", "PUBLIC", "pub_a.cpp", "pub_b.cpp", "pub_c.cpp", "INTERFACE", "interface.hpp", ")"])


    def test_target_sources_stmt_handle_wrong_similar(self):
        givenParser = Parser()

        self.assertEqual(list(givenParser._target_sources_stmt.searchString("target_sources(TabsPls interface.hpp)")), [])
        self.assertEqual(list(givenParser._target_sources_stmt.searchString("target_sources(TabsPls PRIVATE interface.hpp")), [])
        self.assertEqual(list(givenParser._target_sources_stmt.searchString("target_sources_(TabsPls PRIVATE interface.hpp)")), [])

    def test_equivalent_variable_use_in_quotes(self):
        given_parser = Parser()

        given_parser._equivalent_variable_use_in_quotes.parseString('"${sources}"')
        self.assertRaises(pyparsing.exceptions.ParseException, given_parser._equivalent_variable_use_in_quotes.parseString, '"${sources} "')
        self.assertRaises(pyparsing.exceptions.ParseException, given_parser._equivalent_variable_use_in_quotes.parseString, '"${dir}/subdir"')

    def test_detect_variable_use_to_compose_list_item(self):
        given_parser = Parser()

        matched_variable_use_to_compose_list_item = [False]
        def match_variable_use_to_compose_list_item():
            matched_variable_use_to_compose_list_item[0] = True
        matched_variable_use = [False]
        def match_variable_use():
            matched_variable_use[0] = True

        given_parser._variable_use_to_compose_list_item.setParseAction(match_variable_use_to_compose_list_item)
        given_parser._any_standalone_variable_use.setParseAction(match_variable_use)

        given_parser._variable_use_in_string_list.parseString("${dir}/subdir/file.cpp")

        self.assertTrue(matched_variable_use_to_compose_list_item[0])
        self.assertFalse(matched_variable_use[0])

        matched_variable_use_to_compose_list_item[0], matched_variable_use[0] = False, False

        given_parser._variable_use_in_string_list.parseString("${dir}")

        self.assertFalse(matched_variable_use_to_compose_list_item[0])
        self.assertTrue(matched_variable_use[0])

    def test_cmake_stmt_ignores_comment(self):
        given_parser = Parser()
        given_source = "#this is a nice statement\nset(varname file1 file2)"
        
        results = given_parser._cmake_stmt.searchString(given_source)
        
        self.assertEqual(len(results), 1)
        self.assertEqual(list(results[0]), ["set", "(", "varname", "file1", "file2", ")"])

if __name__ == '__main__':
    unittest.main()
