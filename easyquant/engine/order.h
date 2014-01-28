#ifndef EASYQUANT_ENGINE_ORDER_H

#define EASYQUANT_ENGINE_ORDER_H
#include <string>
namespace EasyQuant {
    
enum OrderStatus {
    kOpen,
    kFilled,
    kCancelled
};

enum OrderDirection {
    kBull,        ///< 多头 
    kBear         ///< 空头 
};

/**
* @brief 订单信息
*/
class Order {
 public:
    Order(){ };

 private:
    int             id_;  ///< 订单编号 
    std::string     dt_;  ///< 时间 
    int             instrument_id_; ///< 品种编号 
    int             amount_;
    OrderDirection  direction_;
};


} /* EasyQuant */
#endif /* end of include guard: EASYQUANT_ENGINE_ORDER_H */
