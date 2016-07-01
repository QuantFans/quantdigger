from quantdigger import ConfigUtil
from quantdigger.datasource import import_data, ds_impl

csv_ds = ds_impl.csv_source.CsvSource('../data')
import_data(['../work/AA.SHFE-1.Minute.csv',
             '../work/BB.SHFE-1.Minute.csv',
             '../work/BB.SHFE-1.Day.csv'],
            csv_ds)

sqlite_ds = ds_impl.sqlite_source.SqliteSource('../data/digger.db')
import_data(['../work/AA.SHFE-1.Minute.csv',
             '../work/BB.SHFE-1.Minute.csv',
             '../work/BB.SHFE-1.Day.csv'],
            sqlite_ds)
