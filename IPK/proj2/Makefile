# Makefile for IPK project - Bandwidth measurement
# Author: Peter Kapicak (xkapic02)
# Date: 31.03.2018

CC = g++
FLAGS = -std=c++11 -Wall -Wextra -Werror -g

all: ipk-mtrip

ipk-mtrip: mtrip.o controlArgs.o meter.o reflect.o
	$(CC) $(FLAGS) mtrip.o controlArgs.o meter.o reflect.o -o ipk-mtrip

mtrip.o: mtrip.cpp controlArgs.hpp
	$(CC) $(FLAGS) -c mtrip.cpp -o mtrip.o

meter.o: meter.cpp meter.hpp
	$(CC) $(FLAGS) -c meter.cpp -o meter.o

reflect.o: reflect.cpp reflect.hpp
	$(CC) $(FLAGS) -c reflect.cpp -o reflect.o

controlArgs.o: controlArgs.cpp controlArgs.hpp
	$(CC) $(FLAGS) -c controlArgs.cpp -o controlArgs.o

clean: 
	rm *.o ipk-mtrip

zip: *.cpp *.hpp Makefile dokumentace.pdf README
	zip xkapic02.zip *.cpp *.hpp Makefile dokumentace.pdf README