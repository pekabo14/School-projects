#include <unistd.h>
#include <stdlib.h>
#include <ctype.h>
#include <getopt.h>


#include "client.h"

int argControl(int argc, char** argv, ArgInfo *args) {

    int opt;
    int port;
    char* endptr;
    opterr = 0;// getopt will not print error messages

    bool h_flag = false;
    bool p_flag = false;
    bool login_flag = false;

    args->n_arg = false;
    args->f_arg = false;
    args->l_arg = false;

    while ( optind < argc ) {
        if ( (opt = getopt(argc, argv, "nflh:p:")) != -1 ) {
            switch ( opt ) {
            case 'n':
                if ( args->n_arg ) {
                    fprintf(stderr, "ERROR: Too many arguments of one type\n");
                    return ARG_ERR;
                }
                args->n_arg = true;
                break;

            case 'f':
                if ( args->f_arg ) {
                    fprintf(stderr, "ERROR: Too many arguments of one type\n");
                    return ARG_ERR;
                }
                args->f_arg = true;
                break;

            case 'l':
                if ( args->l_arg ) {
                    fprintf(stderr, "ERROR: Too many arguments of one type\n");
                    return ARG_ERR;
                }
                args->l_arg = true;
                break;

            case 'h':
                if ( h_flag ) {
                    fprintf(stderr, "ERROR: Too many arguments of one type\n");
                    return ARG_ERR;
                }
                args->host = optarg;
                h_flag = true;
                break;

            case 'p':
                if ( p_flag ) {
                    fprintf(stderr, "ERROR: Too many arguments of one type\n");
                    return ARG_ERR;
                }
                port = (int)strtol(optarg, &endptr, 10);
                if ( strlen(endptr) != 0 ) {
                    fprintf(stderr, "Wrong number of port\n");
                    exit(ARG_ERR);
                }
                args->port = port;
                p_flag = true;
                break;

            case '?':
                fprintf(stderr, "ERROR: Missing optional argument or argument\n");
                return ARG_ERR;

            }// end switch
        }
        else {
            if ( login_flag ) {
                fprintf(stderr, "ERROR: Too many arguments of one type\n");
                return ARG_ERR;
            }
            args->login = argv[optind];
            login_flag = true;
            optind++;
        }
    }// end loop

    if ( args->n_arg == true && args->f_arg == true ) {
        fprintf(stderr, "Use only one argument from [-n|-f|-l]\n");
        return ARG_ERR;
    }
    else if ( args->n_arg == true && args->l_arg == true ) {
        fprintf(stderr, "Use only one argument from [-n|-f|-l]\n");
        return ARG_ERR;
    }
    else if ( args->f_arg == true && args->l_arg == true ) {
        fprintf(stderr, "Use only one argument from [-n|-f|-l]\n");
        return ARG_ERR;
    }
    else if ( args->f_arg == false && args->n_arg == false && args->l_arg == false ) {
        fprintf(stderr, "Missing argument [-n|-f|-l]\n");
        return ARG_ERR;
    }

    if ( args->host == NULL ) {
        fprintf(stderr, "Missing argument -host\n");
        return ARG_ERR;
    }
    if ( args->port == 0 ) {
        fprintf(stderr, "Missing argument -port\n");
        return ARG_ERR;
    } 
    if ( strlen(args->login) == 0 && args->l_arg == false ) {
        fprintf(stderr, "Missing argument login\n");
        return ARG_ERR;
    }

    return 0;
}
