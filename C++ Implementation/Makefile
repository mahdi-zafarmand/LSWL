# CC = g++
CC = clang++
CFLAGS =	-g	-std=c++11	-Wall	-O3
TARGET = sna

all : $(TARGET)

$(TARGET): Node.o Edge.o  Graph.o Status.o	SIWO.o	functions.o	main.o
		$(CC)	$(CFLAGS)	-o	sna	Node.o	Edge.o	Graph.o	Status.o	SIWO.o	functions.o	main.o

Node.o:	Node.cpp	Node.hpp
		$(CC)	$(CFLAGS)	-c	Node.cpp

Edge.o:	Edge.cpp	Edge.hpp	Node.hpp
		$(CC)	$(CFLAGS)	-c	Edge.cpp

Graph.o:	Graph.cpp	Graph.hpp	Edge.hpp
		$(CC)	$(CFLAGS)	-c	Graph.cpp

Status.o:	Status.cpp	Status.hpp	Graph.hpp
		$(CC)	$(CFLAGS)	-c	Status.cpp

SIWO.o:	SIWO.cpp	SIWO.hpp	Status.hpp	Graph.hpp	functions.hpp
		$(CC)	$(CFLAGS)	-c	SIWO.cpp

functions.o:	functions.cpp	functions.hpp	Node.hpp
		$(CC)	$(CFLAGS)	-c	functions.cpp

main.o:	main.cpp	SIWO.hpp
		$(CC)	$(CFLAGS)	-c	main.cpp

clean:
		$(RM)	sna	*.o	*.gch