#include "logger.h" 
namespace EasyQuant {
    
Logger& singleton_logger()
{
    static Logger instance;
    return instance;
}
} /* EasyQuant */
