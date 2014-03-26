#ifndef QuantDigger_ENGINE_ALGORITHMSIMULATOR_H

#define QuantDigger_ENGINE_ALGORITHMSIMULATOR_H
#include <vector>
#include <string>
#include "datasource.h" 
#include "datatype.h" 
#include <quantdigger/client/qdlanguage/definition.h>

namespace QuantDigger {
class TradingAlgorithm;
using std::vector;
using std::string;
    
/**
* @brief 
*/
class AlgorithmSimulator {
 public:
    AlgorithmSimulator(){ };

    /** @brief 基于历史数据的策略入口 */
    void run();

    /** @brief 添加策略，及历史数据 */
    void registerAlgorithm(const string& fname, TradingAlgorithm *algo);

    void handleTickData(const vector<TickData> &data);

    /** @brief 从文件中加载数据 */
    bool loadHistoryData(const string &instrument_period);
    const HistoryData& getHistoryData(const string &instrument_period);

 private:
    /**
    * @brief 特定周期的合约信息
    */
    struct InstrumentPeriodInfo {
        /**
         * @brief 处理tick数据
         *
         * 决定是否合成新的bar数据，以及调用注册的策略集
         * @param data
         */
        void handleTickData(const TickData& data);

        /** @brief tick数据来的时候判断是否需要增加新的Bar */
        inline bool toAddNewBar(const DateTime &datetime);

        bool loadHistoryData(const string &src);

        string name;
        vector<TradingAlgorithm*> algorithms;  ///< 策略集合
        HistoryData history_data;               ///< 历史数据
        BarData curbar;                        ///< 当前Bar数据
    };

    vector<TradingAlgorithm*>   algorithms_;
    hash_map<string, InstrumentPeriodInfo> insp_infos_;
};

} /* QuantDigger */
#endif /* end of include guard: QuantDigger_ENGINE_ALGORITHMSIMULATOR_H */
