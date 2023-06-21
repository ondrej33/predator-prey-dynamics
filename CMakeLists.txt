cmake_minimum_required(VERSION 3.23)
project(cpp_simulation)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_FLAGS "-O3 -Wall -Wextra -pedantic")
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/../")

# Find the Boost libraries
find_package(Boost REQUIRED COMPONENTS program_options)

add_executable(cpp_simulation main.cpp)

# Link the Boost program_options library to your executable
target_link_libraries(cpp_simulation Boost::program_options)
#target_link_libraries(my_executable_name boost_program_options)
