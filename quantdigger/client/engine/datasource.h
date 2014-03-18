#ifndef QuantDigger_ENGINE_DATASOURCE_H

#define QuantDigger_ENGINE_DATASOURCE_H
#include <string>
#include <vector>
#include <iostream>
#include "datatype.h" 
#include <quantdigger/client/qdlanguage/definition.h>
namespace QuantDigger {

/** @brief 单根bar的基本数据 */
struct BarData {
    BarData() {
        open = close = high = low = vol = 0;
    }
    DateTime start_time;
    Price open;
    Price close;
    Price high;
    Price low;
    Volume vol;


};

/** @brief k线历史数据结构 */
struct HistoryData {
    void resize(int n){
        dt.resize(n);
        open.resize(n);
        close.resize(n);
        high.resize(n);
        low.resize(n);
        vol.resize(n);
    }
    QDLanguage::DateTimeSeries dt;
    QDLanguage::NumberSeries   open; 
    QDLanguage::NumberSeries   close; 
    QDLanguage::NumberSeries   high; 
    QDLanguage::NumberSeries   low; 
    QDLanguage::NumberSeries   vol; 
    QDLanguage::Period         period;
    int                        curbar;      ///< 当前bar的索引，从0开始。
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
    
std::ostream& operator<<(std::ostream& out, const HistoryData& t);
std::ostream& operator<<(std::ostream& out, const vector<OrderSignal>& t);
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
    vector<OrderSignal>& order_signals() { return order_signals_; }


 private:
    HistoryData history_data_;
    vector<OrderSignal> order_signals_;

};



}; /* QuantDigger */
#endif /* end of include guard: QuantDigger_ENGINE_DATASOURCE_H */
