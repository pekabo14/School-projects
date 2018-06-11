/**
 * IPK project (BUT FIT) - Bandwidth measurement 
 * Author: Peter Kapicak (xkapic02)
 * Date: 31.03.2018
 */

#ifndef CONTROL_ARGS_H
#define CONTROL_ARGS_H

#include <iostream>
#include <vector>
#include <string>

/**
 * ArgsControl class for parsing arguments.
 */  
class ArgsControl {
    int argsCnt;
    char** argsNames;

    // to check if argument is set or set only once
    bool isHost;
    bool isPort;
    bool isSondaSize;
    bool isInterval;
    bool isReflect;
    bool isMeter;

    std::vector <int> numericArgs;// expecting order of arguments according to the project assignment
    std::string hostname;

    void checkCorrectness();

    public:
        ArgsControl(int argc, char** argv);
        void parsingArguments();
        std::vector<int> getNumericArgs();
        std::string getHostname();
        bool chooseSide();
};

#endif