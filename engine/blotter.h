#ifndef ENGINE_BLOTTER_H

#define ENGINE_BLOTTER_H
#include "datatype.h" 
#include <vector>
#include <string>
#include "order.h"
namespace EasyQuant {
using namespace std;
    

/**
* @brief 
*/
class Blotter {
 public:
    Blotter(){ };
    void order(int amount, float limit_price=0, float stop_price=0) {
        if (amount <=  0) {
            
        }
    }

    void set_datetime(const DateTime &dt) { datetime_ = dt; }

 private:
    hash_map<string, Order>     orders_;
    vector<Order>               new_orders_;
    DateTime                    datetime_;
};

} /* EasyQuant */
#endif /* end of include guard: ENGINE_BLOTTER_H */
