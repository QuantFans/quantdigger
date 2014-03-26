#include "tradingalgorithm.h" 
#include <cassert>
#include <fstream>

#include "blotter.h" 

namespace QuantDigger {
int g_requestId = 0;



void TradingAlgorithm::handleTickData(const BarData &data) {
//    excuteAlgorithm();
}

inline void TradingAlgorithm::order(QDLanguage::Number amount,
                                    QDLanguage::Number limit_price,
                                    QDLanguage::Number stop_price) {
    blotter->order(amount, limit_price, stop_price);
}


}; /* QuantDigger */
