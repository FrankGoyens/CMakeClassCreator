project(BoostSpiritCMakeParser)

set(BoostSpiritCMakeParser_Headers include/BoostSpiritCMakeParser/parser.hpp
)

set(BoostSpiritCMakeParser_Sources
	src/parser.cpp
)

add_library(BoostSpiritCMakeParser ${BoostSpiritCMakeParser_Headers} ${BoostSpiritCMakeParser_Sources})

find_path(BOOST_SPIRIT_INCLUDE_DIRS "boost/spirit.hpp")
find_path(BOOST_FUSION_INCLUDE_DIRS "boost/fusion/adapted.hpp")

target_include_directories(BoostSpiritCMakeParser 
	PUBLIC include 
	PRIVATE ${BOOST_SPIRIT_INCLUDE_DIRS} ${BOOST_FUSION_INCLUDE_DIRS})

target_compile_features(BoostSpiritCMakeParser PRIVATE cxx_std_17)

add_executable(RunBoostSpiritCMakeParser src/Main.cpp)
target_link_libraries(RunBoostSpiritCMakeParser BoostSpiritCMakeParser)
