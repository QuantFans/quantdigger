#include "talgo.h" 
using namespace EasyQuant;
int main(int argc, const char *argv[])
{
    TAlgo t;
    t.load_history_data("kdata.csv");
    t.InitialData();

    return 0;
}
