/**
 * IPK project (BUT FIT) - Bandwidth measurement 
 * Author: Peter Kapicak (xkapic02)
 * Date: 31.03.2018
 */

#include <iostream>
#include <cstdlib>
#include <getopt.h>
#include <unistd.h>

#include "controlArgs.hpp"

ArgsControl::ArgsControl(int argc, char** argv) {
    argsCnt = argc;
    argsNames = argv;
    this->isHost = false;
    this->isPort = false;
    this->isInterval = false;
    this->isSondaSize = false;
    this->isReflect = false;
    this->isMeter = false;
}

void ArgsControl::checkCorrectness() {
    if (this->isReflect && this->isPort) {
        if (optind != 4) {
            throw std::logic_error("ERROR: Wrong arguments");
        }
    }
    else if (isMeter && !isReflect && isHost && isPort && isInterval && isSondaSize) {
        if (optind != argsCnt) {
            throw std::logic_error("ERROR: Wrong arguments");
        }
    }
    else {
        throw std::logic_error("ERROR: Wrong arguments");
    }
}

void ArgsControl::parsingArguments() {

    opterr = 0;
    int opt;

    std::string part(argsNames[1]);
    if (part == "meter") {
        isMeter = true;
    }
    else if (part == "reflect") {
        isReflect = true;
    }
    else {
        throw std::logic_error("ERROR: Missing argument for choose if meter or reflector.");
    }

    optind++;
    while (optind < argsCnt) {
        if ((opt = getopt(argsCnt, argsNames, "h:p:s:t:")) != -1) {
            switch (opt) {
                case 'h':
                    if (this->isHost) {
                        throw std::logic_error("ERROR: Same argument is set two or more times");;
                    }
                    this->isHost = true;
                    this->hostname = optarg;
                    break;
                
                case 'p':
                    if (this->isPort) {
                        throw std::logic_error("ERROR: Same argument is set two or more times");
                    }
                    this->isPort = true;
                    this->numericArgs.push_back(std::stoi(optarg));
                    break;

                case 's':
                    if (this->isSondaSize) {
                        throw std::logic_error("ERROR: Same argument is set two or more times");
                    }
                    this->isSondaSize = true;
                    this->numericArgs.push_back(std::stoi(optarg));
                    break;

                case 't':
                    if (this->isInterval) {
                        throw std::logic_error("ERROR: Same argument is set two or more times");
                    }
                    this->isInterval = true;
                    this->numericArgs.push_back(std::stoi(optarg));
                    break;

                case '?':
                    throw std::logic_error("ERROR: Missing optional argument or arguments");
            }
        }
    }

    checkCorrectness();
}



std::vector<int> ArgsControl::getNumericArgs() {
    return this->numericArgs;
}

std::string ArgsControl::getHostname() {
    return this->hostname;
}

bool ArgsControl::chooseSide() {
    if (isReflect) {
        return true;
    }
    return false;
}