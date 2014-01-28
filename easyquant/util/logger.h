#ifndef UTIL_LOGGER_H

#define UTIL_LOGGER_H

#ifndef WINDOWS
#include <easyquant/thirdparty/Logger.h>
#define ERROR opencog::Logger::ERROR
#define NONE opencog::Logger::NONE
#define WARN opencog::Logger::WARN
#define INFO opencog::Logger::INFO
#define DEBUG opencog::Logger::DEBUG
#define FINE opencog::Logger::FINE
#define BAD_LEVEL opencog::Logger::BAD_LEVEL
#define Level opencog::Logger::Level
#else
enum Level { NONE, ERROR, WARN, INFO, DEBUG, FINE, BAD_LEVEL=255 };
#endif
namespace EasyQuant {
    
/**
* @brief 
*/
class Logger {
 public:

    Logger() { }


    /**
     * Reset the level of messages which will be logged. Every message with
     * log-level lower than or equals to newLevel will be logged.
     */
    void setLevel(Level level) { 
#ifndef WINDOWS
        logger_.setLevel(level);
#endif
    }

    /**
     * Get the current log level that determines which messages will be
     * logged: Every message with log-level lower than or equals to returned
     * level will be logged.
     */
    Level getLevel() const { 
#ifndef WINDOWS
        return logger_.getLevel( );
#endif
        return NONE;
    }

    /**
     * Set the level of messages which should be logged with back trace. 
     * Every message with log-level lower than or equals to the given argument
     * will have back trace.
     */
    void setBackTraceLevel(Level level) { 
#ifndef WINDOWS
        logger_.setBackTraceLevel(level);
#endif
    }

    /**
     * Get the current back trace log level that determines which messages
     * should be logged with back trace. 
     */
    Level getBackTraceLevel() const { 
#ifndef WINDOWS
        return logger_.getBackTraceLevel();
#endif
        return NONE;
    }

    /* filename property */
    void setFilename(const std::string& fname) { 
#ifndef WINDOWS
        logger_.setFilename(fname);
#endif
    }
    const std::string& getFilename() { 
#ifndef WINDOWS
        return logger_.getFilename();
#endif
        return std::string("");
    }

    /**
     * Reset the flag that indicates whether a timestamp is to be prefixed
     * in every message or not.
     */
    void setTimestampFlag(bool flag) { 
#ifndef WINDOWS
        logger_.setTimestampFlag(flag);
#endif
    }

    /**
     * Reset the flag that indicates whether the log messages should be
     * printed to the stdout or not.
     */
    void setPrintToStdoutFlag(bool flag) { 
#ifndef WINDOWS
        logger_.setPrintToStdoutFlag(flag);
#endif
    }

    /**
     * Set the main logger to print only
     * error level log on stdout (useful when one is only interested
     * in printing cassert logs)
     */
    void setPrintErrorLevelStdout() { 
#ifndef WINDOWS
        logger_.setPrintErrorLevelStdout();
#endif
    }

    /**
     * Log a message into log file (passed in constructor) if and only
     * if passed level is lower than or equal to the current log level
     * of this Logger instance.
     */
    void log(Level level, const std::string &txt) { 
#ifndef WINDOWS
        logger_.log(level, txt);
#endif
    }
    // void error(const std::string &txt);
    // void warn (const std::string &txt);
    // void info (const std::string &txt);
    // void debug(const std::string &txt);
    // void fine (const std::string &txt);

    /**
     * Log a message (printf style) into log file (passed in constructor)
     * if and only if passed level is lower than or equals to the current
     * log level of this Logger instance.
     *
     * You may use these methods as any printf-style call, eg: 
     * fine("Count = %d", count)
     */
    void logva(Level level, const char *t, va_list args) { 
#ifndef WINDOWS
        logger_.logva(level, t, args);
#endif
    }
//    void log  (Level level, const char *t, ...) { 
//#ifndef WINDOWS
//        logger_.log(level, t, ...);
//#endif
//    }
 private:
#ifndef WINDOWS
    opencog::Logger logger_;
#endif
    /* data */
};

Logger& singleton_logger();

} /* EasyQuant */
#endif /* end of include guard: UTIL_LOGGER_H */
