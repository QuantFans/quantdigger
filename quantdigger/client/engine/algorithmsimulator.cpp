#include "algorithmsimulator.h" 
#include "tradingalgorithm.h"
#include <quantdigger/util/csv.h>
namespace QuantDigger {
    
void AlgorithmSimulator::run() {
    // foreach algorithm
    for(auto *algo : algorithms_) {
//        algo->excuteHistoryData();
    }
}

void AlgorithmSimulator::registerAlgorithm(const string& instrument_period, TradingAlgorithm *algo) {
//    if(data2algo_.insert(make_pair(fname, algo))
}

void AlgorithmSimulator::handleTickData(const vector<TickData> &data) {
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

bool AlgorithmSimulator::loadHistoryData(const string &instrument_period) {
//    std::ifstream file(fname);
//    auto iter = CSVIterator(file);
//    ++iter;
//    auto rst = instrument_period2data_.insert(make_pair(fname, HistoryData()));
//    while(iter != CSVIterator()) {
//        datetime.push_back((*iter)[0]);
//        open.push_back(::atof((*iter)[1].c_str()));
//        close.push_back(::atof((*iter)[2].c_str()));
//        high.push_back(::atof((*iter)[3].c_str()));
//        low.push_back(::atof((*iter)[4].c_str()));
//        vol.push_back(::atof((*iter)[5].c_str()));
//        ++iter;
//    }
}

inline void AlgorithmSimulator::updateBarIndex(int curindex) {
//    datetime.set_curindex(curindex);    
//    open.set_curindex(curindex);    
//    close.set_curindex(curindex);    
//    high.set_curindex(curindex);    
//    low.set_curindex(curindex);    
//
//    vol.set_curindex(curindex);    
//    curbar = curindex;
}

void AlgorithmSimulator::excuteHistoryData() {
//    // 一种简化的验证
//    int s = open.size() + close.size() + high.size() + low.size() + vol.size();
//    assert(datetime.size()*5 == s);
//    //
//    for (int i = 0; i < open.size(); i++) {
//        updateBarIndex(i); 
//        excuteAlgorithm();
//    }
}

const HistoryData& AlgorithmSimulator::getHistoryData(const string &instrument_period) {
    return instrument_period2data_[instrument_period];
}

void fn() {
    AlgorithmSimulator simulator;
    string instrument_p;
    simulator.loadHistoryData(instrument_p);
//    TradingAlgorithm algo(simulator, instrument_p);
}

} /* QuantDigger */
