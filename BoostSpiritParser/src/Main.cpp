#include <iostream>

#include <BoostSpiritCMakeParser/parser.hpp>

namespace 
{
    struct list_item_visitor: boost::static_visitor<>
    {
        void operator()(const Ast::ListItemStringWithLocation& list_item_string) const
        {
            std::cout << list_item_string.list_item_string << std::endl;
        }

        void operator()(const Ast::VariableUseWithLocation& variable_use) const
        {
            std::cout << "${" << variable_use.var_name << "}" << std::endl;
        }
    };
}

int main(int argc, const char** argv)
{
    {
        const auto parser = CMakeParser::CreateSetNormalVariableParser();
        const std::string source = "set(varname\n \
            \t${sources}\n \
            \t${samen}gesteld \n\
            #WHAT ABOUT COMMENTS?\n \
            \tfile.cpp file2.cpp \"file met spaties.h\" \n)";
        const auto result = parser->parse(source);

        if(result)
        {
            std::cout << "Parsing success!" << std::endl;
            std::cout << "variable name: " << result->var_name << std::endl;
            std::cout << "parent scope?: " << (result->parent_scope ? "true" : "false") << std::endl;
            for(const auto& item: result->cmake_string_list)
                boost::apply_visitor(list_item_visitor(), item);
        }
        else
            std::cout << "Failed parsing set." << std::endl;
    }
    {
        const auto parser = CMakeParser::CreateCMakeStringListParser();
        const std::string source = "${samen}gesteld";
        const auto result = parser->parse(source);

        if(result)
        {
            std::cout << "Parsing success!" << std::endl;
            for(const auto& item: *result)
                boost::apply_visitor(list_item_visitor(), item);
        }
        else
            std::cout << "Failed parsing." << std::endl;
    }
    return 0;
}