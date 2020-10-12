#pragma once

#include <string>
#include <memory>
#include <vector>

#include <boost/variant.hpp>
#include <boost/optional.hpp>

namespace Ast
{

struct VariableUseWithLocation
{
    std::string var_name;
    unsigned location;
};

struct ListItemStringWithLocation
{
    std::string list_item_string;
    unsigned location;
};

using CMakeStringList =  std::vector<boost::variant<VariableUseWithLocation, ListItemStringWithLocation>>;

struct SetNormalVariable
{
    std::string var_name;
    CMakeStringList cmake_string_list;
    bool parent_scope;
};

struct SetEnvVariable
{
    std::string var_name;
    boost::optional<std::string> value;
};

struct AddLibrary
{
    std::string library_name;
    CMakeStringList cmake_string_list;
};

struct AddExecutable
{
    std::string executable_name;
    CMakeStringList cmake_string_list;
};

struct ScopedList
{
    std::string scope_name;
    CMakeStringList cmake_string_list;
};

struct TargetSources
{
    std::string target_name;
    std::vector<ScopedList> sources_per_scope;  
};

using CMakeStatement = boost::variant<
    SetNormalVariable, 
    AddExecutable,
    AddLibrary,
    TargetSources>;

}

namespace CMakeParser
{
    template<typename Ast>
    struct Parser
    {
        virtual ~Parser() = default;
        virtual boost::optional<Ast> parse(const std::string&) const = 0;
    };

    std::unique_ptr<Parser<Ast::CMakeStringList>> CreateCMakeStringListParser();
    std::unique_ptr<Parser<Ast::SetNormalVariable>> CreateSetNormalVariableParser();
}
