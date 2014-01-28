#include "talgo.h" 
#include <easyquant/util/logger.h>
int main(int argc, const char *argv[])
{
    using namespace EasyQuant;
    TAlgo t;
    t.load_history_data("kdata.csv");
    t.InitialData();

    return 0;
}
