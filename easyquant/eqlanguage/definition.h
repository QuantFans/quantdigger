#ifndef EASYQUANT_EQLANGUAG_DEFINITION_H

#define EASYQUANT_EQLANGUAG_DEFINITION_H

#include <vector>
#include <string>
#include <iostream>
#include <easyquant/engine/datatype.h>
#include <easyquant/engine/series.h>
namespace EQLanguage {
typedef float Number;
typedef int Int;
typedef float Price;
typedef EasyQuant::DateTime DateTime;
typedef EasyQuant::Time  Time;
typedef std::string Period;
typedef std::vector<Number> NumberList;
typedef std::vector<DateTime> DateTimeList;

typedef EasyQuant::Series<Number> NumberSeries;
typedef const EasyQuant::Series<Number>& NumberSeriesReference;
typedef EasyQuant::Series<DateTime> DateTimeSeries;
typedef EasyQuant::Series<DateTime>& DateTimeSeriesReference;

} /* EQLanguage */
#endif /* end of include guard: EASYQUANT_EQLANGUAG_DEFINITION_H */
