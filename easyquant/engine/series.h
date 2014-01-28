#ifndef EASYQUANT_ENGINE_SERIES_H

#define EASYQUANT_ENGINE_SERIES_H

namespace EasyQuant {
class TradingAlgorithm;
    
template <typename T>
class Series {

 public:
//    friend TradingAlgorithm;
    inline operator T() { return data_[curindex_]; }

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

 private:
    /// @todo 让TradingAlgorithm成为友员, 私有化部份接口
    friend class TradingAlgorithm;
    void push_back(T d){ data_.push_back(d); }
    int size() const { return data_.size(); }
    void set_curindex(int index) { curindex_ = index; }
    int curindex() const { return curindex_; }

    
 private:
    std::vector<T> data_;
    int curindex_;
};
} /* EasyQuant */
#endif /* end of include guard: EASYQUANT_ENGINE_SERIES_H */
