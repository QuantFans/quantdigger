#ifndef QuantDigger_ENGINE_DATATYPE_H

#define QuantDigger_ENGINE_DATATYPE_H

#include <map>
#include <string>
#include <set>
namespace QuantDigger {
using namespace std;
    
typedef string DateTime;
typedef string Time;
typedef float TickData;
typedef float Price;
typedef int Volume;
/// @todo replace map/set with boost::hash_map/boost::hash_set
#define hash_map map
#define hash_set set

} /* QuantDigger */

#endif /* end of include guard: QuantDigger_ENGINE_DATATYPE_H */
