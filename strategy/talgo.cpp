#include "talgo.h" 
#include <iostream>
#include <technical/function.h>
#include <eqlanguage/definition.h>
using namespace std;
namespace EasyQuant {
using namespace EQLanguage;

void TAlgo::ExcuteAlgorithm() {
    cout<<open[0]<<"*";
    if (curbar != 0) {
        cout<<average(open, 2);
    }
    cout<<endl;
}

} /* EasyQuant */
