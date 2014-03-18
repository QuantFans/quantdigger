#include <fstream>
#include <quantdigger/client/strategy/talgo.h>
#include <quantdigger/client/engine/datasource.h>
#include <quantdigger/client/engine/algorithmsimulator.h>
#include <quantdigger/util/csv.h>
#include <quantdigger/util/logger.h>
using namespace QuantDigger;
bool test_DataSource();
bool test_TradingAlgorithm();
int test_csv();

int main(int argc, const char *argv[])
{
//    auto &logger = singleton_logger();
//    logger.setPrintToStdoutFlag(true);
//    logger.log("nihao");
    test_DataSource();
    test_TradingAlgorithm();
    test_csv();

    return 0;
}

bool test_DataSource() {
    std::cout<<"*Test DataSource*"<<std::endl;
    QuantDigger::DataSource dd;
    dd.load_order_signal("./test/signal.csv");
    dd.load_history_data("./test/kdata.csv");
    std::cout<<dd.order_signals();
    std::cout<<dd.history_data();
    return false;
}

bool test_TradingAlgorithm() {
    std::cout<<"*Test TradingAlgorithm*"<<std::endl;
    AlgorithmSimulator simulator;

//    TAlgo t;
//    t.load_history_data("./test/kdata.csv");
//    t.excuteHistoryData();
}

int test_csv()
{
    std::cout<<"*Test CSVIterator*"<<std::endl;
    std::ifstream file("./test/kdata.csv");
    std::string         line;
    for(CSVIterator iter(file); iter != CSVIterator(); ++iter) {
        std::cout << "2th Element(" << (*iter)[1] << ")\n";
    }
}
