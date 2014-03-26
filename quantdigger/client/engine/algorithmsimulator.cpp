#include "algorithmsimulator.h" 
#include <quantdigger/util/csv.h>
#include <cassert>
#include <fstream>
#include "tradingalgorithm.h"
namespace QuantDigger {

bool AlgorithmSimulator::InstrumentPeriodInfo::loadHistoryData(const string &src) {
    std::ifstream file(src);
    auto iter = CSVIterator(file);
    ++iter;
    while(iter != CSVIterator()) {
        history_data.dt.push_back((*iter)[0]);
        history_data.open.push_back(::atof((*iter)[1].c_str()));
        history_data.close.push_back(::atof((*iter)[2].c_str()));
        history_data.high.push_back(::atof((*iter)[3].c_str()));
        history_data.low.push_back(::atof((*iter)[4].c_str()));
        history_data.vol.push_back(::atof((*iter)[5].c_str()));
        ++iter;
    }
    return true;
}
    
void AlgorithmSimulator::
InstrumentPeriodInfo::handleTickData(const TickData& data) {
    // update instrument_period2curbar
//    Time time;
//    if (toAddNewBar(time)) {
////        datetime.push_back((*iter)[0]);
////        open.push_back(::atof((*iter)[1].c_str()));
////        close.push_back(::atof((*iter)[2].c_str()));
////        high.push_back(::atof((*iter)[3].c_str()));
////        low.push_back(::atof((*iter)[4].c_str()));
////        vol.push_back(::atof((*iter)[5].c_str()));
//        curbar += 1;
//        updateBarIndex(curbar); 
//    // lastbar_time_ = ?
//    } else {
//        // update close
//        // update vol
//    }
}

inline bool AlgorithmSimulator::
InstrumentPeriodInfo::toAddNewBar(const DateTime &datetime) {

}

void AlgorithmSimulator::handleTickData(const vector<TickData> &data) {
}

bool AlgorithmSimulator::loadHistoryData(const string &instrument_period) {
    InstrumentPeriodInfo value;
    value.name = instrument_period;
    value.loadHistoryData(instrument_period);
    insp_infos_.insert(make_pair(instrument_period, value));
}

void AlgorithmSimulator::registerAlgorithm(const string& instrument_period, 
                                           TradingAlgorithm *algo) {
    auto iter = insp_infos_.find(instrument_period);
    // 保证之前已经调用loadHistoryData加载了历史数据.
    assert(iter == insp_infos_.end());
    iter->second.algorithms.push_back(algo);
}

const HistoryData& AlgorithmSimulator::getHistoryData(const string &instrument_period) {
    auto iter = insp_infos_.find(instrument_period);
    // 保证之前已经调用loadHistoryData加载了历史数据.
    assert(iter == insp_infos_.end());
    return iter->second.history_data;
}

void AlgorithmSimulator::run() {
    // 遍历特定周期的合约
    for(auto &t: insp_infos_){
        auto &insp_info = t.second;
        // 遍历每根bar
         for (int i = 0; i < insp_info.history_data.size(); i++) {
             // 更新该周期合约当前bar的索引
             insp_info.history_data.updateBarIndex(i);
             // 遍历算法
             for (auto iter = insp_info.algorithms.begin(); 
                     iter != insp_info.algorithms.end(); iter++) {
                 // 对当前bar运行策略
                 (*iter)->handleCurrentBar();
             }
         }
    }
}

void fn() {
    AlgorithmSimulator simulator;
    string instrument_p;
    simulator.loadHistoryData(instrument_p);
//    TradingAlgorithm algo(simulator, instrument_p);
}

} /* QuantDigger */
