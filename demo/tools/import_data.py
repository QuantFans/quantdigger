from quantdigger import locd, set_config
from quantdigger.datasource import import_data

set_config({ 'data_path': '../data', 'source': 'csv'})
import_data(['../work/AA.SHFE-1.Minute.csv', '../work/BB.SHFE-1.Minute.csv', '../work/BB.SHFE-1.Day.csv'], locd)

set_config({ 'data_path': '../data', 'source': 'sqlite'})
import_data(['../work/AA.SHFE-1.Minute.csv', '../work/BB.SHFE-1.Minute.csv', '../work/BB.SHFE-1.Day.csv'], locd)
