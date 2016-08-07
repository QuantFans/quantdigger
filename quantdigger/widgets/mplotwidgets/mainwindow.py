# -*- coding: utf-8 -*-
#import os, sys
#sys.path.append(os.path.join('..', '..'))

import pandas as pd
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.widgets import Button

from quantdigger.config import ConfigInteraction
from quantdigger.datastruct import PContract
from quantdigger.event.rpc import EventRPCClient, EventRPCServer
from quantdigger.event.eventengine import ZMQEventEngine
from quantdigger.interaction.interface import BackendInterface
from quantdigger.technicals.common import MA, Volume
from quantdigger.util import gen_logger as log
from quantdigger.widgets.mplotwidgets import widgets

#price_data = pd.read_csv('../data/IF000.csv', index_col=0, parse_dates=True)


class WindowGate(BackendInterface):
    def __init__(self, widget):
        self._engine = ZMQEventEngine('WindowGate')
        self._engine.start()
        self._backend = EventRPCClient('WindowGate', self._engine, 
                ConfigInteraction.backend_server_for_ui)
        self._ipy_srv = EventRPCServer(self._engine, ConfigInteraction.ui_server_for_shell)
        self._period = None
        self._contract = None
        self._widget = widget
        self._register_functions(self._ipy_srv)

    def _register_functions(self, server):
        server.register('get_all_contracts', self.get_all_contracts)

    def add_widget(self, ith, type_):
        self._widget.add_widget

    def add_technical(self, ith, technical):
        """""" 
        ## @TODO compute technical with backend,
        # display result from backend
        return

    @property
    def pcontract(self):
        return PContract(self._contract, self._period)

    def stop(self):
        self._engine.stop()

    def next(self, event):
        #plt.draw()
        print "next" 

    def prev(self, event):
        #plt.draw()
        print "prev" 

    def get_all_contracts(self):
        return self._backend.sync_call('get_all_contracts')

    def get_pcontract(self, pcontract):
        pass

    def run_strategy(self, name):
        """""" 
        return

    def run_technical(self, name):
        return

    def get_technicals(self):
        """ 获取系统的所有指标。 """
        return

    def get_strategies(self):
        """ 获取系统的所有策略。 """
        return

    def next_pcontract(self):
        return

    def previous_pcontract(self):
        return
    

class MainWindow(object):
    """  主界面，负责界面的创建，ui信号和WindowGate函数的对接。
        WindowGate是界面和其它模块交互的入口。
    """
    def __init__(self):
        super(MainWindow, self).__init__()
        self._fig = plt.figure()
        self._gate = WindowGate(self)
        self._create_toolbar()
        self._create_technical_window()
        self._connect_signal()
    
    def _create_toolbar(self):
        axprev = self._fig.add_axes([0.1, 0.92, 0.07, 0.075], axisbg='gray')
        axnext = self._fig.add_axes([0.2, 0.92, 0.07, 0.075], axisbg='gray')
        self.btn_next = Button(axnext, '1Day')
        self.btn_prev = Button(axprev, '1Min')

    def _create_technical_window(self):
        #self.frame = widgets.TechnicalWidget(self._fig, price_data, height=0.85)
        #self.frame.init_layout(50, 4, 1)
        #ax_candles,  ax_volume = self.frame.get_subwidgets()
        ## at most 5 ticks, pruning the upper and lower so they don't overlap
        ## with other ticks
        #ax_volume.yaxis.set_major_locator(widgets.MyLocator(5, prune='both'))

        ## 添加k线和交易信号。
        #kwindow = widgets.CandleWindow("kwindow", price_data, 100, 50)
        #candle_widget = self.frame.add_widget(0, kwindow, True)
        ## 添加指标
        #self.frame.add_technical(0, MA(price_data.close, 20, 'MA20', 'y', 2))
        #self.frame.add_technical(0, MA(price_data.close, 30, 'MA30', 'b', 2))
        #self.frame.add_technical(1, Volume(price_data.open, price_data.close, price_data.vol))
        #self.frame.draw_widgets()
        pass

    def _connect_signal(self):
        self.btn_next.on_clicked(self._gate.next)
        self.btn_prev.on_clicked(self._gate.prev)
        self._fig.canvas.mpl_connect('key_release_event', self.on_keyrelease)

    def on_keyrelease(self, event):
        log.debug(event.key)
        if event.key == u"super+up":
            self._gate.previous_pcontract()
        elif event.key == u"super+down":
            self._gate.next_pcontract()

    def show(self):
        plt.show()

    def close(self):
        self._gate.stop()


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
