# -*- coding: utf-8 -*-
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg
from quantdigger.widgets.mplotwidgets.widgets import MultiWidgets
import matplotlib.pyplot as plt


class TechWidget(MultiWidgets, FigureCanvasQTAgg):
    def __init__(self, parent=None, *args):
        self.fig = plt.figure()
        FigureCanvasQTAgg.__init__(self, self.fig)
        MultiWidgets.__init__(self, self.fig, *args)
        self.setParent(parent)
