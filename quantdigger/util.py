from logbook import Logger
import time

engine_logger = Logger('engine')
data_logger = Logger('data')

def time2int(t):
     """ datetime to int  """
     epoch =  int(time.mktime(t.timetuple())*1000)
     return epoch
