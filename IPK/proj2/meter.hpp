/**
 * IPK project (BUT FIT) - Bandwidth measurement 
 * Author: Peter Kapicak (xkapic02)
 * Date: 31.03.2018
 */

#ifndef METER_H
#define METER_H

#include <iostream>
#include <vector>

#include <netinet/in.h>

#define DEFAULT_P_SIZE 512
#define NUM_OF_STREAM_PACKETS 100
#define MIN_NUM_OF_STREAMS 120
#define MEASURE_INFO 50

#define ADD_INTERVAL 150
#define SUB_INTERVAL 100

class Meter {
    std::vector <int> numArgs; 
    std::string hostname;
    int udpSocket;
    int tcpSocket;

    struct sockaddr_in address;
    struct hostent *hp;

    void createSocket();
    void meterCommunication();

    public:
        Meter(std::vector <int> numArgs, std::string hostname);
        void createMeter();
};

#endif