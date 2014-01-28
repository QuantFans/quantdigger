#include "talgo.h" 
#include <iostream>
#include <easyquant/technical/function.h>
#include <easyquant/eqlanguage/definition.h>
using namespace std;
namespace EasyQuant {
using namespace EQLanguage;

void TAlgo::ExcuteAlgorithm() {
    cout<<open + 1<<"*";
    if (curbar != 0) {
        cout<<average(open, 2);
    }
    cout<<endl;
}

} /* EasyQuant */
