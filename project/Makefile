CC = g++
CFLAGS = -O3 -Wall -Wextra -pedantic
SRC = main.cpp
TARGET = cpp_simulation

all: $(TARGET)

$(TARGET): $(SRC)
	$(CC) $(CFLAGS) -std=c++23 -o $(TARGET) $(SRC)

clean:
	rm -f $(TARGET)
