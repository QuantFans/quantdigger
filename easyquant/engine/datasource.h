#ifndef EASYQUANT_ENGINE_DATASOURCE_H

#define EASYQUANT_ENGINE_DATASOURCE_H
#include <string>
#include <vector>
#include <iostream>
#include "datatype.h" 
namespace EasyQuant {

/**
 * @brief k线历史数据结构   
 *
 */
struct HistoryData {
    void resize(int n){
        dt.resize(n);
        open.resize(n);
        close.resize(n);
        high.resize(n);
        low.resize(n);
        vol.resize(n);
    }
    vector<DateTime>    dt;                        ///< 时间 
    vector<Price>       open;
    vector<Price>       close;
    vector<Price>       high;
    vector<Price>       low;
    vector<Price>       vol;
};

/**
 * @brief 开仓信号信息
 */
struct OrderSignal {
    OrderSignal(DateTime en_dt, Price en_p, DateTime ex_dt, Price ex_p) {
        entry_dt = en_dt;
        entry_price = en_p;
        exit_dt = ex_dt;
        exit_price = ex_p;
    }
    DateTime    entry_dt;
    Price       entry_price;
    DateTime    exit_dt;
    Price       exit_price;
};
typedef vector<OrderSignal> OrderSignalVec;
    
std::ostream& operator<<(std::ostream& out, const HistoryData& t);
std::ostream& operator<<(std::ostream& out, const OrderSignalVec& t);
/**
* @brief 
*/
class DataSource {
 public:

    DataSource(string history_data_fname, string order_signal_fname) {
        load_history_data(history_data_fname);
        load_order_signal(order_signal_fname);
    };
    DataSource(){ }

    /** @brief 从文件中读取k线历史数据 */
    bool load_history_data(string fname);
    /** @brief 从文件种读取开平仓信号 */
    bool load_order_signal(string fname);

    HistoryData& history_data() { return history_data_; }
    OrderSignalVec& order_signals() { return order_signals_; }


 private:
    HistoryData history_data_;
    OrderSignalVec order_signals_;

};



}; /* EasyQuant */
#endif /* end of include guard: EASYQUANT_ENGINE_DATASOURCE_H */
