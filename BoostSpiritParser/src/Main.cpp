#include <iostream>

#include <BoostSpiritCMakeParser/parser.hpp>

int main(int argc, const char** argv)
{
    const auto parser = CMakeParser::CreateCMakeStringListParser();
    const std::string source = "File.cpp Main.cpp";
    const bool result = parser->parse(source);

    if(result)
        std::cout << "Parsing success!" << std::endl;
    else
        std::cout << "Failed parsing." << std::endl;
    return 0;
}