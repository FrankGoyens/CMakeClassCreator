#include <iostream>

#include <BoostSpiritCMakeParser/parser.hpp>

int main(int argc, const char** argv)
{
    const std::string source = "#leuke comment\n${var}";
    CMakeParser::parse(source);
    return 0;
}