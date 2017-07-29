# -*- coding: utf-8 -*-

import six
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.widgets import Button

from quantdigger.util import gen_logger as log
from quantdigger.interaction.windowgate import WindowGate
from quantdigger.widgets.mplotwidgets import widgets
from quantdigger.widgets.mplotwidgets.mplots import Candles

import pandas as pd
price_data = pd.read_csv('../demo/data/1DAY/SHFE/BB.csv', index_col=0, parse_dates=True)
#price_data = pd.read_csv('../demo/data/IF000.csv', index_col=0, parse_dates=True)

class SubWindowData(object):
    """ 子窗口的数据。"""
    def __init__(self):
        self.curpcontract = None
        self.technicals = { }
        self.strategies = { }


class MainWindow(object):
    """  主界面，负责界面的创建，ui信号和WindowGate函数的对接。
        WindowGate是界面和其它模块交互的入口。
    """
    DEFAULT_PERIOD = 0
    def __init__(self):
        super(MainWindow, self).__init__()
        self._fig = plt.figure()
        self._gate = WindowGate(self)
        self._cur_contract_index = 0
        self._pcontracts_of_contract = {} # {[], []}
        self._subwindows = []
        self._cur_period = 0

        self._create_toolbar()
        self._create_technical_window()
        self._connect_signal()

        pcons = self._gate.get_all_pcontracts()
        for pcon in pcons:
            d = self._pcontracts_of_contract.get(pcon.contract, [])
            d.append(pcon)
            self._pcontracts_of_contract[pcon.contract] = d

    def show_data(self, str_pcontract):
        """"""
        pcon, data = self._gate.get_pcontract(str_pcontract)
        self.candle_widget.plot_with_plotter('candles', data)
        self._frame.load_data(data)
        self.frame.draw_widgets()
        return

    def _create_toolbar(self):
        axprev = self._fig.add_axes([0.1, 0.92, 0.07, 0.075])
        axnext = self._fig.add_axes([0.2, 0.92, 0.07, 0.075])
        self.btn_next = Button(axnext, '1Day')
        self.btn_prev = Button(axprev, '1Min')

    def _create_technical_window(self):
        self.frame = widgets.TechnicalWidget(self._fig, price_data, height=0.85)
        axes = self.frame.init_layout(50, 4, 1)
        ax_volume = axes[1]
        # at most 5 ticks, pruning the upper and lower so they don't overlap
        # with other ticks
        ax_volume.yaxis.set_major_locator(widgets.MyLocator(5, prune='both'))

        # 添加k线和交易信号。
        subwidget1 = widgets.FrameWidget(axes[0], "subwidget1", 100, 50)
        candles = Candles(price_data, None, 'candles')
        subwidget1.add_plotter(candles, False)
        self.candle_widget = self.frame.add_widget(0, subwidget1, True)
        ## 添加指标
        #self.frame.add_technical(0, MA(price_data.close, 20, 'MA20', 'y', 2))
        #self.frame.add_technical(0, MA(price_data.close, 30, 'MA30', 'b', 2))
        #self.frame.add_technical(1, Volume(price_data.open, price_data.close, price_data.vol))
        self.frame.draw_widgets()

    def _connect_signal(self):
        self.btn_next.on_clicked(self.on_next_contract)
        self.btn_prev.on_clicked(self.on_previous_contract)
        self._fig.canvas.mpl_connect('key_release_event', self.on_keyrelease)

    def on_keyrelease(self, event):
        log.debug(event.key)
        if event.key == u"super+up":
            self.on_previous_contract
        elif event.key == u"super+down":
            self.on_next_contract()

    def show(self):
        plt.show()

    def close(self):
        self._gate.stop()

    def on_next_contract(self, event):
        if self._cur_contract_index + 1 < len(self._pcontracts_of_contract.keys()):
            self._cur_contract_index += 1
            contract = list(self._pcontracts_of_contract.keys())[self._cur_contract_index]

            pcon = self._pcontracts_of_contract[contract][self._cur_period]
            pcon, data = self._gate.get_pcontract(str(pcon))
            self.frame.load_data(data)
            self.candle_widget.plot_with_plotter('candles', data)
            self.frame.draw_widgets()
            six.print_("next" , str(pcon), "**" )
        else:
            six.print_("stop_next" )

    def on_previous_contract(self, event):
        if self._cur_contract_index - 1 >= 0:
            self._cur_contract_index -= 1
            contract = list(self._pcontracts_of_contract.keys())[self._cur_contract_index]

            pcon = self._pcontracts_of_contract[contract][self._cur_period]
            pcon, data = self._gate.get_pcontract(str(pcon))
            self.frame.load_data(data)
            self.candle_widget.plot_with_plotter('candles', data)
            self.frame.draw_widgets()
            six.print_("prev" , str(pcon), "**" )
        else:
            six.print_("stop_pre" )



mainwindow = MainWindow()

if __name__ == '__main__':
    mainwindow.show()
    import time, sys
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        mainwindow.close()
        sys.exit(0)
