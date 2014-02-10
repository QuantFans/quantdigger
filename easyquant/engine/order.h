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
struct Order {
 public:
    Order(){ };

    int             id;  ///< 订单编号 
    std::string     dt;  ///< 时间 
    int             instrument_id; ///< 品种编号 
    int             amount;
    OrderDirection  direction;
};


} /* EasyQuant */
#endif /* end of include guard: EASYQUANT_ENGINE_ORDER_H */
