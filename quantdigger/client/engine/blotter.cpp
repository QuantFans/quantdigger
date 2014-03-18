#include "blotter.h"
#include <utility>
#include <quantdigger/util/logger.h>

namespace QuantDigger {
extern int g_requestId;
static auto &logger = singleton_logger();

void Blotter::order(int amount, float limit_price, float stop_price) {
        if (amount <=  0) {
            logger.log(WARN, "订单数量没大于0!");    
            return;
        } else if (amount > max_limit_) {
            logger.log(WARN, "订单数量超过限制!");    
            return;
        }
        Order order = createOrder(amount, limit_price, stop_price);
        new_orders_.push_back(order);
        orders_.insert(std::make_pair(order.id, order));
        open_orders_.insert(std::make_pair(order.id, order));
}

inline Order Blotter::createOrder(int amount, float limit_price, float stop_price) const {

}

} /* QuantDigger */
