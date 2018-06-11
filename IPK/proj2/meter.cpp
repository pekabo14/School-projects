/**
 * IPK project (BUT FIT) - Bandwidth measurement 
 * Author: Peter Kapicak (xkapic02)
 * Date: 31.03.2018
 */
#include <cstring>
#include "meter.hpp"
#include <chrono>
#include <thread>
#include <iterator>
#include <cmath>

#include <sys/socket.h>
#include <arpa/inet.h>
#include <netdb.h>
#include <unistd.h>

Meter::Meter(std::vector <int> nArgs, std::string host) {
    numArgs = nArgs;
    hostname = host;
    udpSocket = 0;
    tcpSocket= 0;
}

void Meter::createSocket() {
    udpSocket = socket(AF_INET, SOCK_DGRAM, 0);
    if (udpSocket <= 0) {   
        throw std::runtime_error("ERROR: Socket creating failed");
    }

    tcpSocket = socket(AF_INET, SOCK_STREAM, 0);
    if (tcpSocket <= 0) {
        throw std::runtime_error("ERROR: Socket creating failed");
    }
}

void Meter::meterCommunication() {

    // Packets
    char recvTcpPacket[numArgs[1]] = {0};
    
    char sendPacket[numArgs[1]] = {0};
    std::strcpy(sendPacket, "Little fella for testing");
    
    char endPacket[numArgs[1]] = {0};
    std::strcpy(endPacket, "END_MEASURE");

    int addrLen = sizeof(address);
   
    // for RTT values
    std::chrono::duration<double> resultRtt;
    std::vector<std::chrono::duration<double>> rtt;
    std::vector<std::chrono::duration<double>>::iterator counter;

    // send size of the packet from command line
    
    std::string packetSize = std::to_string(numArgs[1]);
   
    char pcktSize[DEFAULT_P_SIZE] = {0}; 
    std::strcpy(pcktSize, packetSize.c_str());
    if (send(tcpSocket, pcktSize, DEFAULT_P_SIZE, 0) < 0) { 
        throw std::runtime_error("ERROR: sendto()");
    }

// ********* Initial measurement **********
    auto testStart = std::chrono::system_clock::now();

    for (int packet = 0; packet < NUM_OF_STREAM_PACKETS; ++packet) {
        // UDP packets for measurement
        if (sendto(udpSocket, sendPacket, numArgs[1], 0, (struct sockaddr *)&address, addrLen) < 0) {
            throw std::runtime_error("ERROR: sendto() tuto??");
        }
        // Interval for sending packets
        std::this_thread::sleep_for(std::chrono::nanoseconds(10000));
    }
    auto testEnd = std::chrono::system_clock::now();
    
    std::chrono::duration<double> testStreamDuration = testEnd-testStart;
    close(udpSocket);
        udpSocket = socket(AF_INET, SOCK_DGRAM, 0);
        if (udpSocket <= 0) {   
            throw std::runtime_error("ERROR: Socket creating failed");
        }

    double initRate = NUM_OF_STREAM_PACKETS*numArgs[1] / testStreamDuration.count();

// variables for measurement
    int fleet = 0;
    double maxTransRate = 0.0;
    double minTransRate = initRate;
    double actualRate = initRate;
    double avgRate = 0.0;

    std::vector<double> streamsRate;
    std::vector<double>::iterator avgCounter;
    std::chrono::duration<double> measureDuration;

    double tempMaxRate = 0.0;
    double tempMinRate = 0.0;
    double tempAvgRate = 0.0;

    int interval = 10000; //deafult value

    int streams = 0;
    int ackStreams = 0;

    while (true) {
        
        // for measurement information
        if (fleet == MEASURE_INFO) {
            fleet = 0;
        }
        else {
            ++fleet;
        }

        auto measureStart = std::chrono::system_clock::now();// start trans rate measure

        for (int packet = 0; packet < NUM_OF_STREAM_PACKETS; ++packet) {
            // UDP packets for measurement
            if (sendto(udpSocket, sendPacket, numArgs[1], 0, (struct sockaddr *)&address, addrLen) < 0) {
                throw std::runtime_error("ERROR: sendto() tuto??");
            }
            // Interval for sending packets
            std::this_thread::sleep_for(std::chrono::nanoseconds(interval));
        }

        // store info about measure duration
        auto measureEnd = std::chrono::system_clock::now();
        std::chrono::duration<double> oneStreamDuration = measureEnd-measureStart;
        measureDuration += oneStreamDuration;

        streams++;

        close(udpSocket);
        udpSocket = socket(AF_INET, SOCK_DGRAM, 0);
        if (udpSocket <= 0) {   
            throw std::runtime_error("ERROR: Socket creating failed");
        }

        auto startRTT = std::chrono::system_clock::now(); //timestamp for start measure RTT
        if (measureDuration.count() >= numArgs[2]) {
            if (send(tcpSocket, endPacket, numArgs[1], 0) < 0) {
                throw std::runtime_error("ERROR: sendto()");
            }
        }
        else {
            if (send(tcpSocket, sendPacket, numArgs[1], 0) < 0) {
                throw std::runtime_error("ERROR: sendto()");
            }
        }    
        if (recv(tcpSocket, recvTcpPacket, numArgs[1], 0) < 0) {
            throw std::runtime_error("ERROR: recv()");
        }

        auto endRTT = std::chrono::system_clock::now();//timestamp for end measure RTT
        std::chrono::duration<double> elapsed_seconds = endRTT-startRTT;
        rtt.push_back(elapsed_seconds);

        std::string numero(recvTcpPacket);  
        int numberRecvPackets = std::stoi(numero);
        int missing = NUM_OF_STREAM_PACKETS - numberRecvPackets;

        // adjustment interval of send packets
        if (missing >= 5) { // 5 is maximum lose of packet in stream
            interval += ADD_INTERVAL;
        }
        else {// calculating single stream trans rate
            ackStreams++;

            actualRate = numberRecvPackets*numArgs[1] / oneStreamDuration.count();
            streamsRate.push_back(actualRate);
            if (actualRate > maxTransRate) {
                maxTransRate = actualRate;
            }
            else {
                if (actualRate < minTransRate) {
                    minTransRate = actualRate;    
                }
            }

        // print informations about measurement every 50 streams
            if (fleet == MEASURE_INFO) {
                tempMaxRate = ((maxTransRate*8) / 1024) / 1024;
                tempMinRate = ((minTransRate*8) / 1024) / 1024;
                std::cout << "============================================================\n";
                std::cout << "              Current result of measurement\n";
                std::cout << "============================================================\n";
                std::cout << "      Maximum transmission rate = " << tempMaxRate << " Mbit/s\n";
                std::cout << "      Minimum transmission rate = " << tempMinRate << " Mbit/s\n";

                for (avgCounter = streamsRate.begin(); avgCounter < streamsRate.end(); ++avgCounter) {
                    tempAvgRate += *avgCounter;
                }
                tempAvgRate /= streamsRate.size();
                tempAvgRate = ((tempAvgRate*8) / 1024) / 1024;
                std::cout << "      Average transmission rate = " << tempAvgRate << " Mbit/s\n";
            }

            // adjustment interval for send packets
            interval -= SUB_INTERVAL;
            if (interval < 0) {
                interval += SUB_INTERVAL; // for handle interval on zero
            }
        }
        // control time of measurement
        if (measureDuration.count() >= numArgs[2]) {
            break;
        }
        
        std::memset(recvTcpPacket,0,numArgs[1]);
    }
// **************************************************************************************
    // FINAL CALCULATING OF MEASUREMENT
    maxTransRate = ((maxTransRate*8) / 1024) / 1024;
    minTransRate = ((minTransRate*8) / 1024) / 1024;
    std::cout << "============================================================\n";
    std::cout << "============================================================\n";
    std::cout << "              Final result of measurement\n";
    std::cout << "============================================================\n";
    std::cout << "      Maximum transmission rate = " << maxTransRate << " Mbit/s\n";
    std::cout << "      Minimum transmission rate = " << minTransRate << " Mbit/s\n";

    // calculating average transmission rate
    for (avgCounter = streamsRate.begin(); avgCounter < streamsRate.end(); ++avgCounter) {
        avgRate += *avgCounter;
    }
    avgRate /= streamsRate.size();
    avgRate = ((avgRate*8) / 1024) / 1024; // from B/s to Mbit/s
    std::cout << "      Average transmission rate = " << avgRate << " Mbit/s\n";

    // Average RTT calculating
    for (counter = rtt.begin(); counter < rtt.end(); ++counter) {
        resultRtt += *counter;
    }
    resultRtt /= rtt.size();
    std::cout << "      Average RTT =               " << resultRtt.count()*1000 << " ms\n";

    // standard deviation
    std::vector<double>::iterator devCounter;
    double tempRate = 0.0;
    double elem = 0.0;
    double dev = 0.0;
    for (devCounter = streamsRate.begin(); devCounter < streamsRate.end(); ++devCounter) {
        tempRate = *devCounter*8/1024/1024; 
        elem += (tempRate - avgRate)*(tempRate - avgRate);
    }
    elem /= (streamsRate.size() - 1);
    dev = std::sqrt(elem);
    std::cout << "      Std dev of trans rate =     " << dev << " Mbit/s\n";
    std::cout << "============================================================\n";
    std::cout << "      Sent streams =              " << streams << "\n";
    std::cout << "      Useable streams =           " << ackStreams << "\n";
// **************************************************************************************
}

void Meter::createMeter() {
    hp = gethostbyname(hostname.c_str());
    if (!hp) {
        throw std::runtime_error("ERROR: gethostbyname() failed");
    }

    createSocket();

    std::memset(&address, 0, sizeof(address));
   
    address.sin_family = AF_INET;
    address.sin_port = htons(numArgs[0]);
    address.sin_addr = *((struct in_addr *)hp->h_addr_list[0]);

    if ( connect(tcpSocket, (const struct sockaddr *) &address, sizeof(address)) != 0 ) {
        throw std::runtime_error("ERROR: connect() failed");
    }
    meterCommunication();

    
    close(tcpSocket);
}