#!/usr/bin/env python

import os
from setuptools import setup, find_packages

install_requires = []
with open("requirements.txt", 'r') as requirements_file:
      install_requires = requirements_file.read().splitlines()

long_description = ""
with open("README.md", 'r') as long_description_file:
      long_description = long_description_file.read()

setup(name='CMake-Class-Creator',
      version='0.1.6',
      description='A script that inserts a new c++ class in an existing CMake configuration.',
      author='Frank Goyens',
      url='https://github.com/FrankGoyens/CMakeClassCreator',
      packages=find_packages(),
      py_modules=["cmake_create_class"],
      install_requires=install_requires,
      long_description=long_description,
      long_description_content_type="text/markdown",
      entry_points={"console_scripts": {"cmake_create_class=cmake_create_class:main"}}
     )
