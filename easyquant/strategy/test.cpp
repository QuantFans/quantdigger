#include "talgo.h" 
#include <easyquant/util/logger.h>
int main(int argc, const char *argv[])
{
    using namespace EasyQuant;
    TAlgo t;
    t.load_history_data("kdata.csv");
    t.initialData();
    auto &logger = singleton_logger();
    logger.setPrintToStdoutFlag(true);
    logger.log("nihao");

    return 0;
}
