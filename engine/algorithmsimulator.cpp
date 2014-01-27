#include "algorithmsimulator.h" 
#include "tradingalgorithm.h"
namespace EasyQuant {
    
void AlgorithmSimulator::Run() {
    // for every tick
    // foreach algorithm
    for(auto *algo : algorithms_) {
        algo->InitialData();
    }
}

void AlgorithmSimulator::RegisterAlgorithm(TradingAlgorithm *algo, const string& fname) {
    algo->load_history_data(fname);
}

} /* EasyQuant */
