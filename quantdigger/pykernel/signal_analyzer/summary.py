# -*- coding: gbk -*-
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import analyze

def wave_analyze(fname):
    #print waves
    #load_data(0, fname)
    data, = load_datas(0, False, fname) 
    t, = load_wavedata(fname)

def tradeinfo(fname, n=10, intraday=False):
    '''docstring for analyze''' 
    analyze.AnalyzeFrame(fname, 10, intraday)
    plt.show()

if __name__ == '__main__':
    tradeinfo("_djtrend2_IF000")

