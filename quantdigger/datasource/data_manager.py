# -*- coding:utf-8 -*-  
import time
from pymongo import MongoClient
import pandas as pd

class Min(object):
    count = 0
    t = 0                             # unix time with ms
    ct ='0'                            # contract
    o = 0                            # open price
    h =0                             # high price
    c =0                             # close price
    l= 999999999              # low price
    v = 0                            # vol
    ticks = {}
    def clear(self):
        self.count =0
        self.t = 0
        self.c =0
        self.o =0
        self.v = 0
        self.l = 999999999
        self.h = 0
        self.ct = '0'
        self.ticks = {}
        
    def addToTicks(self, simpleTick):
        length = len(self.ticks)
        self.ticks[str(length)] = simpleTick.__dict__

    def update(self, tick):
        if self.count == 0 :
            self.t = tick.t
            self.o = tick.o
            self.ct = tick.ct
        self.c = tick.o
        self.h = (self.h if self.h > tick.o else tick.o)
        self.l = (self.l if self.l < tick.o else tick.o)
        self.v += tick.v
        self.count += 1
        self.addToTicks(SimpleTick(tick))
        
    def toTicksDict(self):
        d = {'t' : self.t , 'ct' : self.ct}
        d.update(self.ticks)
        return d
                  
    def save(self, client, db):
        minDoc = dict(t=self.t, ct=self.ct, o=self.o, h = self.h, l = self.l, c = self.c, v = self.v);        
        
        db['mins'].insert_one(minDoc) 
        
        d = self.toTicksDict()
        db['ticks'].insert_one(d)
        print 'save min...'

class HalfHour(object):
    count = 0
    t = 0                             # unix time with ms
    ct ='0'                          # contract
    o = 0                            # open price
    h =0                             # high price
    c =0                             # close price
    l= 999999999              # low price
    v = 0                            # vol 
    
    def clear(self):
        self.count = 0
        self.t = 0                             # unix time with ms
        self.ct ='0'                          # contract
        self.o = 0                            # open price
        self.h =0                             # high price
        self.c =0                             # close price
        self.l= 999999999              # low price
        self.v = 0                            # vol 
    
    def update(self, min) :
        if self.count == 0 :
            self.t = min.t
            self.ct = min.ct
            self.o = min.o
        self.c = min.c
        self.h = (self.h if self.h > min.h else min.h)
        self.l = (self.l if self.l < min.l else min.l)
        self.v += min.v
        self.count += 1
    
    def save(self, client, db):
        d = {}
        self.__dict__['count']
        d.update(self.__dict__)
        del d['count']
        db['halfhours'].insert_one(d)

class Tick(object):
    t = 0                             # unix time with ms
    ct ='0'                          # contract
    o = 0                            # open price
    v = 0                            # vol
    
class SimpleTick(object):
    def __init__(self, tick):       
       self.o = tick.o
       self.v = tick.v
    
def isSameMin(ta, tb):
    return (abs(ta-tb) < 60000) and (int(ta / 60000) == int(tb / 60000)) 

def isSameHalfHour(ta, tb):
    return (abs(ta-tb) < 1800000) and (int(ta / 1800000) == int(tb / 1800000)) 

# filepath: data file 
def import_data(filepath):
    d = pd.read_csv(filepath)    
    client = MongoClient()
    db = client['test']
    minData = Min()
    halfHourData = HalfHour()
       
    for index in range(len(d)) :
        print index
        tick = Tick()
        tick.ct = d.iloc[index]['code']
        tick.t = time.mktime(time.strptime(d.iloc[index]['datetime'], '%Y-%m-%d %H:%M:%S')) * 1000
        tick.o = d.iloc[index]['price']
        tick.v = d.iloc[index]['vol']
        
        tag = (minData.count == 0 or isSameMin(minData.t, tick.t))
       
#        if isSameMin(minData.t, tick.t) == False:
#            print 'ta: ', str(minData.t), 'tb: ', str(tick.t)
        if  tag:
            minData.update(tick)
#            print 'update min data, count= ' , minData.count
#            print 'isSameMin= ' , isSameMin(minData.t, tick.t) , 'ta= ' , minData.t/1000, 'tb= ' , tick.t/1000
        else :
            minData.save(client, db)
            if halfHourData.count == 0 or isSameHalfHour(halfHourData.t, minData.t):
                halfHourData.update(minData)
            else :
                halfHourData.save(client, db)
                halfHourData.clear()
                halfHourData.update(minData)
            minData.clear()
            minData.update(tick)

# begin_time, end_time: unix time with ms
def get_data(contract, kline, begin_time, end_time):
    client = MongoClient()
    db = client['test']
    result = db[kline].find({'ct' : str(contract), 't' : {'$gte' : begin_time, '$lte' : end_time}})
    rows = []
    for res in result :
        rows.append(res)
    return rows

# example for importing data
filepath = 'if1508.csv'
import_data(filepath);

# example for reading data
#rows = get_data('0', 'mins', 1340084340000,  1340094340000)




