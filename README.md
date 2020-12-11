# CMake Class Creator
A script that inserts a new c++ class in an existing CMake configuration.

A class is composed of a header file and a source file. That's two files! And sometimes they have to be added to different folders as well!
Adding classes and files can be tedious when using CMake. This project automates adding classes or single files to a cmake configuration.

## How to install
The recommended way is to use pip: `pip install CMake-Class-Creator`

**Please note** that this module depends on a release candidate version op pyparsing, 3.0.0b1. So it is also recommended to install this in a virtual environment.

Optionally you can alias this command: `alias cmcc=cmake_create_class`


## Easy insertion using references
There are (too many) ways to specify source files for CMake. Usually the sources are list variables defined with the `set` keyword. Sometimes the sources are defined directly in `add_library` or `add_executable`. In modern CMake there is also a `target_sources` statement. 

So, you want to insert a new class, CMake Class Creator somehow must know how to insert it. The easiest way is to define a reference class. 

## Adding a class using a reference class
Suppose you want to insert a new class 'NewClass' next to 'ExistingClass':

`$>cmcc <cmakelists> NewClass -rc ExistingClass`

Executing this command will dump the updated cmakelists content to stdout, here you can check if the result is what you expect it to be.

When you approve of the changes, run the same command again with the `-i` option:

`$>cmcc <cmakelists> NewClass -rc ExistingClass -i`

Now the file contents of the cmakelists are updated. Your new class has been inserted!

## Adding a single file using a reference file
It is also possible to add a single file using the `-s` option.

When you want to make a header only class for instance:

`$>cmcc <cmakelists> New.hpp -s -rc Existing.hpp`

**Note** that since we're dealing with single files, specifying the complete filename including the extension is required. But it is **not** required to specify the full path. In this example, `Existing.hpp` may be defined as `<path>/Existing.hpp` or just `Existing.hpp`. In case there is a path prefix, this will also be used for `New.hpp`.

When you approve of the changes, run the same command again with the `-i` option:

`$>cmcc <cmakelists> New.hpp -s -rc Existing.hpp -i`

Now the file contents of the cmakelists are updated. Your new file has been inserted!
