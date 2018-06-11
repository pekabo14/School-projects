/**
 * @author Peter Kapicak (xkapic02)
 * @date 09 March 2018
 * @brief Communication on side of client
 */

#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#include "server.h"

int main(int argc, char** argv) {
    
    int c;
    int port;
    char* endptr;

// --------------- Handling arguments --------------------------------
    opterr = 0;
    while ( (c = getopt(argc, argv, "p:")) != -1 ) {
        switch (c) {
            case 'p':
                port = (int)strtol(optarg, &endptr, 10);
                break;

            case '?':
                fprintf(stderr, "ERROR: Missing optional argument\n");
                exit(SERVER_ERR);
        }
    }

// ----------------- SERVER ---------------------------

    int serverSocket, clientSocket;
    struct sockaddr_in address;
    int addrLen = sizeof(address);

    if ( (serverSocket = socket(AF_INET, SOCK_STREAM, 0)) <= 0 ) {
        perror("ERROR: socket");
        exit(SERVER_ERR);
    }

    memset(&address, 0, sizeof(address));

    address.sin_family = AF_INET;
    address.sin_port = htons(port);
    address.sin_addr.s_addr = INADDR_ANY;

    if ( bind(serverSocket, (struct sockaddr*) &address, sizeof(address)) < 0 ) {
        perror("ERROR: bind");
        exit(SERVER_ERR);
    }

    if ( listen(serverSocket, 1) < 0 ) { 
        perror("ERROR: listen");
        exit(SERVER_ERR);
    }
    
    // server is waiting for request from client
    // server can handle multiple requests from clients
    int *socket;
    while ( (clientSocket = accept(serverSocket, (struct sockaddr *)&address, (socklen_t*)&addrLen)) ) {
        // server creates one thread for one client
        // ***** from website binarytides.com
        pthread_t request;
        socket = malloc(sizeof(int));
        *socket = clientSocket;
        // ***** only these 3 lines above 

        if ( pthread_create(&request, NULL, requestRoutine, (void*)socket) < 0 ) {
            perror("ERROR: thread");
            exit(SERVER_ERR);
        }
    }

    close(clientSocket);
    close(serverSocket);
    
    return 0;
}