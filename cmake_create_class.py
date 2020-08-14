from CMakeClassCreator.parser import Parser

s = ("set(var content)"
"#set(actualvar actualcontent)")
parser = Parser()
result = parser._cmake_stmt.searchString(s)
print(result)
