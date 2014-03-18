#include "datasource.h" 
#include <fstream>
#include <quantdigger/util/csv.h>

namespace QuantDigger {
/// @todo @wdj 预先分配空间，加速
bool DataSource::load_history_data(string fname) {
    std::ifstream file(fname);
    auto iter = CSVIterator(file);
    ++iter;
    while(iter != CSVIterator()) {
        history_data_.dt.push_back((*iter)[0]);
        history_data_.open.push_back(::atof((*iter)[1].c_str()));
        history_data_.close.push_back(::atof((*iter)[2].c_str()));
        history_data_.high.push_back(::atof((*iter)[3].c_str()));
        history_data_.low.push_back(::atof((*iter)[4].c_str()));
        history_data_.vol.push_back(::atof((*iter)[5].c_str()));
        ++iter;
    }
}

bool DataSource::load_order_signal(string fname) {
    std::ifstream file(fname);
    auto iter = CSVIterator(file);
    ++iter;
    while(iter != CSVIterator()) {
        order_signals_.push_back(OrderSignal((*iter)[0], 
                                 ::atof((*iter)[1].c_str()), 
                                 (*iter)[2], 
                                 ::atof((*iter)[3].c_str())));
        ++iter;
    }
}

std::ostream& operator<<(std::ostream& out, const HistoryData& d) {
    cout<<"datetime, open, close, high, low, vol"<<endl;
    for (int i = 0; i < d.dt.size(); i++) {
        cout<<d.dt[i]<<","<<d.open[i]<<","
            <<d.close[i]<<","<<d.high[i]<<","
            <<d.low[i]<<","<<d.vol[i]<<endl;
    }
}

std::ostream& operator<<(std::ostream& out, const vector<OrderSignal>& signals) {
    cout<<"entry_datetime, entry_price, exit_datetime, exit_price"<<endl;
    for (int i = 0; i < signals.size(); i++) {
        cout<<signals[i].entry_dt<<","<<signals[i].entry_price<<","
            <<signals[i].exit_dt<<","<<signals[i].exit_price<<endl;
    }
}

}; /* QuantDigger */
