#pragma once

#include <string>

#include <memory>

namespace CMakeParser
{
    struct Parser
    {
        virtual ~Parser() = default;
        virtual bool parse(const std::string&) const = 0;
    };

    std::unique_ptr<Parser> CreateCMakeStringListParser();
}
