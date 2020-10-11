
#include <BoostSpiritCMakeParser/parser.hpp>

#include <vector>

#include <boost/bind/bind.hpp>

#include <boost/spirit/include/qi.hpp>
#include <boost/spirit/include/phoenix_core.hpp>
#include <boost/spirit/include/phoenix_operator.hpp>
#include <boost/spirit/include/phoenix_fusion.hpp>
#include <boost/spirit/include/phoenix_stl.hpp>
#include <boost/spirit/include/phoenix_object.hpp>
#include <boost/fusion/adapted/struct/adapt_struct.hpp>
#include <boost/fusion/include/adapt_struct.hpp>

using namespace boost::spirit;
using namespace boost::spirit::ascii;

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
    (auto, cmake_string_list),
    (auto, parent_scope)
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
using Skipper = qi::rule<Iterator>;

template<typename Iterator>
struct cmake_grammar:
    qi::grammar<Iterator, CMakeStatement(), Skipper<Iterator>>
{
    cmake_grammar(Iterator inputBegin):
        cmake_grammar::base_type(cmake_statement)
    {
        using qi::lit;
        using ascii::char_;
        using ascii::string;
        using qi::int_;
        using qi::eps;
        using qi::lexeme;
        using qi::skip;
        using qi::on_success;
        using qi::on_error;

        dblQuotedString %= lexeme["\"" >> +(char_ - "\"") >> "\""];

        variable_use %= lit("${") >> +(char_ - "}") >> "}";
        equivalent_variable_use %= variable_use | ("\"" >> variable_use >> "\"");

        location %= eps[_val = 0U]; //This will be filled later with on_success

        word_until_space %= lexeme[+(char_ - ascii::space)];

        //this is not used to parse into anything meaningful, so they are combined into a single token. This makes this easily managed
        word_until_space_or_rpar %= lexeme[+(char_ - ascii::space - lit(")"))];
        variable_use_to_compose_list_item %= (dblQuotedString >> equivalent_variable_use)
            | (equivalent_variable_use >> dblQuotedString)
            | (word_until_space_or_rpar >> equivalent_variable_use)
            | (equivalent_variable_use >> word_until_space_or_rpar);

        variable_use_with_location %= equivalent_variable_use >> location;

        parent_scope_keyword %= lit("PARENT_SCOPE");
        scope_specifier_keywords = lit("PRIVATE") | lit("PUBLIC") | lit("INTERFACE");

        list_item_string %= dblQuotedString 
            | variable_use_to_compose_list_item
            | (word_until_space_or_rpar - parent_scope_keyword - scope_specifier_keywords);
        list_item_string_with_location %= list_item_string >> location;

        any_list_item %= (variable_use_with_location 
            | list_item_string_with_location);

        cmake_string_list %= +any_list_item;

	    on_success(variable_use_with_location, 
            boost::bind(&set_match_location_on_success<Iterator, VariableUseWithLocation>, boost::placeholders::_1, boost::placeholders::_2, inputBegin));
        on_success(list_item_string_with_location, 
            boost::bind(&set_match_location_on_success<Iterator, ListItemStringWithLocation>, boost::placeholders::_1, boost::placeholders::_2, inputBegin));

        const auto set_keyword = lit("set") | lit("SET");

        set_normal_variable_cmake_string_list %= +(any_list_item);

        set_normal_variable %= set_keyword >> "(" >> word_until_space >> cmake_string_list >> (parent_scope_keyword >> ")" | ")");
        
        set_env_variable %= set_keyword >> "(" >> "ENV" >> "{" >> word_until_space >> "}" >> -(word_until_space - ")") >> ")";

        const auto add_library_keyword = lit("add_library") | lit("ADD_LIBRARY");
        const auto normal_library_types = lit("STATIC") | lit("SHARED") | lit("MODULE");
        const auto exclude_from_all_flag = lit("EXCLUDE_FROM_ALL");

        add_library %= add_library_keyword >> "(" >> word_until_space >> -normal_library_types >> -exclude_from_all_flag >> cmake_string_list >> ")";

        const auto object_library_type_keyword = lit("OBJECT");

        add_object_library %= add_library_keyword >> "(" >> word_until_space >> object_library_type_keyword >> cmake_string_list >> ")";

        const auto add_executable_keyword = lit("add_executable") | lit("ADD_EXECUTABLE");
        const auto add_executable_win32_keyword = lit("WIN32");
        const auto add_executable_macosx_bundle_keyword = lit("MACOSX_BUNDLE");

        add_executable %= add_executable_keyword >> "(" >> word_until_space >> -add_executable_win32_keyword >> -add_executable_macosx_bundle_keyword >> -exclude_from_all_flag >> cmake_string_list >> ")";

        const auto target_sources_keyword = lit("target_sources") | lit("TARGET_SOURCES");

        scoped_list %= scope_specifier_keywords >> cmake_string_list;

        target_sources %= target_sources_keyword >> "(" >> (word_until_space - scope_specifier_keywords) >> +scoped_list >> ")";

        cmake_statement %= set_normal_variable | add_executable | add_library | add_object_library | target_sources;
    }
 
    //basics
    qi::rule<Iterator, std::string(), Skipper<Iterator>> dblQuotedString;
    qi::rule<Iterator, std::string(), Skipper<Iterator>> word_until_space;
    qi::rule<Iterator, std::string(), Skipper<Iterator>> word_until_space_or_rpar;
    qi::rule<Iterator, std::string(), Skipper<Iterator>> parent_scope_keyword;
    qi::rule<Iterator, unsigned(), Skipper<Iterator>> location;

    //list item string (a list item that is just a string)
    qi::rule<Iterator, std::string(), Skipper<Iterator>> list_item_string;
    qi::rule<Iterator, ListItemStringWithLocation(), Skipper<Iterator>> list_item_string_with_location;

    //variable use
    qi::rule<Iterator, std::string(), Skipper<Iterator>> variable_use;
    qi::rule<Iterator, std::string(), Skipper<Iterator>> equivalent_variable_use;
    qi::rule<Iterator, std::string(), Skipper<Iterator>> variable_use_to_compose_list_item;

    qi::rule<Iterator, VariableUseWithLocation(), Skipper<Iterator>> variable_use_with_location;

    //list item
    qi::rule<Iterator, std::string(), Skipper<Iterator>> scope_specifier_keywords;
    qi::rule<Iterator, boost::variant<VariableUseWithLocation, ListItemStringWithLocation>(), Skipper<Iterator>> any_list_item;

    //cmake string list
    qi::rule<Iterator, CMakeStringList(), Skipper<Iterator>> set_normal_variable_cmake_string_list;
    qi::rule<Iterator, CMakeStringList(), Skipper<Iterator>> cmake_string_list;

    //https://cmake.org/cmake/help/latest/command/set.html#set-normal-variable 
    qi::rule<Iterator, SetNormalVariable(), Skipper<Iterator>> set_normal_variable;
    qi::rule<Iterator, SetNormalVariable(), Skipper<Iterator>> set_parent_variable;

    //https://cmake.org/cmake/help/latest/command/set.html#set-environment-variable
    qi::rule<Iterator, SetEnvVariable(), Skipper<Iterator>> set_env_variable;

    //https://cmake.org/cmake/help/latest/command/add_library.html#normal-libraries
    qi::rule<Iterator, AddLibrary(), Skipper<Iterator>> add_library;

    //https://cmake.org/cmake/help/latest/command/add_library.html#object-libraries
    qi::rule<Iterator, AddLibrary(), Skipper<Iterator>> add_object_library;

    //https://cmake.org/cmake/help/latest/command/add_executable.html#normal-executables
    qi::rule<Iterator, AddExecutable(), Skipper<Iterator>> add_executable;

    //a scoped list (PRIVATE ... PUBLIC ... INTERFACE ...)
    qi::rule<Iterator, ScopedList(), Skipper<Iterator>> scoped_list;

    //https://cmake.org/cmake/help/latest/command/target_sources.html
    qi::rule<Iterator, TargetSources(), Skipper<Iterator>> target_sources;

    //any top-level cmake statement
    qi::rule<Iterator, CMakeStatement(), Skipper<Iterator>> cmake_statement;
};

}

template <typename Iterator, typename Grammar, typename AstStruct>
static bool parse_cmake(Iterator first, Iterator last, const Grammar& grammar, AstStruct& ast_struct)
{
    using qi::double_;
    using qi::phrase_parse;
    using ascii::space;

    const auto comment = "#" >> +(char_ - qi::eol) >> qi::eol;
    qi::rule<Iterator> skipper = space | comment;

    const bool r = phrase_parse(
        first,                       
        last,                           
        grammar,
        skipper,
        ast_struct  
    );
    if (first != last) // fail if we did not get a full match
        return false;
    return r;
}

namespace 
{
    template<typename Iterator, typename AstT>
    auto GetRule(Ast::cmake_grammar<Iterator>& grammar);

    template<>
    auto GetRule<std::string::const_iterator, Ast::CMakeStringList>(Ast::cmake_grammar<std::string::const_iterator>& grammar)
    {
        return grammar.cmake_string_list;
    }

    template<>
    auto GetRule<std::string::const_iterator, Ast::SetNormalVariable>(Ast::cmake_grammar<std::string::const_iterator>& grammar)
    {
        return grammar.set_normal_variable;
    }

    template<typename AstT>
    struct ParserImpl : CMakeParser::Parser<AstT>
    {
        boost::optional<AstT> parse(const std::string& source) const
        {
            Ast::cmake_grammar<std::string::const_iterator> grammar(source.begin());
            AstT ast_struct;
            if(parse_cmake(source.begin(), source.end(), GetRule<std::string::const_iterator, AstT>(grammar), ast_struct))
                return ast_struct;
            return boost::none;
        }
    };
}

namespace CMakeParser
{
    std::unique_ptr<Parser<Ast::CMakeStringList>> CreateCMakeStringListParser()
    {
        return std::make_unique<ParserImpl<Ast::CMakeStringList>>();
    }

    std::unique_ptr<Parser<Ast::SetNormalVariable>> CreateSetNormalVariableParser()
    {
        return std::make_unique<ParserImpl<Ast::SetNormalVariable>>();
    }
}
