import unittest
import context


from CMakeClassCreator.parser import Parser

class ParserTest(unittest.TestCase):
    def test_comment_stmt(self):
        givenParser = Parser()
        givenString = "#This is a comment, here's some garbage 34857039(*&)(**&%*&$%$#`~"

        result = givenParser._comment_stmt.parseString(givenString)
        self.assertEqual(list(result), ["#", "This is a comment, here's some garbage 34857039(*&)(**&%*&$%$#`~"])

    def test_normal_set_stmt(self):
        givenStringVarContent = ("\n$\{some_other_var\}\n"
            + "cool_class.h\n"
            + "# The parser should skip these commented tokens: PARENT_SCOPE, ) \n"
            + '" as well as thing between double quotes: PARENT_SCOPE, )" \n'
            + "cool_class.cpp")

        givenString = ("set(var"
            + givenStringVarContent
            + "\n)")

        givenParser = Parser()

        result = givenParser._set_normal_variable_stmt.parseString(givenString)
        self.assertEqual(list(result), ["set", "(", "var", givenStringVarContent, ")"])

    def test_normal_set_stmt_handle_wrong_similar(self):
        givenParser = Parser()

        self.assertEqual(list(givenParser._set_normal_variable_stmt.searchString("set(x t")), [])
        self.assertEqual(list(givenParser._set_normal_variable_stmt.searchString("set x t)")), [])
        self.assertEqual(list(givenParser._set_normal_variable_stmt.searchString("set_ (x t)")), [])

    def test_normal_set_stmt_with_parent_scope(self):
        givenString = "set(var content PARENT_SCOPE)"
        givenParser = Parser()

        result = givenParser._set_normal_variable_stmt.parseString(givenString)
        self.assertEqual(list(result), ["set", "(", "var", " content", "PARENT_SCOPE", ")"])

    def test_set_env_variable_stmt(self):
        givenString = "set(ENV\{ENV_VAR_NAME\} value)"
        givenParser = Parser()

        result = givenParser._set_normal_variable_stmt.parseString(givenString)
        self.assertEqual(list(result), ["set", "(", "ENV", "\{ENV_VAR_NAME\} value", ")"])
    
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
        self.assertEqual(list(result), ["add_library", "(", "TabsPlsLib", "OBJECT", "shared_component.hpp shared_component.cpp", ")"])

    def test_add_object_library_stmt_handle_wrong_similar(self):
        givenParser = Parser()

        self.assertEqual(list(givenParser._add_object_library_stmt.searchString("add_library(x OBJECT t")), [])
        self.assertEqual(list(givenParser._add_object_library_stmt.searchString("add_library x OBJECT t)")), [])
        self.assertEqual(list(givenParser._add_object_library_stmt.searchString("add_library_ (x OBJECT t)")), [])

if __name__ == '__main__':
     unittest.main()