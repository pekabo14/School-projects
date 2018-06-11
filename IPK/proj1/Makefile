# Makefile for project to IPK
# Author: Peter Kapicak (xkapic02)

CC = gcc
CFLAGS = -std=c99 -Wall -Wextra -g

all: ipk-client ipk-server

ipk-server: server.o serverFunctions.o
	$(CC) $(CFLAGS) -pthread server.o serverFunctions.o -o ipk-server

ipk-client: client.o clientFunctions.o
	$(CC) $(CFLAGS) client.o clientFunctions.o -o ipk-client

server.o: server.c server.h
	$(CC) $(CFLAGS) -c server.c -o server.o 

client.o: client.c client.h
	$(CC) $(CFLAGS) -c client.c -o client.o

serverFunctions.o: serverFunctions.c server.h
	$(CC) $(CFLAGS) -c serverFunctions.c -o serverFunctions.o

clientFunctions.o: clientFunctions.c client.h
	$(CC) $(CFLAGS) -c clientFunctions.c -o clientFunctions.o

clean:
	rm *.o ipk-server ipk-client

zip: *.c *.h Makefile dokumentace.pdf README
	zip xkapic02.zip *.c *.h Makefile dokumentace.pdf README