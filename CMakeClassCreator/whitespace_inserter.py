""" Functionality that improves source inserting by copying the existing whitespace when adding source """

from abc import ABC, abstractmethod

class WhitespaceInsertException(Exception):
    pass

class LessThanTwoItemsException(WhitespaceInsertException):
    """ To deduce what whitespace is between two elements, there must be at least two elements """
    pass

def enhance_insert_action_with_whitespace_used_in_cmake_string_list(full_cmake_source, insert_action, cmake_string_list_ast):
    try:
        insert_action.whitespace_prefix = get_content_between_second_to_last_and_last_item(full_cmake_source, cmake_string_list_ast)
    except WhitespaceInsertException:
        pass

def get_content_between_second_to_last_and_last_item(full_cmake_source, cmake_string_list_ast):
    if len(cmake_string_list_ast.items)<2:
        raise LessThanTwoItemsException()

    begin_index, end_index = cmake_string_list_ast.items[-2].get_end_location(), cmake_string_list_ast.items[-1].location
    return full_cmake_source[begin_index:end_index]

