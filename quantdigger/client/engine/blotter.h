#ifndef QuantDigger_ENGINE_BLOTTER_H

#define QuantDigger_ENGINE_BLOTTER_H
#include "datatype.h" 
#include <vector>
#include <string>
#include "order.h"
namespace QuantDigger {
    
/**
* @brief 
*/
class Blotter {
 public:
    Blotter(){ };

    void order(int amount, float limit_price=0, float stop_price=0);
    void set_datetime(const DateTime &dt) { datetime_ = dt; }
    void set_max_limit(int m) { max_limit_ = m; }

 private:
    inline Order createOrder(int amount, float limit_price=0, float stop_price=0) const;

 private:
    hash_map<int, Order>        orders_;
    hash_map<int, Order>        open_orders_;
    std::vector<Order>          new_orders_;
    DateTime                    datetime_;
    /** @brief 订单量的最大上限制 
    * 可用来防止错误的大量下单，或则超过该品种的总量
    */
    int                         max_limit_; 
};

} /* QuantDigger */
#endif /* end of include guard: QuantDigger_ENGINE_BLOTTER_H */
