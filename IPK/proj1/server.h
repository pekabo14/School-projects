/**
 * @author Peter Kapicak (xkapic02)
 * @date 09 March 2018
 * @brief Header file for server 
 */

#ifndef SERVER_H
#define SERVER_H

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <stdbool.h>
#include <getopt.h>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <pthread.h>

#define BUFFER_SIZE 1500

#define SERVER_ERR 2

// strings for controls messages between client/server
#define SEND_ME "send"
#define END_INFO "end_info"

// strings for arguments on the side of server
static const char NAME[] = "name";
static const char FOLDER[] = "fold";
static const char LOGIN[] = "logn";

// for store information about searching data
typedef struct Arguments {
    char login[BUFFER_SIZE];
    char search[BUFFER_SIZE];
}Arguments;

/**
 * @brief Function for find data for client
 * @param FILE*
 * @param Arguments*
 * @param char*
 * @return void
 */
void getInfo(FILE *fr, Arguments *args, char *buffer);

/**
 * @brief Function for add match to buffer
 * @param char*
 * @param char*
 * @return int
 */
int addToBuffer(char *buffer, char *result);

/**
 * @brief Function for find clients folder
 * @param char*
 * @param Arguments*
 * @param char*
 * @return void
 */
void searchFolder(char *line, Arguments *args, char *result);

/**
 * @brief Function for find clients full name
 * @param char*
 * @param Arguments*
 * @param char*
 * @return void
 */
void searchName(char *line, Arguments *args, char *result);

/**
 * @brief Function for find logins
 * @param char*
 * @param Arguments*
 * @param char*
 * @return void
 */
void searchLogins(char *line, Arguments *args, char *result);

/**
 * @brief Function for proccesed one request
 * @param void*
 * @return void*
 */
void *requestRoutine(void *clientSocket);

#endif