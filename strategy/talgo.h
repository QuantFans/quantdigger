#ifndef STRATEGY_TALGO_H

#define STRATEGY_TALGO_H
#include <engine/tradingalgorithm.h>
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
#endif /* end of include guard: STRATEGY_TALGO_H */
