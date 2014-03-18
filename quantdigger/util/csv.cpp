#include "csv.h" 
#include <fstream>
using namespace std;

namespace QuantDigger {

std::istream& operator>>(std::istream& str,CSVRow& data)
{
    data.readNextRow(str);
    return str;
} 

}; /* QuantDigger */
