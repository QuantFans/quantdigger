#ifndef EASYQUANT_ENGINE_ALGORITHMSIMULATOR_H

#define EASYQUANT_ENGINE_ALGORITHMSIMULATOR_H
#include <vector>
#include <string>

namespace EasyQuant {
class TradingAlgorithm;
using std::vector;
using std::string;
    
/**
* @brief 
*/
class AlgorithmSimulator {
 public:
    AlgorithmSimulator(){ };
    void run();
    void registerAlgorithm(TradingAlgorithm *algo, const string& fname);


 private:
    vector<TradingAlgorithm*>   algorithms_;
    
};

} /* EasyQuant */
#endif /* end of include guard: EASYQUANT_ENGINE_ALGORITHMSIMULATOR_H */
