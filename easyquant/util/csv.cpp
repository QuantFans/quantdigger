#include "csv.h" 
#include <fstream>
using namespace std;

namespace EasyQuant {

std::istream& operator>>(std::istream& str,CSVRow& data)
{
    data.readNextRow(str);
    return str;
} 

}; /* EasyQuant */
