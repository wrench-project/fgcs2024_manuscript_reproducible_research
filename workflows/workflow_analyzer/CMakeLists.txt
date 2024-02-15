cmake_minimum_required(VERSION 3.2)
message(STATUS "Cmake version ${CMAKE_MAJOR_VERSION}.${CMAKE_MINOR_VERSION}.${CMAKE_PATCH_VERSION}")

project(scheduling-using-simulation-simulator CXX)

# Disable annoying warnings
add_definitions("-DBOOST_ALLOW_DEPRECATED_HEADERS")

add_definitions("-Wall -Wno-unused-variable -Wno-unused-private-field")

# Make Release the default build type
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release)
endif()

set(CMAKE_CXX_STANDARD 14)

set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} "${CMAKE_SOURCE_DIR}/CMakeModules/")

find_package(SimGrid REQUIRED)
find_package(WRENCH REQUIRED)
find_package(Boost COMPONENTS program_options REQUIRED)

# include directories for dependencies and WRENCH libraries
include_directories(src/ ${SimGrid_INCLUDE_DIR}/include /usr/local/include /opt/local/include /usr/local/include/wrench ${Boost_INCLUDE_DIR})

# source files
set(SOURCE_FILES
        src/main.cpp
        )

# test files
set(TEST_FILES
        )

# wrench library and dependencies
find_library(WRENCH_LIBRARY NAMES wrench)
find_library(WRENCH_WFCOMMONS_WORKFLOW_PARSER_LIBRARY NAMES wrenchwfcommonsworkflowparser)

# generating the executable
add_executable(workflow_analyzer ${SOURCE_FILES})

if (ENABLE_BATSCHED)
    target_link_libraries(workflow_analyzer
            ${WRENCH_LIBRARY}
            ${WRENCH_WFCOMMONS_WORKFLOW_PARSER_LIBRARY}
            ${SimGrid_LIBRARY}
            ${Boost_LIBRARIES}
            -lzmq )
else()
    target_link_libraries(workflow_analyzer
            ${WRENCH_LIBRARY}
            ${WRENCH_WFCOMMONS_WORKFLOW_PARSER_LIBRARY}
            ${SimGrid_LIBRARY}
            ${Boost_LIBRARIES}
            )
endif()

install(TARGETS workflow_analyzer DESTINATION bin)
