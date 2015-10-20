# -*- coding: utf8 -*-
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from quantdigger.indicators.common import MA
from quantdigger.datasource.data import csv2frame

# 创建画布
fig, ax = plt.subplots()
# 加载数据
price_data = csv2frame("IF000.SHFE-10.Minute.csv")
# 创建平均线
ma10 = MA(None, price_data.close, 10, 'MA10', 'y', 2)
ma20 = MA(None, price_data.close, 60, 'MA10', 'b', 2)
# 绘制指标
ma10.plot(ax)
ma20.plot(ax)
plt.show()
