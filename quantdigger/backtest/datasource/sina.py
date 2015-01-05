#!/usr/local/bin/python
#coding=utf-8

import os, io, sys, re, time, json, base64
import webbrowser, urllib

#国内股票数据：指数
def get_sina_index_daily(stockCode):
    try:
        exchange = "sz" if (int(stockCode) // 100000 == 3) else "sh"
        #http://hq.sinajs.cn/list=s_sh000001
        dataUrl = "http://hq.sinajs.cn/list=s_" + exchange + stockCode
        stdout = urllib.urlopen(dataUrl)
        stdoutInfo = stdout.read().decode('gb2312')
        tempData = re.search('''(")(.+)(")''', stdoutInfo).group(2)
        stockInfo = tempData.split(",")
        #stockCode = stockCode,
        stockName   = stockInfo[0]
        stockEnd    = stockInfo[1]  #当前价，15点后为收盘价
        stockZD     = stockInfo[2]  #涨跌
        lastPrice   = str(float(stockEnd) - float(stockZD)) #开盘价
        stockFD     = stockInfo[3]  #幅度
        stockZS     = stockInfo[4]  #总手
        stockZS_W   = str(int(stockZS) / 100)
        stockJE     = stockInfo[5]  #金额
        stockJE_Y   = str(int(stockJE) / 10000)
        content = "#" + stockName + "#" + "(" + str(stockCode) + ")" + u" 收盘：" \
          + stockEnd + u"，涨跌：" + stockZD + u"，幅度：" + stockFD + "%" \
          + u"，总手：" + stockZS_W + u"万" + u"，金额：" + stockJE_Y + u"亿" + "  "

        #imgPath = "http://image.sinajs.cn/newchart/" + period + "/n/" + exchange + str(stockCode) + ".gif"
        

    except Exception as e:
        print(">>>>>> Exception: " + str(e))
    else:
        return content
    finally:
        None

#国内股票数据：个股
def get_sina_stock_daily(stockCode):
    try:
        exchange = "sh" if (int(stockCode) // 100000 == 6) else "sz"
        dataUrl = "http://hq.sinajs.cn/list=" + exchange + stockCode
        stdout = urllib.urlopen(dataUrl)
        stdoutInfo = stdout.read().decode('gb2312')
        tempData = re.search('''(")(.+)(")''', stdoutInfo).group(2)
        stockInfo = tempData.split(",")
        #stockCode = stockCode,
        stockName   = stockInfo[0]  #名称
        stockStart  = stockInfo[1]  #开盘
        stockLastEnd= stockInfo[2]  #昨收盘
        stockCur    = stockInfo[3]  #当前
        stockMax    = stockInfo[4]  #最高
        stockMin    = stockInfo[5]  #最低
        stockUp     = round(float(stockCur) - float(stockLastEnd), 2)
        stockRange  = round(float(stockUp) / float(stockLastEnd), 4) * 100
        stockVolume = round(float(stockInfo[8]) / (100 * 10000), 2)
        stockMoney  = round(float(stockInfo[9]) / (100000000), 2)
        stockTime   = stockInfo[31]

        content = "#" + stockName + "#(" + stockCode + ")" + u" 开盘:" + stockStart \
        + u",最新:" + stockCur + u",最高:" + stockMax + u",最低:" + stockMin \
        + u",涨跌:" + str(stockUp) + u",幅度:" + str(stockRange) + "%" \
        + u",总手:" + str(stockVolume) + u"万" + u",金额:" + str(stockMoney) \
        + u"亿" + u",更新时间:" + stockTime + "  "

        #imgUrl = "http://image.sinajs.cn/newchart/" + period + "/n/" + exchange + str(stockCode) + ".gif"
        

    except Exception as e:
        print(">>>>>> Exception: " + str(e))
    else:
        return content
    finally:
        None

#全球股票指数
def get_yahoo_daily(stockDict):
    try:
        #http://download.finance.yahoo.com/d/quotes.csv?s=^IXIC&f=sl1c1p2l
        yahooCode = stockDict['yahoo']
        dataUrl = "http://download.finance.yahoo.com/d/quotes.csv?s=" + yahooCode + "&f=sl1c1p2l"

        stdout = urllib.urlopen(dataUrl)
        stdoutInfo = stdout.read().decode('gb2312')
        tempData = stdoutInfo.replace('"', '')
        stockInfo = tempData.split(",")
        #stockNameCn = stockDict['name']['chinese']
        #stockNameEn = stockDict['name']['english']
        stockCode   = stockDict['code']
        stockEnd    = stockInfo[1]  #当前价，5点后为收盘价
        stockZD     = stockInfo[2]  #涨跌
        lastPrice   = str(float(stockEnd) - float(stockZD)) #开盘价
        stockFD     = stockInfo[3]  #幅度
        #percent     = float(stockFD.replace("%", ""))
        matchResult = re.search("([\w?\s?:]*)(\-)", stockInfo[4])  #日期和最新值
        stockDate   = matchResult.group(1)

        content =  "(" + stockCode + ")" \
          + u" 当前：" + stockEnd + u", 涨跌：" + stockZD + u", 幅度：" + stockFD \
          + u", 最后交易时间：" + stockDate

    except Exception as err:
        print(">>>>>> Exception: " + yahooCode )
        print "error: "  +  str(err)
    else:
        return content
    finally:
        None
#--------------------------------------------------------------------------------------------------------
chinaIndex = [
    "000001", # sh000001 上证指数
    "399001", # sz399001 深证成指
    "000300", # sh000300 沪深300
    "399005", # sz399005 中小板指
    "399006", # sz399006 创业板指
    "000003",  # sh000003 B股指数
]
worldIndex = [
    {'code':"000001", 'yahoo':"000001.SS",'name':{'chinese':u"中国上证指数", 'english':"CHINA SHANGHAI COMPOSITE INDEX"}},
    {'code':"399001", 'yahoo':"399001.SZ",'name':{'chinese':u"中国深证成指", 'english':"SZSE COMPONENT INDEX"}},
    {'code':"DJI", 'yahoo':"^DJI",'name':{'chinese':u"美国道琼斯工业平均指数", 'english':"Dow Jones Industrial Average"}},
    {'code':"IXIC", 'yahoo':"^IXIC",'name':{'chinese':u"美国纳斯达克综合指数", 'english':"NASDAQ Composite"},},
    {'code':"GSPC", 'yahoo':"^GSPC",'name':{'chinese':u"美国标准普尔500指数", 'english':"S&P 500"}},
    {'code':"N225", 'yahoo':"^N225",'name':{'chinese':u"日本日经225指数", 'english':"NIKKEI 225"}},
    {'code':"TWII", 'yahoo':"^TWII",'name':{'chinese':u"台湾台北加权指数", 'english':"TSEC weighted index"}},
    {'code':"HSI", 'yahoo':"^HSI",'name':{'chinese':u"香港恒生指数", 'english':"HANG SENG INDEX"}},
    {'code':"FCHI", 'yahoo':"^FCHI",'name':{'chinese':u"法国CAC40指数", 'english':"CAC 40"}},
    {'code':"FTSE", 'yahoo':"^FTSE",'name':{'chinese':u"英国富时100指数", 'english':"FTSE 100"}},
    {'code':"GDAXI", 'yahoo':"^GDAXI",'name':{'chinese':u"德国法兰克福DAX指数", 'english':"DAX"} }
]
chinaStock = [
    "000063", #  中兴通讯
    "600036", #  招商银行
]

def main():
    "main function"
    print "test world stock index:" 
    for stockDict in worldIndex:
        print get_yahoo_daily(stockDict)


if __name__ == '__main__':
    import pycallgraph 
    pycallgraph.start_trace()
    main()
    pycallgraph.make_dot_graph('r.png')
