/**
 * @author Peter Kapicak (xkapic02)
 * @date 09 March 2018
 * @brief Communication on side of client 
 */

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <netdb.h>
#include <errno.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include "client.h"

int main(int argc, char** argv) {
 
// --------------------- Control arguments ------------------------------
    int result;
    ArgInfo *args;
    
    if ( (args = malloc( sizeof(ArgInfo))) == NULL ) {
        return CLIENT_ERR;
    }
    args->login = "\0";
    result = argControl(argc, argv, args);
    if ( result != 0 ) {
        return ARG_ERR;
    } 
    
// --------------------- CLIENT ----------------------------------------

    int clientSocket;
    struct sockaddr_in serverAdress;
    struct hostent *hp = gethostbyname(args->host);

    if ( hp == NULL ) {
        perror("ERROR: gethostbyname");
        exit(CLIENT_ERR);
    }

    if ( (clientSocket = socket(AF_INET, SOCK_STREAM, 0)) <= 0 ) {
        perror("ERROR: socket");
        exit(CLIENT_ERR);
    }

    memset(&serverAdress, 0, sizeof(serverAdress));

    serverAdress.sin_family = AF_INET;
    serverAdress.sin_port = htons(args->port);

    serverAdress.sin_addr = *((struct in_addr *)hp->h_addr_list[0]);

    if ( connect(clientSocket, (const struct sockaddr *) &serverAdress, sizeof(serverAdress)) != 0 ) {
        perror("ERROR connect");
        exit(CLIENT_ERR);
    }
    
// ------------------ Client communication -------------------------------------------

    bool emptyFlag = false;
    
    // buffers for sendind and recieving messages
    char buffs[BUFFER_SIZE];
    char param[BUFFER_SIZE]; // buffer for sending arguments

    memset(buffs, 0, BUFFER_SIZE);
    memset(param, 0, BUFFER_SIZE);

    strcpy(param, args->login);

    // sending arguments to server
    if ( send(clientSocket, param, BUFFER_SIZE, 0) < 0 ) {
        perror("ERROR: send");
        exit(CLIENT_ERR);
    }
    if ( recv(clientSocket, buffs, BUFFER_SIZE, 0) < 0 ) {
        perror("ERROR: recv");
        exit(CLIENT_ERR);
    }
    
    memset(buffs, 0, BUFFER_SIZE);
    memset(param, 0, BUFFER_SIZE);

    // choice of which flag is set and sending to server 
    if ( args->n_arg ) {
        strcpy(param, NAME);
    }
    else if ( args->f_arg ) {
        strcpy(param, FOLDER);
    }
    else {
        strcpy(param, LOGIN);
    }


    if ( send(clientSocket, param, BUFFER_SIZE, 0) < 0 ) {
        perror("ERROR: send");
        exit(CLIENT_ERR);
    }
    if ( recv(clientSocket, buffs, BUFFER_SIZE, 0) < 0 ) {
        perror("ERROR: recv");
        exit(CLIENT_ERR);
    }
    
    memset(buffs, 0, BUFFER_SIZE);
    // loop for recieving information from server
    while (1) {
        if ( send(clientSocket, SEND_ME, BUFFER_SIZE, 0) < 0 ) {
            perror("ERROR: send");
            exit(CLIENT_ERR);
        }

        if ( recv(clientSocket, buffs, BUFFER_SIZE, 0) < 0 ) {
            perror("ERROR: recv");
            exit(CLIENT_ERR);
        }

        if ( strcmp(buffs, END_INFO) == 0 ) {// client recieved if transfer of data ends or not
            if ( !emptyFlag ) {// if no match was found in data 
                fprintf(stderr, "No match was found\n");
            }
            break;
        }
        emptyFlag = true; // true if client recieved some data 

        printf("%s", buffs);
        memset(buffs, 0, BUFFER_SIZE);
    }

    close(clientSocket);
    free(args);

    return 0;
}