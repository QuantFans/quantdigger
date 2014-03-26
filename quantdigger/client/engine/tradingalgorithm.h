#ifndef QuantDigger_ENGINE_TRADINGALGORITHM_H
#define QuantDigger_ENGINE_TRADINGALGORITHM_H

#include "algorithmsimulator.h"
#include <quantdigger/client/qdlanguage/definition.h>
#include "datatype.h"
#include "datasource.h"


namespace QuantDigger {
class Blotter;
    

/**
* @brief 
*/
class TradingAlgorithm {
 public:
    TradingAlgorithm(AlgorithmSimulator &sim, const string& instrument_period) 
            : curbar(0),
              datetime(sim.getHistoryData(instrument_period).dt), 
              open(sim.getHistoryData(instrument_period).open), 
              close(sim.getHistoryData(instrument_period).close), 
              high(sim.getHistoryData(instrument_period).high), 
              low(sim.getHistoryData(instrument_period).low), 
              vol(sim.getHistoryData(instrument_period).vol), 
              period(sim.getHistoryData(instrument_period).period) { 
        //
        sim.registerAlgorithm(instrument_period, this);
    };
    virtual ~TradingAlgorithm(){ };

    /** @brief 基于实时数据的策略入口 */
    void handleTickData(const BarData &data);

    void set_datetime(const DateTime &dt) { datetime_ = dt; }

    /** @brief 对单根Bar运行策略 */
    virtual void handleCurrentBar() = 0;

 protected:

    /**@name 用户策略算法可见:
     * @{ */
    inline void order(QDLanguage::Number amount, 
                      QDLanguage::Number limit_price=0,
                      QDLanguage::Number stop_price=0);

    const QDLanguage::DateTimeSeries     &datetime;
    const QDLanguage::NumberSeries       &open;
    const QDLanguage::NumberSeries       &close;
    const QDLanguage::NumberSeries       &high;
    const QDLanguage::NumberSeries       &low;
    const QDLanguage::NumberSeries       &vol;
    const QDLanguage::Period             &period;
    int                                  curbar;      ///< 当前bar的索引，从0开始。
    /**@} */
 private:
    Blotter  *blotter;       ///< 订单处理中心
    DateTime    datetime_;
    
};



} /* QuantDigger */

#endif /* end of include guard: QuantDigger_ENGINE_TRADINGALGORITHM_H */
