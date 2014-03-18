#ifndef QuantDigger_STRATEGY_TALGO_H

#define QuantDigger_STRATEGY_TALGO_H
#include <quantdigger/client/engine/tradingalgorithm.h>
namespace QuantDigger {
    
/**
* @brief 
*/
class TAlgo : public TradingAlgorithm {

 public:
    TAlgo(AlgorithmSimulator& simulator, const string& instrument_period)
            : TradingAlgorithm(simulator, instrument_period){ };
    virtual ~TAlgo(){ };

 private:
    void excuteAlgorithm();

};



} /* QuantDigger */
#endif /* end of include guard: QuantDigger_STRATEGY_TALGO_H */
