#include "algorithmsimulator.h" 
#include "tradingalgorithm.h"
namespace EasyQuant {
    
void AlgorithmSimulator::run() {
    // for every tick
    // foreach algorithm
    for(auto *algo : algorithms_) {
        algo->initialData();
    }
}

void AlgorithmSimulator::registerAlgorithm(TradingAlgorithm *algo, const string& fname) {
    algo->load_history_data(fname);
}

} /* EasyQuant */
