# -*- coding: utf8 -*-
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from quantdigger.indicators.common import MA
import pandas as pd

# 创建画布
fig, ax = plt.subplots()
# 加载数据
price_data = pd.read_csv("./data/IF000.SHFE-10.Minute.csv", 
                        index_col=0, parse_dates=True)
# 创建平均线
ma10 = MA(price_data.close, 10, 'MA10', 'y', 2)
ma20 = MA(price_data.close, 60, 'MA10', 'b', 2)
# 绘制指标
ma10.plot(ax)
ma20.plot(ax)
plt.show()
