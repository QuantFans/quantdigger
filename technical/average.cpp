#include "function.h" 
using namespace std;
namespace EasyQuant {
using namespace EQLanguage;
Number average(NumberSeriesReference data, Number n){
    Number sum = 0;
    for (int i = 0; i < n; i++) {
       sum += data[i];
    }
    return sum / n;
}



} /* EasyQuant */

