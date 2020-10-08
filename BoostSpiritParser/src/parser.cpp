
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
    Ast::SetNormalVariable,
    (auto, var_name),
    (auto, cmake_string_list)
)

BOOST_FUSION_ADAPT_STRUCT(
    Ast::SetEnvVariable,
    (auto, var_name),
    (auto, value)
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
    Ast::ScopedList,
    (auto, scope_name),
    (auto, cmake_string_list)
)

BOOST_FUSION_ADAPT_STRUCT(
    Ast::TargetSources,
    (auto, target_name),
    (auto, sources_per_scope)
)

BOOST_FUSION_ADAPT_STRUCT(
    Ast::CMakeStatement,
    (auto, statement)
)

template<typename Attribute>
using f_context = boost::spirit::context<
        boost::fusion::cons<Attribute&, boost::fusion::nil>, 
        boost::fusion::vector0<>>;
	
template<typename Iterator, typename Attribute>
static void set_match_location_on_success(boost::fusion::vector<
		Iterator&, //first
		Iterator const&, //last
		Iterator const&> args, //i
	f_context<Attribute>& context,
    Iterator inputBegin)
{
    const unsigned location_index = boost::fusion::at_c<0>(args) - inputBegin;
    std::cout << "succesfully parsed cmake list item at location " << location_index << std::endl;
    boost::fusion::at_c<0>(context.attributes).location = location_index;
}

namespace Ast
{

template<typename Iterator>
struct cmake_grammar:
    qi::grammar<Iterator, CMakeStatement(), ascii::space_type>
{
    cmake_grammar(Iterator inputBegin):
        cmake_grammar::base_type(cmake_statement)
    {
        using qi::lit;
        using ascii::char_;
        using qi::int_;
        using qi::eps;
        using qi::lexeme;
        using qi::skip;
        using qi::on_success;
        using qi::on_error;

        dblQuotedString %= lexeme["\"" >> +(char_ - "\"") >> "\""];
        comment %= lexeme["#" >> +(char_ - "\n") >> "\n"];

        variable_use %= lit("${") >> +(char_ - "}") >> "}";
        equivalent_variable_use %= variable_use | ("\"" >> variable_use >> "\"");

        location %= eps[_val = 0U]; //This will be filled later with on_success

        //this is not used to parse into anything meaningful, so they are combined into a single token. This makes this easily managed
        word_until_rpar %= +(char_ - ")");
        variable_use_to_compose_list_item %= (dblQuotedString[_val = _1] >> equivalent_variable_use[_val += _1])
            | (equivalent_variable_use[_val = _1] >> dblQuotedString[_val += _1])
            | (word_until_rpar[_val = _1] >> equivalent_variable_use[_val += _1])
            | (equivalent_variable_use[_val = _1] >> word_until_rpar[_val += _1]);

        variable_use_with_location %= equivalent_variable_use >> location;

        list_item_string %= dblQuotedString 
            | word_until_rpar
            | skip[/*not supported/needed yet*/variable_use_to_compose_list_item]
            | skip[comment];
        list_item_string_with_location %= list_item_string >> location;

        scope_specifier_keywords = lit("PRIVATE") | lit("PUBLIC") | lit("INTERFACE");
        any_list_item %= !scope_specifier_keywords >> 
            (variable_use_with_location 
            | list_item_string_with_location);

        cmake_string_list %= +(any_list_item);

	    on_success(variable_use_with_location, 
            boost::bind(&set_match_location_on_success<Iterator, VariableUseWithLocation>, boost::placeholders::_1, boost::placeholders::_2, inputBegin));
        on_success(list_item_string_with_location, 
            boost::bind(&set_match_location_on_success<Iterator, ListItemStringWithLocation>, boost::placeholders::_1, boost::placeholders::_2, inputBegin));

        const auto set_keyword = lit("set") | lit("SET");

        set_normal_variable %= set_keyword >> "(" >> +char_ >> cmake_string_list >> -lit("PARENT_SCOPE") >> ")";
        set_env_variable %= set_keyword >> "(" >> "ENV" >> "{" >> +char_ >> "}" >> -(+char_ - ")") >> ")";

        const auto add_library_keyword = lit("add_library") | lit("ADD_LIBRARY");
        const auto normal_library_types = lit("STATIC") | lit("SHARED") | lit("MODULE");
        const auto exclude_from_all_flag = lit("EXCLUDE_FROM_ALL");

        add_library %= add_library_keyword >> "(" >> +char_ >> -normal_library_types >> -exclude_from_all_flag >> cmake_string_list >> ")";

        const auto object_library_type_keyword = lit("OBJECT");

        add_object_library %= add_library_keyword >> "(" >> +char_ >> object_library_type_keyword >> cmake_string_list >> ")";

        const auto add_executable_keyword = lit("add_executable") | lit("ADD_EXECUTABLE");
        const auto add_executable_win32_keyword = lit("WIN32");
        const auto add_executable_macosx_bundle_keyword = lit("MACOSX_BUNDLE");

        add_executable %= add_executable_keyword >> "(" >> +char_ >> -add_executable_win32_keyword >> -add_executable_macosx_bundle_keyword >> -exclude_from_all_flag >> cmake_string_list >> ")";

        const auto target_sources_keyword = lit("target_sources") | lit("TARGET_SOURCES");

        scoped_list %= scope_specifier_keywords >> cmake_string_list;

        target_sources %= target_sources_keyword >> "(" >> (+char_ - scope_specifier_keywords) >> +scoped_list >> ")";

        cmake_statement %= set_normal_variable | add_executable | add_library | add_object_library | target_sources;
    }
 
    //basics
    qi::rule<Iterator, std::string(), ascii::space_type> comment;
    qi::rule<Iterator, std::string(), ascii::space_type> dblQuotedString;
    qi::rule<Iterator, std::string(), ascii::space_type> word_until_rpar;
    qi::rule<Iterator, unsigned(), ascii::space_type> location;

    //list item string (a list item that is just a string)
    qi::rule<Iterator, std::string(), ascii::space_type> list_item_string;
    qi::rule<Iterator, ListItemStringWithLocation(), ascii::space_type> list_item_string_with_location;

    //variable use
    qi::rule<Iterator, std::string(), ascii::space_type> variable_use;
    qi::rule<Iterator, std::string(), ascii::space_type> equivalent_variable_use;
    qi::rule<Iterator, std::string(), ascii::space_type> variable_use_to_compose_list_item;

    qi::rule<Iterator, VariableUseWithLocation(), ascii::space_type> variable_use_with_location;

    //list item
    qi::rule<Iterator, std::string(), ascii::space_type> scope_specifier_keywords;
    qi::rule<Iterator, boost::variant<VariableUseWithLocation, ListItemStringWithLocation>(), ascii::space_type> any_list_item;

    //cmake string list
    qi::rule<Iterator, CMakeStringList(), ascii::space_type> cmake_string_list;

    //https://cmake.org/cmake/help/latest/command/set.html#set-normal-variable 
    qi::rule<Iterator, SetNormalVariable(), ascii::space_type> set_normal_variable;

    //https://cmake.org/cmake/help/latest/command/set.html#set-environment-variable
    qi::rule<Iterator, SetEnvVariable(), ascii::space_type> set_env_variable;

    //https://cmake.org/cmake/help/latest/command/add_library.html#normal-libraries
    qi::rule<Iterator, AddLibrary(), ascii::space_type> add_library;

    //https://cmake.org/cmake/help/latest/command/add_library.html#object-libraries
    qi::rule<Iterator, AddLibrary(), ascii::space_type> add_object_library;

    //https://cmake.org/cmake/help/latest/command/add_executable.html#normal-executables
    qi::rule<Iterator, AddExecutable(), ascii::space_type> add_executable;

    //a scoped list (PRIVATE ... PUBLIC ... INTERFACE ...)
    qi::rule<Iterator, ScopedList(), ascii::space_type> scoped_list;

    //https://cmake.org/cmake/help/latest/command/target_sources.html
    qi::rule<Iterator, TargetSources(), ascii::space_type> target_sources;

    //any top-level cmake statement
    qi::rule<Iterator, CMakeStatement(), ascii::space_type> cmake_statement;
};

}

template <typename Iterator, typename Grammar, typename AstStruct>
static bool parse_cmake(Iterator first, Iterator last, const Grammar& grammar, AstStruct& ast_struct)
{
    using qi::double_;
    using qi::phrase_parse;
    using ascii::space;

    bool r = phrase_parse(
        first,                       
        last,                           
        grammar,
        space,
        ast_struct  
    );
    if (first != last) // fail if we did not get a full match
        return false;
    return r;
}

namespace 
{
    struct CMakeStringListParser : CMakeParser::Parser
    {
        bool parse(const std::string& source) const
        {
            Ast::cmake_grammar<std::string::const_iterator> grammar(source.begin());
            Ast::CMakeStringList ast_struct;
            return parse_cmake(source.begin(), source.end(), grammar.cmake_string_list, ast_struct);
        }
    };
}

namespace CMakeParser
{
    std::unique_ptr<Parser> CreateCMakeStringListParser()
    {
        return std::make_unique<CMakeStringListParser>();
    }
}
