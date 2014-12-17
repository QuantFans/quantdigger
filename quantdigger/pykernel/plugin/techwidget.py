# -*- coding: utf8 -*-
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg
from techmplot import TechMPlot

import os, sys
sys.path.append(os.getcwd())
#from  mplot_widgets import widgets as mwidgets

class TechWidget(TechMPlot, FigureCanvasQTAgg):
    def __init__(self, parent=None, *args):
        TechMPlot.__init__(self, *args)
        FigureCanvasQTAgg.__init__(self, self.fig)
        self.setParent(parent)
        self.in_qt = True
        self.set_cursor()
        self.connect()  # 必须在这里再调用一次。


