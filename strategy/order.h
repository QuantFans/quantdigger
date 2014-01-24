#ifndef STRATEGY_ORDER_H

#define STRATEGY_ORDER_H
#include <string>

enum OrderStatus {
    kOpen,
    kFilled,
    kCancelled
};

enum OrderDirection {
    kBull,  ///< 多头
    kBear   ///< 空头
}

/**
* @brief 订单信息
*/
class Order {
 public:
    Order();

 private:
    int     id_;  ///< 订单编号
    string  dt_;  ///< 时间
    int     stock_id_; ///< 品种编号 
    int     amount_;
    OrderDirection direction_;



};


#endif /* end of include guard: STRATEGY_ORDER_H */
