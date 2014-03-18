#ifndef QuantDigger_EQLANGUAG_DEFINITION_H

#define QuantDigger_EQLANGUAG_DEFINITION_H

#include <vector>
#include <string>
#include <iostream>
#include <quantdigger/client/engine/datatype.h>
#include <quantdigger/client/engine/series.h>
namespace QDLanguage {
typedef float Number;
typedef int Int;
typedef QuantDigger::Price Price;
typedef QuantDigger::Volume Volume;
typedef QuantDigger::DateTime DateTime;
typedef QuantDigger::Time  Time;
typedef std::string Period;
typedef std::vector<Number> NumberArray;
typedef std::vector<DateTime> DateTimeArray;

typedef QuantDigger::Series<Number> NumberSeries;
typedef const QuantDigger::Series<Number>& NumberSeriesReference;
typedef QuantDigger::Series<DateTime> DateTimeSeries;
typedef QuantDigger::Series<DateTime>& DateTimeSeriesReference;

} /* QDLanguage */
#endif /* end of include guard: QuantDigger_EQLANGUAG_DEFINITION_H */
