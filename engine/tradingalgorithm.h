#ifndef ENGINE_TRADINGALGORITHM_H
#define ENGINE_TRADINGALGORITHM_H

#include "datasource.h"
#include <eqlanguage/definition.h>
#include "datatype.h"


namespace EasyQuant {
class Blotter;
    

/**
* @brief 
*/
class TradingAlgorithm {
 public:
    TradingAlgorithm(){ };
    virtual ~TradingAlgorithm(){ };

    /** @brief 基于历史数据的策略入口 */
    void InitialData();

    /** @brief 基于实时数据的策略入口 */
    void HandleTickData(TickData data);

    /** @brief 从网络中加载数据 */
    void set_history_data(){ }

    /** @brief 从文件中加载数据 */
    bool load_history_data(const string &fname);

    void set_datetime(const DateTime &dt) { datetime_ = dt; }


 protected:

    /** @brief 更新当前bar的索引 */
    inline void UpdateBarIndex(int curindex);

    /** @brief tick数据来的时候判断是否需要增加新的Bar */
    inline bool ToAddNewBar(const DateTime &datetime);

    /** @brief 对单根Bar运行策略 */
    virtual void ExcuteAlgorithm() = 0;

    /**@name 用户策略算法可见:
     * @{ */
    inline void order(EQLanguage::Number amount, 
                      EQLanguage::Number limit_price=0,
                      EQLanguage::Number stop_price=0);
    EQLanguage::DateTimeSeries     datetime;
    EQLanguage::NumberSeries       open;
    EQLanguage::NumberSeries       close;
    EQLanguage::NumberSeries       high;
    EQLanguage::NumberSeries       low;
    EQLanguage::NumberSeries       vol;
    EQLanguage::Period             period;
    int                            curbar;
    /**@} */
 private:
    Time     lastbar_time_;  ///< 最后一根Bar的创建时间
    Blotter  *blotter;       ///< 订单处理中心
    DateTime    datetime_;
    
};



} /* EasyQuant */

#endif /* end of include guard: ENGINE_TRADINGALGORITHM_H */
