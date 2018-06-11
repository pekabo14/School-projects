/**
 * IPK project (BUT FIT) - Bandwidth measurement 
 * Author: Peter Kapicak (xkapic02)
 * Date: 31.03.2018
 */

#include "reflect.hpp"
#include <cstring>

#include <sys/socket.h>
#include <sys/select.h>
#include <sys/types.h>
#include <arpa/inet.h>
#include <netdb.h>
#include <unistd.h>

Reflector::Reflector(std::vector<int> nArgs) {
    numArgs = nArgs;
    udpSocket = 0;
    tcpSocket = 0;
}

void Reflector::createSocket() {
    udpSocket = socket(AF_INET, SOCK_DGRAM, 0);
    if (udpSocket <= 0) {   
        throw std::runtime_error("ERROR: Socket creating failed");
    }

    tcpSocket = socket(AF_INET, SOCK_STREAM, 0);
    if (tcpSocket <= 0) {
        throw std::runtime_error("ERROR: Socket creating failed");
    }
}

void Reflector::bindingCommunication() {
    if (bind(udpSocket, (struct sockaddr*) &address, sizeof(address)) < 0) {
        throw std::runtime_error("ERROR: binding was failed");
    }
    if (bind(tcpSocket, (struct sockaddr*) &address, sizeof(address)) < 0) {
        throw std::runtime_error("ERROR: binding was failed");
    }

    if ( listen(tcpSocket, 1) < 0 ) { 
        throw std::runtime_error("ERROR: listen was failed");
    }
}

void Reflector::reflectCommunicaton() {

    int addrLen = sizeof(address);
    int tcpClientSock = 0;

    if ((tcpClientSock = accept(tcpSocket, (struct sockaddr *)&address, (socklen_t*)&addrLen)) < 0) {
        throw std::runtime_error("ERROR: accept() was failed");
    }

    // get size of packet for measurement
    char packetSize[DEFAULT_P_SIZE] = {0};
    if (recv(tcpClientSock, packetSize, DEFAULT_P_SIZE, 0) < 0) {
        throw std::runtime_error("ERROR: recv()");
    }
    std::string defPacket(packetSize);
    
    int pSize = std::stoi(defPacket);
    
    char recvTcpPacket[pSize] = {0};
    char recvUdpPacket[pSize] = {0};
    char sendTcpPacket[pSize] = {0};

    int numPackets = 0;
    
    while (true) {
        
        fd_set rfd;
        FD_ZERO(&rfd);
        FD_SET(tcpClientSock, &rfd);
        FD_SET(udpSocket, &rfd);

        struct timeval timeout;
        timeout.tv_sec = 0;
        timeout.tv_usec = 0;

       int ret = select(FD_SETSIZE, &rfd, NULL, NULL, &timeout);
        
        if (ret < 0) {
            throw std::runtime_error("ERROR: select() was failed");
        }
        if (ret == 0) {
            continue;
        }

        if (FD_ISSET(tcpClientSock, &rfd)) {
            if (recv(tcpClientSock, recvTcpPacket, pSize, 0) < 0) {
                throw std::runtime_error("ERROR: recv()");
            }
            std::string ackPackets = std::to_string(numPackets);
            std::strcpy(sendTcpPacket, ackPackets.c_str());
            numPackets = 0;
            if (send(tcpClientSock, sendTcpPacket, pSize,0) < 0) {
                throw std::runtime_error("ERROR: send()");
            }
            
           
            std::string res(recvTcpPacket);
            if (res == "END_MEASURE") {
                break;
            }
            std::memset(recvTcpPacket,0,pSize);
        }
        if (FD_ISSET(udpSocket, &rfd)) {
            if (recvfrom(udpSocket, recvUdpPacket, pSize, 0, (struct sockaddr *)&address, (socklen_t*)&addrLen) < 0) {
                throw std::runtime_error("ERROR: recv()");
            }
            else {
                numPackets++;
            }
            std::memset(recvUdpPacket,0,pSize);
        }  
    }
    close(tcpClientSock);
    close(udpSocket);
    close(tcpSocket);
}

void Reflector::createReflector() {
    createSocket();

    std::memset(&address, 0, sizeof(address));

    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(numArgs[0]);

    bindingCommunication();

    reflectCommunicaton();

}