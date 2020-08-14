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

        #https://cmake.org/cmake/help/latest/command/set.html#set-environment-variable
        #We need to define this one to be able to ignore it
        self._set_env_variable_stmt = self._set_keyword + "(" + Literal("ENV") + ")"

        #Limited only to the things we actually need of course
        self._cmake_stmt = self._set_normal_variable_stmt
        self._cmake_stmt.ignore(self._comment_stmt)
