#include <fstream>
#include <iostream>
#include "csv.h" 
using namespace EasyQuant;
int test_csv()
{
    std::ifstream file("./test.csv");
    std::string         line;
    for(CSVIterator iter(file); iter != CSVIterator(); ++iter) {
        std::cout << "2th Element(" << (*iter)[1] << ")\n";
    }
}
