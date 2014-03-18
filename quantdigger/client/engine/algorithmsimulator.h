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

    void run();

    /** @brief 添加策略，及历史数据 */
    void registerAlgorithm(const string& fname, TradingAlgorithm *algo);

    /** @brief 基于历史数据的策略入口 */
    void excuteHistoryData();

    /**
     * @brief 处理tick数据
     *
     * 决定是否合成新的bar数据，以及调用注册的策略集
     * @param data
     */
    void handleTickData(const vector<TickData> &data);

    /** @brief 更新当前bar的索引 */
    inline void updateBarIndex(int curindex);

    /** @brief tick数据来的时候判断是否需要增加新的Bar */
    inline bool toAddNewBar(const DateTime &datetime);

    /** @brief 从文件中加载数据 */
    bool loadHistoryData(const string &instrument_period);
    const HistoryData& getHistoryData(const string &instrument_period);

 private:

    vector<TradingAlgorithm*>   algorithms_;
    hash_map<string, vector<TradingAlgorithm*> > instrument_period2algos_; ///< 特定周期的合约到策略的映射
    hash_map<string, HistoryData> instrument_period2data_; ///< 特定周期的合约到历史数据的映射
    hash_map<string, BarData> instrument_period2curbar; ///< 特定周期的合约到当前bar的映射

    
};

} /* QuantDigger */
#endif /* end of include guard: QuantDigger_ENGINE_ALGORITHMSIMULATOR_H */
