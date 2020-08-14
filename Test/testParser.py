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

    def test_normal_set_stmt_handle_garbage(self):
        givenGarbageString = "432534^^*&^%*&2341029357*(&)())(_)(*&(*)(_!"

        givenParser = Parser()
        result = givenParser._set_normal_variable_stmt.searchString(givenGarbageString)
        self.assertEqual(list(result), [])

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


if __name__ == '__main__':
     unittest.main()