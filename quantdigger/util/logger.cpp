#include "logger.h" 
namespace QuantDigger {
    
Logger& singleton_logger()
{
    static Logger instance;
    return instance;
}
} /* QuantDigger */
