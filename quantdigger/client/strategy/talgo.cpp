#include "talgo.h" 
#include <iostream>
#include <quantdigger/client/technical/function.h>
#include <quantdigger/client/qdlanguage/definition.h>
using namespace std;
namespace QuantDigger {
using namespace QDLanguage;

void TAlgo::handleCurrentBar() {
    cout<<"open: ";
    cout<<open<<" average(2): ";
    if (curbar != 0) {
        cout<<average(open, 2);
    }
    cout<<endl;
}

} /* QuantDigger */
