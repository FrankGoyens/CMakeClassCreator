from pyparsing import Word, Literal, CaselessLiteral, Optional, alphas, alphanums, restOfLine, SkipTo, Suppress, dblQuotedString

class Parser(object):
    def __init__(self):
        self._comment_keyword = Literal("#")
        self._comment_stmt = self._comment_keyword + restOfLine 

        self._variable_name = Word(alphas+"_", alphanums+"_")
        self._variable_use = "${" + self._variable_name + "}"

        self._set_keyword = CaselessLiteral("set")
        self._parent_scope_keyword = Literal("PARENT_SCOPE")

        #https://cmake.org/cmake/help/latest/command/set.html#set-normal-variable 
        self._set_normal_variable_stmt = self._set_keyword + "(" \
            + self._variable_name \
                + SkipTo(self._parent_scope_keyword + ")" | ")", include=True, ignore=self._comment_stmt | dblQuotedString)

        self._content_until_endparen = SkipTo(")", include=True, ignore=self._comment_stmt | dblQuotedString)

        #https://cmake.org/cmake/help/latest/command/set.html#set-environment-variable
        #We need to define this one to be able to ignore it
        self._set_env_variable_stmt = self._set_keyword + "(" + Literal("ENV") \
            + self._content_until_endparen

        self._add_library_keyword = CaselessLiteral("add_library")
        self._normal_library_types = Literal("STATIC") | Literal("SHARED") | Literal("MODULE")
        self._library_name = self._variable_name

        #https://cmake.org/cmake/help/latest/command/add_library.html#normal-libraries
        self._add_library_stmt = self._add_library_keyword + "(" \
            + self._library_name + Optional(self._normal_library_types) \
                + Optional(Literal("EXCLUDE_FROM_ALL")) \
                    + self._content_until_endparen

        self._object_library_type = Literal("OBJECT")

        #https://cmake.org/cmake/help/latest/command/add_library.html#object-libraries
        self._add_object_library_stmt = self._add_library_keyword + "(" \
            + self._library_name + self._object_library_type \
                + self._content_until_endparen

        #Limited only to the things we actually need of course
        self._cmake_stmt = self._set_normal_variable_stmt
        self._cmake_stmt.ignore(self._comment_stmt)
