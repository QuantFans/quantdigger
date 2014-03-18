#include "function.h" 
using namespace std;
namespace QuantDigger {
using namespace QDLanguage;
Number average(NumberSeriesReference data, Number n){
    Number sum = 0;
    for (int i = 0; i < n; i++) {
       sum += data[i];
    }
    return sum / n;
}



} /* QuantDigger */

