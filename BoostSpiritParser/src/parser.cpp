
#include <BoostSpiritCMakeParser/parser.hpp>

#include <vector>

#include <boost/bind/bind.hpp>

#include <boost/spirit/include/qi.hpp>
#include <boost/spirit/include/phoenix_core.hpp>
#include <boost/spirit/include/phoenix_operator.hpp>
#include <boost/spirit/include/phoenix_object.hpp>
#include <boost/fusion/adapted/struct/adapt_struct.hpp>
#include <boost/fusion/include/adapt_struct.hpp>

using namespace boost::spirit;
using namespace boost::spirit::ascii;

namespace Ast
{

struct VariableUseWithLocation
{
    std::string var_name;
    unsigned location;
};

struct ListItemString
{
    std::string list_item_string;
};

struct ListItemStringWithLocation : ListItemString
{
    unsigned location;
};

struct CMakeStringList
{
    std::vector<VariableUseWithLocation> items;
};

struct SetNormalVariable
{
    std::string var_name;
    CMakeStringList cmake_string_list;
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

struct TargetSources
{
    std::string target_name;
    CMakeStringList cmake_string_list;
};

struct CMakeStatement
{
    boost::variant<
        SetNormalVariable, 
        AddExecutable,
        AddLibrary,
        TargetSources> statement;
};

}

BOOST_FUSION_ADAPT_STRUCT(
    Ast::VariableUseWithLocation,
    (auto, var_name),
    (auto, location)
)

BOOST_FUSION_ADAPT_STRUCT(
    Ast::ListItemStringWithLocation,
    (auto, list_item_string),
    (auto, location)
)

BOOST_FUSION_ADAPT_STRUCT(
    Ast::CMakeStringList,
    (auto, items)
)

BOOST_FUSION_ADAPT_STRUCT(
    Ast::SetNormalVariable,
    (auto, var_name),
    (auto, cmake_string_list)
)

BOOST_FUSION_ADAPT_STRUCT(
    Ast::AddLibrary,
    (auto, library_name),
    (auto, cmake_string_list)
)

BOOST_FUSION_ADAPT_STRUCT(
    Ast::AddExecutable,
    (auto, executable_name),
    (auto, cmake_string_list)
)

BOOST_FUSION_ADAPT_STRUCT(
    Ast::TargetSources,
    (auto, target_name),
    (auto, cmake_string_list)
)

BOOST_FUSION_ADAPT_STRUCT(
    Ast::CMakeStatement,
    (auto, statement)
)

using f_context = boost::spirit::context<
        boost::fusion::cons<Ast::VariableUseWithLocation&, boost::fusion::nil>, 
        boost::fusion::vector0<>>;
	
template<typename Iterator>
static void set_position_on_success(boost::fusion::vector<
		Iterator&, //first
		Iterator const&, //last
		Iterator const&> args, //i
	f_context& context,
    Iterator inputBegin)
{
    const unsigned location_index = boost::fusion::at_c<0>(args) - inputBegin;
    std::cout << "succesfully parsed variable use at location " << location_index << std::endl;
    boost::fusion::at_c<0>(context.attributes).location = location_index;
}

namespace Ast
{

template<typename Iterator>
struct cmake_string_list_grammar:
    qi::grammar<Iterator, CMakeStringList(), ascii::space_type>
{
    cmake_string_list_grammar(Iterator inputBegin):
        cmake_string_list_grammar::base_type(cmake_string_list)
    {
        using qi::lit;
        using ascii::char_;
        using qi::int_;
        using qi::eps;
        using qi::on_success;
        using qi::on_error;

        variable_use %= lit("${") >> +(char_ - "}") >> "}";

	    location %= eps[_val = 0U]; //This will be filled later with on_success
        variable_use_with_location %= variable_use >> location;

        variable_use.name("variable_use");
        variable_use_with_location.name("variable_use_with_location");

        cmake_string_list_items %= +(variable_use_with_location);
        cmake_string_list %= cmake_string_list_items;

	    on_success(variable_use_with_location, 
            boost::bind(&set_position_on_success<Iterator>, boost::placeholders::_1, boost::placeholders::_2, inputBegin));
    }
 
    qi::rule<Iterator, std::vector<VariableUseWithLocation>(), ascii::space_type> cmake_string_list_items;
    qi::rule<Iterator, CMakeStringList(), ascii::space_type> cmake_string_list;
    qi::rule<Iterator, std::string(), ascii::space_type> variable_use;
    qi::rule<Iterator, unsigned(), ascii::space_type> location;
    qi::rule<Iterator, VariableUseWithLocation(), ascii::space_type> variable_use_with_location;
};

}
namespace
{
template<typename Iterator>
struct cmake_statement_grammar:
    qi::grammar<Iterator, Ast::CMakeStatement(), ascii::space_type>
{
    cmake_statement_grammar():
        cmake_statement_grammar::base_type(cmake_statement)
    {
        using qi::lit;
        using qi::_val;
        using qi::char_;

        // set_normal_variable = lit("set") >> "(" >> (+char_)[_1] >> +((char_[_1] - ")")) >> ")";
        // cmake_statement %= variable_use | set_normal_variable;
    }

    qi::rule<Iterator, Ast::CMakeStatement(), ascii::space_type> cmake_statement;
    qi::rule<Iterator, Ast::SetNormalVariable(), ascii::space_type> set_normal_variable;
};
}

template <typename Iterator>
static bool parse_cmake(Iterator first, Iterator last)
{
    using qi::double_;
    using qi::phrase_parse;
    using ascii::space;

    Ast::cmake_string_list_grammar<Iterator> grammar(first);
    Ast::CMakeStringList ast;

    bool r = phrase_parse(
        first,                       
        last,                           
        grammar,
        space,
        ast  
    );
    if (first != last) // fail if we did not get a full match
        return false;
    return r;
}

namespace CMakeParser
{
    void parse()
    {
        std::string source = "   ${sources}";
        parse_cmake(source.begin(), source.end());
    }
}
