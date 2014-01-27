#include "tradingalgorithm.h" 
#include <cassert>
#include <fstream>

#include "blotter.h" 
#include <util/csv.h>

namespace EasyQuant {


bool TradingAlgorithm::load_history_data(const string &fname) {
    std::ifstream file(fname);
    auto iter = CSVIterator(file);
    ++iter;
    while(iter != CSVIterator()) {
        datetime.push_back((*iter)[0]);
        open.push_back(::atof((*iter)[1].c_str()));
        close.push_back(::atof((*iter)[2].c_str()));
        high.push_back(::atof((*iter)[3].c_str()));
        low.push_back(::atof((*iter)[4].c_str()));
        vol.push_back(::atof((*iter)[5].c_str()));
        ++iter;
    }
}

inline void TradingAlgorithm::UpdateBarIndex(int curindex) {
    datetime.set_curindex(curindex);    
    open.set_curindex(curindex);    
    close.set_curindex(curindex);    
    high.set_curindex(curindex);    
    low.set_curindex(curindex);    
    vol.set_curindex(curindex);    
    curbar = curindex;
}

void TradingAlgorithm::InitialData() {
    // 一种简化的验证
    int s = open.size() + close.size() + high.size() + low.size() + vol.size();
    assert(datetime.size()*5 == s);

    // 策略运行的主循环
    for (int i = 0; i < open.size(); i++) {
        UpdateBarIndex(i); 
        ExcuteAlgorithm();
    }
}

void TradingAlgorithm::HandleTickData(TickData data) {
    Time time;
    if (ToAddNewBar(time)) {
//        datetime.push_back((*iter)[0]);
//        open.push_back(::atof((*iter)[1].c_str()));
//        close.push_back(::atof((*iter)[2].c_str()));
//        high.push_back(::atof((*iter)[3].c_str()));
//        low.push_back(::atof((*iter)[4].c_str()));
//        vol.push_back(::atof((*iter)[5].c_str()));
        curbar += 1;
        UpdateBarIndex(curbar); 
    // lastbar_time_ = ?
    } else {
        // update close
        // update vol
    }
    ExcuteAlgorithm();
}


inline bool TradingAlgorithm::ToAddNewBar(const EQLanguage::Time &time) {
    // time, last_bartime_, period
    return false;
}


inline void TradingAlgorithm::order(EQLanguage::Number amount,
                                    EQLanguage::Number limit_price,
                                    EQLanguage::Number stop_price) {
    blotter->order(amount, limit_price, stop_price);
}

}; /* EasyQuant */
