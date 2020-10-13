
import unittest

import context

from CMakeClassCreator import source_inserter, ast

class TestSourceInserter(unittest.TestCase):
    def test_get_position_after_last_list_item(self):
        #This is based entirely on the last item's location
        given_cmake_string_list = ast.CMakeStringList([ast.ListItemStringWithLocation("item1.cpp", -1), ast.VariableUseWithLocation("Sources", -1), ast.ListItemStringWithLocation("item2", 14)])
        self.assertEqual(source_inserter._get_position_after_last_list_item(given_cmake_string_list), 20)
        

    def test_insert_directly_in_executable(self):
        given_ast = ast.Ast()
        given_source = "add_executable(TabsPls Main.cpp)"
        given_cmake_ast = given_ast.parse(given_source)
        insert_action = source_inserter.insert_source_item_directly_in_target(given_cmake_ast, "file.cpp", "TabsPls")
        self.assertEqual(insert_action.position, 32)
        self.assertEqual(insert_action.content, " file.cpp")
        self.assertEqual(insert_action.do(given_source), "add_executable(TabsPls Main.cpp file.cpp)")

    def test_insert_directly_in_non_existing_executable(self):
        given_ast = ast.Ast()
        given_cmake_ast = given_ast.parse("add_executable(IWantTabs Main.cpp)")
        self.assertRaises(source_inserter.SourceInserterException, source_inserter.insert_source_item_directly_in_target, given_cmake_ast, "file.cpp", "TabsPls")

    def test_insert_in_variable_from_target(self):
        given_ast = ast.Ast()
        given_source = ("set(TabsPls_Sources Main.cpp)\n"
            + "add_executable(TabsPls ${TabsPls_Sources})")
        given_cmake_ast = [match[0] for match in list(given_ast.scan_all(given_source))]

        insert_action = source_inserter.insert_source_item_in_variable_from_target(given_cmake_ast, "file.cpp", "TabsPls", "TabsPls_Sources")
        self.assertEqual(insert_action.position, 29)
        self.assertEqual(insert_action.content, " file.cpp")
        self.assertEqual(insert_action.do(given_source), "set(TabsPls_Sources Main.cpp file.cpp)\nadd_executable(TabsPls ${TabsPls_Sources})")

    def test_insert_in_non_existing_variable_from_target(self):
        given_ast = ast.Ast()
        given_cmake_ast = given_ast.parse(("set(TabsPls_Sources Main.cpp)\n"
            + "add_executable(TabsPls OtherMain.cpp")) 

        self.assertRaises(source_inserter.SourceInserterException, source_inserter.insert_source_item_in_variable_from_target, given_cmake_ast, "file.cpp", "TabsPls", "TabsPls_Sources")

    def test_insert_in_variable_from_non_existing_target(self):
        given_ast = ast.Ast()
        given_cmake_ast = given_ast.parse(("set(IWantTabs_Sources Main.cpp)\n"
            + "add_executable(IWantTabs ${IWantTabs_Sources}")) 

        self.assertRaises(source_inserter.SourceInserterException, source_inserter.insert_source_item_in_variable_from_target, given_cmake_ast, "file.cpp", "TabsPls", "IWantTabs_Sources")
        
    def test_insert_in_variable(self):
        given_ast = ast.Ast()
        given_source = ("set(TabsPls_Sources Main.cpp)\n"
            + "add_executable(TabsPls ${TabsPls_Sources})")
        given_cmake_ast = given_ast.parse(given_source)

        insert_action = source_inserter.insert_source_item_in_variable(given_cmake_ast, "file.cpp", "TabsPls_Sources")
        self.assertEqual(insert_action.position, 29)
        self.assertEqual(insert_action.content, " file.cpp")
        self.assertEqual(insert_action.do(given_source), ("set(TabsPls_Sources Main.cpp file.cpp)\n"
            + "add_executable(TabsPls ${TabsPls_Sources})"))


    def test_insert_in_non_existing_variable(self):
        given_ast = ast.Ast()
        given_cmake_ast = given_ast.parse(("set(IWantTabs_Sources Main.cpp)\n"
            + "add_executable(TabsPls OtherMain.cpp")) 

        self.assertRaises(source_inserter.SourceInserterException, source_inserter.insert_source_item_in_variable, given_cmake_ast, "file.cpp", "TabsPls_Sources")

    def test_insert_next_to_other_source_directly_at_target(self):
        given_ast = ast.Ast()
        given_source = "add_executable(TabsPls Main.cpp)"
        given_cmake_ast = given_ast.parse(given_source)

        insert_action = source_inserter.insert_source_item_next_to_other_source(given_cmake_ast, "file.cpp", "Main.cpp")
        self.assertEqual(insert_action.position, 32)
        self.assertEqual(insert_action.content, " file.cpp")
        self.assertEqual(insert_action.do(given_source), "add_executable(TabsPls Main.cpp file.cpp)")

    def test_insert_next_to_other_source_in_variable_set(self):
        given_ast = ast.Ast()
        given_source = ("set(TabsPls_Sources Main.cpp)\n"
            + "add_executable(TabsPls ${TabsPls_Sources})")
        given_cmake_ast = given_ast.parse(given_source)

        insert_action = source_inserter.insert_source_item_next_to_other_source(given_cmake_ast, "file.cpp", "Main.cpp")
        self.assertEqual(insert_action.position, 29)
        self.assertEqual(insert_action.content, " file.cpp")
        self.assertEqual(insert_action.do(given_source), "set(TabsPls_Sources Main.cpp file.cpp)\nadd_executable(TabsPls ${TabsPls_Sources})")
    
    def test_insert_next_to_other_source_in_target_sources_stmt(self):
        given_ast = ast.Ast()
        given_source = ("set(TabsPls_Sources Main.cpp)\n"
            + "add_executable(TabsPls ${TabsPls_Sources})\n"
            + "target_sources(TabsPls PRIVATE file1.cpp)")
        given_cmake_ast = [match[0] for match in list(given_ast.scan_all(given_source))]

        insert_action = source_inserter.insert_source_item_next_to_other_source(given_cmake_ast, "file2.cpp", "file1.cpp")
        self.assertEqual(insert_action.position, 114)
        self.assertEqual(insert_action.content, " file2.cpp")
        self.assertEqual(insert_action.do(given_source), \
            ("set(TabsPls_Sources Main.cpp)\n"
            + "add_executable(TabsPls ${TabsPls_Sources})\n"
            + "target_sources(TabsPls PRIVATE file1.cpp file2.cpp)"))

    def test_insert_next_to_non_existing_other_source(self):
        given_ast = ast.Ast()
        given_cmake_ast = given_ast.parse("add_executable(TabsPls Main.cpp)") 

        self.assertRaises(source_inserter.SourceInserterException, source_inserter.insert_source_item_next_to_other_source, given_cmake_ast, "file.cpp", "other_file.cpp")


if __name__ == '__main__':
    unittest.main()
