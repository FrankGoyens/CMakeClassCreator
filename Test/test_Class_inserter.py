import unittest

import context

from CMakeClassCreator import class_inserter, ast

class TestClassInserter(unittest.TestCase):
    def test_insert_class_next_to_other_class(self):
        given_source = ("project(TabsPls)\n\n"
            + "set(TabsPls_Headers File.hpp\n"
            + "\tDirectory.hpp\n"
            + ")\n\n"
            + "set(TabsPls_Sources File.cpp\n"
            + "\tDirectory.cpp\n"
            + "\tMain.cpp\n"
            + ")\n\n"
            + "add_executable(TabsPls ${TabsPls_Headers} ${TabsPls_Sources})\n"
            + "target_sources(TabsPls PRIVATE windows_util.h windows_util.c)")
        given_ast = [match[0] for match in list(ast.Ast().scan_all(given_source))]

        header_insert_action, impl_insert_action = class_inserter.insert_class_next_to_other_class(given_ast, "Symlink", "File")

        self.assertEqual(header_insert_action.position, 62)
        self.assertEqual(header_insert_action.do(given_source), ("project(TabsPls)\n\n"
            + "set(TabsPls_Headers File.hpp\n"
            + "\tDirectory.hpp Symlink.hpp\n"
            + ")\n\n"
            + "set(TabsPls_Sources File.cpp\n"
            + "\tDirectory.cpp\n"
            + "\tMain.cpp\n"
            + ")\n\n"
            + "add_executable(TabsPls ${TabsPls_Headers} ${TabsPls_Sources})\n"
            + "target_sources(TabsPls PRIVATE windows_util.h windows_util.c)"))

        self.assertEqual(impl_insert_action.position, 119)
        self.assertEqual(impl_insert_action.do(given_source), ("project(TabsPls)\n\n"
            + "set(TabsPls_Headers File.hpp\n"
            + "\tDirectory.hpp\n"
            + ")\n\n"
            + "set(TabsPls_Sources File.cpp\n"
            + "\tDirectory.cpp\n"
            + "\tMain.cpp Symlink.cpp\n"
            + ")\n\n"
            + "add_executable(TabsPls ${TabsPls_Headers} ${TabsPls_Sources})\n"
            + "target_sources(TabsPls PRIVATE windows_util.h windows_util.c)"))

if __name__ == "__main__":
    unittest.main()