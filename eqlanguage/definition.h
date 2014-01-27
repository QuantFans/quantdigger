#ifndef EQLANGUAG_DEFINITION_H

#define EQLANGUAG_DEFINITION_H

#include <vector>
#include <string>
#include <iostream>
#include <engine/datatype.h>
namespace EQLanguage {
//class TradingAlgorithm;
typedef float Number;
typedef int Int;
typedef float Price;
typedef EasyQuant::DateTime DateTime;
typedef EasyQuant::Time  Time;
typedef std::string Period;
typedef std::vector<Number> NumberList;
typedef std::vector<DateTime> DateTimeList;

template <typename T>
class Series {

 public:
//    friend TradingAlgorithm;

    /**
     * @brief 返回给定偏移的元素。
     *
     * @param i 正数表示左偏移，负数表示右偏移.
     *
     * @return 0: 偏移超出范围； 其它：元素值。
     */
    inline T operator[](int i) {
        int index = curindex_ - i;
        if (index<0 or index>=data_.size()) return 0; // 偏移超出范围
        return data_[index]; 
    }
    inline T operator[](int i) const {
        int index = curindex_ - i;
        if (index<0 or index>=data_.size()) return 0;
        return data_[index]; 
    }

 public:
    /// @todo 让TradingAlgorithm成为友员, 私有化部份接口
    void push_back(T d){ data_.push_back(d); }
    int size() const { return data_.size(); }
    void set_curindex(int index) { curindex_ = index; }
    int curindex() const { return curindex_; }

    
 private:
    std::vector<T> data_;
    int curindex_;
};
typedef Series<Number> NumberSeries;
typedef const Series<Number>& NumberSeriesReference;
typedef Series<DateTime> DateTimeSeries;
typedef Series<DateTime>& DateTimeSeriesReference;

} /* EQLanguage */
#endif /* end of include guard: EQLANGUAG_DEFINITION_H */
