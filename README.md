# CMake Class Creator
A script that inserts a new c++ class in an existing CMake configuration.

A class is composed of a header file and a source file. That's two files! And sometimes they have to be added to different folders as well!
Adding classes and files can be tedious when using CMake. This project automates adding classes or single files to a cmake configuration.

## How to install
**To be added, but assume that CMake Class Creator can be invoked with 'cmcc' for the further readme content**

## Easy insertion using references
There are (too many) ways to specify source files for CMake. Usually the sources are list variables defined with the `set` keyword. Sometimes the sources are defined directly in `add_library` or `add_executable`. In modern CMake there is also a `target_sources` statement. 

So, you want to insert a new class, CMake Class Creator somehow must know how to insert it. The easiest way is to define a reference class. 

## Adding a class using a reference class
Suppose you want to insert a new class 'NewClass' next to 'OldClass':

`$>cmcc <cmakelists> NewClass -rc OldClass`

Executing this command will dump the updated cmakelists content to stdout, here you can check if the result is what you expect it to be.

When you approve of the changes, run the same command again with the `-i` option:

`$>cmcc <cmakelists> NewClass -rc OldClass -i`

Now the file contents of the cmakelists is updated. Your new class has been inserted!
