#ifndef QuantDigger_ENGINE_ORDER_H

#define QuantDigger_ENGINE_ORDER_H
#include <string>
namespace QuantDigger {
    
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


} /* QuantDigger */
#endif /* end of include guard: QuantDigger_ENGINE_ORDER_H */
