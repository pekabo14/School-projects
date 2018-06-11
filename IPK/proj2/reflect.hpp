/**
 * IPK project (BUT FIT) - Bandwidth measurement 
 * Author: Peter Kapicak (xkapic02)
 * Date: 31.03.2018
 */

#ifndef REFLECT_H
#define REFLECT_H

#include <iostream>
#include <vector>

#include <netinet/in.h>

#define DEFAULT_P_SIZE 512

class Reflector {
    std::vector <int> numArgs; 
    int udpSocket;
    int tcpSocket;

    struct sockaddr_in address;

    void createSocket();
    void bindingCommunication();
    void reflectCommunicaton();

    public:
        Reflector(std::vector <int> numArgs);
        void createReflector();
};

#endif