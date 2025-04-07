# CC = g++
# CFLAGS = -O3 -Wall -Wextra -pedantic
# SRC = main.cpp
# TARGET = cpp_simulation

# all: $(TARGET)

# $(TARGET): $(SRC)
# 	$(CC) $(CFLAGS) -std=c++23 -o $(TARGET) $(SRC)

# clean:
# 	rm -f $(TARGET)
CXX = g++-11
CXXFLAGS = -std=c++23 -O3 -Wall -Wextra -pedantic
BOOST_LIBS = -lboost_program_options

SRCS = main.cpp
OBJS = $(SRCS:.cpp=.o)
EXEC = cpp_simulation

.PHONY: all clean

all: $(EXEC)

$(EXEC): $(OBJS)
	$(CXX) $(CXXFLAGS) -o $@ $^ $(BOOST_LIBS)

%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

clean:
	rm -f $(OBJS) $(EXEC)