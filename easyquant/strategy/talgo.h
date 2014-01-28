#ifndef EASYQUANT_STRATEGY_TALGO_H

#define EASYQUANT_STRATEGY_TALGO_H
#include <easyquant/engine/tradingalgorithm.h>
namespace EasyQuant {
    
/**
* @brief 
*/
class TAlgo : public TradingAlgorithm {

 public:
    TAlgo(){ };
    virtual ~TAlgo(){ };

 private:
    void ExcuteAlgorithm();

};



} /* EasyQuant */
#endif /* end of include guard: EASYQUANT_STRATEGY_TALGO_H */
