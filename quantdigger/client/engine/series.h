#ifndef QuantDigger_ENGINE_SERIES_H

#define QuantDigger_ENGINE_SERIES_H

namespace QuantDigger {
    
template <typename T>
class Series {

 public:
//    friend TradingAlgorithm;
    inline operator T() const { return data_[curindex_]; }

    /**
     * @brief 返回给定偏移的元素。
     *
     * @param i 正数表示左偏移，负数表示右偏移.
     *
     * @return 0: 偏移超出范围； 其它：元素值。
     */
    inline T operator[](int i) {
        int index = curindex_ - i;
        if (index<0 or index>=data_.size()) return T(); // 偏移超出范围
        cout<<index<<endl;
        return data_[index]; 
    }
    inline T operator[](int i) const {
        int index = curindex_ - i;
        if (index<0 or index>=data_.size()) return T();
        return data_[index]; 
    }

    inline void resize(int n) {
        data_.resize(n);
    }

    void push_back(T d){ data_.push_back(d); }
    int size() const { return data_.size(); }
    void set_curindex(int index) { curindex_ = index; }
    int curindex() const { return curindex_; }
    T at(int index) const {
        if (index >= 0 && index < data_.size()) {
            return data_[index]; 
        } else
            return T();
    }

 private:
    std::vector<T> data_;
    // 当前bar的索引，由于它的数据会被共享，
    int curindex_;
};
} /* QuantDigger */
#endif /* end of include guard: QuantDigger_ENGINE_SERIES_H */
