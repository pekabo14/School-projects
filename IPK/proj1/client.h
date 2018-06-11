/**
 * @author Peter Kapicak (xkapic02)
 * @date 09 March 2018
 * @brief Header file for client 
 */

#ifndef CLIENT_H
#define CLIENT_H

#include <stdio.h>
#include <stdbool.h>
#include <string.h>

#define ARG_ERR 1
#define CLIENT_ERR 2

#define BUFFER_SIZE 1500

// strings for controls messages between client/server
#define SEND_ME "send"
#define END_INFO "end_info"

// strings for arguments on the side of server
static const char NAME[] = "name";
static const char FOLDER[] = "fold";
static const char LOGIN[] = "logn";

// for store arguments
typedef struct ArgInfo {
    bool n_arg;
    bool f_arg;
    bool l_arg;

    char* login;
    char* host;

    int port;
}ArgInfo;

/**
 * @brief
 * @param int
 * @param char**
 * @param ArgInfo*
 * @return int
 */
int argControl(int argc, char**argv, ArgInfo *args);

#endif