#include "server.h"

void getInfo(FILE *fr, Arguments *args, char *buffer) {
    
    char line[BUFFER_SIZE];
    static char result[BUFFER_SIZE];
    int count = 0;
    int c;
    static int emptyResult = 1;

    if ( !emptyResult ) {// if buffer was full result is add to empty buffer after sent old one
        emptyResult = 1;
        addToBuffer(buffer, result);
    }

    while ( (c = fgetc(fr)) != EOF && count < BUFFER_SIZE ) {
        if ( c == '\n' ) {
            line[count] = c;
            
            if ( strcmp(args->search, NAME) == 0 ) {
                searchName(line, args, result);
            }
            else if ( strcmp(args->search, FOLDER) == 0 ) {
                searchFolder(line, args, result);
            }
            else if ( strcmp(args->search, LOGIN) == 0 ) { 
                searchLogins(line, args, result);
            }
            if ( strlen(result) != 0 ) {// add to buffer if result is not empty
                if ( addToBuffer(buffer, result) ) {
                    emptyResult = 0;
                    return;
                } 
                if ( strcmp(args->search, FOLDER) == 0 || strcmp(args->search, NAME) == 0 ){// buffer is send after find result with these flags
                    return;
                }
            } 
            // prepare variables for new line
            count = 0;
            memset(line,0,BUFFER_SIZE);
        }
        else {
            line[count] = c;
            count++;
        }
    }

    if ( strcmp(args->search, NAME) == 0 ) {
        searchName(line, args, result);
    }
    else if ( strcmp(args->search, FOLDER) == 0 ) {
        searchFolder(line, args, result);
    }
    else if ( strcmp(args->search, LOGIN) == 0 ) {
        searchLogins(line, args, result);
    }
    if ( strlen(result) != 0 ) {
        if ( addToBuffer(buffer, result) ) {
            emptyResult = 0;
            return;
        }  
    }
    return;
}

int addToBuffer(char *buffer, char *result) {
    int check = 0; // variable for control size

    check = strlen(buffer) + strlen(result) + 2; // 2 additional characters because "\n"
    if ( check < BUFFER_SIZE ) {
        result = strcat(result, "\n");
        buffer = strcat(buffer, result);
        memset(result, 0, BUFFER_SIZE);
        return 0;
    }
    else {
        return 1;
    }
}

void searchFolder(char *line, Arguments *args, char *result) {
    int cnt = 0, colonCnt = 0, resCnt = 0;
    char name[BUFFER_SIZE];
    memset(name, 0, BUFFER_SIZE);

    while ( colonCnt < 6 && line[cnt] != EOF ) {
        
        if ( line[cnt] == ':' ) {
            colonCnt++;
            if ( colonCnt == 5 ) {// increment because on this index of line is colon
                cnt++;
            }
            if ( colonCnt == 1 ) {//control if login is correct 
                if ( strcmp(args->login, name) != 0 ) {
                    return;
                }
            }
        }
        else {
            name[cnt] = line[cnt];
        }

        // if colonCnt is bigger than 4
        // after this colon is data what want client
        if ( colonCnt < 5 ) {
            cnt++;
        }
        else {// store data to the next colon
            if ( line[cnt] != ':' ) {
                result[resCnt] = line[cnt];
                cnt++;
                resCnt++;
            }
            else {
                return;
            }
        }
    }
    return;
}

void searchName(char *line, Arguments *args, char *result) {
    int cnt = 0, colonCnt = 0, resCnt = 0;
    char name[BUFFER_SIZE];
    memset(name, 0, BUFFER_SIZE);

    while ( colonCnt < 5 && line[cnt] != EOF ) {
        
        if ( line[cnt] == ':' ) {
            colonCnt++;
            if ( colonCnt == 4 ) {// increment because on this index of line is colon
                cnt++;
            }
            if ( colonCnt == 1 ) {//control if login is correct
                if ( strcmp(args->login, name) != 0 ) {
                    return;
                }
            }
        }
        else {
            name[cnt] = line[cnt];
        }
        // if colonCnt is bigger than 4
        // after this colon is data what want client
        if ( colonCnt < 4 ) {
            cnt++;
        }
        else {// store data to the next colon
             if ( line[cnt] != ':' ) {
                result[resCnt] = line[cnt];
                cnt++;
                resCnt++;
            }
            else {
                return;
            }
        }
    }
    return;
}

void searchLogins(char *line, Arguments *args, char *result) {
    int cnt = 0;
    int isMatch = 0;

    while ( line[cnt] != ':' && line[cnt] != EOF ) {
        
        result[cnt] = line[cnt];

        if ( strlen(args->login) != 0 ) {
            
            if ( strcmp(args->login, result) == 0 ) {
                isMatch = 1; // if prefix was matched
            }
        }
        cnt++;
    }
    if ( isMatch ) {
        return;
    }
    else if ( strlen(args->login) != 0 ) { // if prefix was not matched
        memset(result, 0, BUFFER_SIZE);
        return;
    }   
    else {
        return;
    }
}

void *requestRoutine(void *cSocket) {
    // ***** from website binarytides.com, only 1 line below
    int clientSocket = *(int*)cSocket;

    bool endFlag = false;

    char buff[BUFFER_SIZE];
    char param[BUFFER_SIZE] = "OK"; // just message for send to client as answer for arguments
    char buffer[BUFFER_SIZE];
    
    Arguments *args;

    if ( (args = malloc( sizeof(Arguments))) == NULL ) {
        exit(SERVER_ERR);
    }
    memset(args->login,0,BUFFER_SIZE);
    memset(args->search,0,BUFFER_SIZE);

    // opening file    
    FILE *fr;
    if ( (fr = fopen("/etc/passwd", "r")) == NULL ) {
        fprintf(stderr,"FILE WAS NOT OPENED\n");
    }

// Recieving arguments by client
    if ( recv(clientSocket, buff, BUFFER_SIZE, 0) < 0 ) {
        perror("ERROR: recv");
        exit(SERVER_ERR);
    }
    if ( send(clientSocket, param, BUFFER_SIZE, 0) < 0 ) {
        perror("ERROR: send");
        exit(SERVER_ERR);
    }
    strcpy(args->login, buff);// save arguments to structure

    memset(buff,0,BUFFER_SIZE);

    if ( recv(clientSocket, buff, BUFFER_SIZE, 0) < 0 ) {
        perror("ERROR: recv");
        exit(SERVER_ERR);
    }
    if ( send(clientSocket, param, BUFFER_SIZE, 0) < 0 ) {
        perror("ERROR: send");
        exit(SERVER_ERR);
    }
    strcpy(args->search, buff);// save arguments to structure

    memset(buff,0,BUFFER_SIZE);
    memset(buffer,0,BUFFER_SIZE);

    // communication with client
    while ( recv(clientSocket, buff, BUFFER_SIZE, 0) > 0 ) {
            
        if ( !endFlag ) {// if data was found then end
            getInfo(fr, args, buffer);
        } 
        
        if ( strlen(buffer) == 0 ) {
            strcpy(buffer, END_INFO);
        }
        else if ( strcmp(args->search, NAME) == 0 || strcmp(args->search, FOLDER) == 0 ) {
            endFlag = true; // if client want find name or folder then searching end  
        }

        if ( send(clientSocket, buffer, BUFFER_SIZE, 0) < 0 ) {
            perror("ERROR: send");
            exit(SERVER_ERR);
        }
        memset(buffer,0,BUFFER_SIZE);
    }
    fclose(fr);
    free(args);
    free(cSocket);
    return 0;
}