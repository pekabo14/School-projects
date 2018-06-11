/**
 * IPK project (BUT FIT) - Bandwidth measurement 
 * Author: Peter Kapicak (xkapic02)
 * Date: 31.03.2018
 */

#include <iostream>

#include "controlArgs.hpp"
#include "meter.hpp"
#include "reflect.hpp"

using namespace std;

int main(int argc, char** argv) {
    ArgsControl argsControl(argc, argv);
    argsControl.parsingArguments();

    vector <int> numArgs = argsControl.getNumericArgs();
    string hostname = argsControl.getHostname();

    if (argsControl.chooseSide()) {
        Reflector reflector(numArgs);
        reflector.createReflector();
    }
    else {
        Meter meter(numArgs, hostname);
        meter.createMeter();
    }

    return 0;
}