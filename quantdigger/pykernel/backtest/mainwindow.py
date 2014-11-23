__author__ = 'Wenwei Huang'

import os
import logging
import glob
import imp
from datetime import datetime

import pandas as pd
import matplotlib.mlab as mlab
from PyQt4 import QtCore
from PyQt4 import QtGui
from dateutil import parser
import matplotlib.dates as mdates
from functools import partial

from config import data_path
from config import strategy_path
from utils import fromUtf8, WindowSize
from mainwindow_ui import Ui_MainWindow
from strategy_runner import StrategyRunner

logger = logging.getLogger(__name__)

class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.ui_controller = Ui_MainWindow()
        self.ui_controller.setupUi(self)
        self.connect()
        self.ui_controller.matplotlibWidget.connect()
        self.init_style_menu()
        self.init_indicator_menu()
        self.init_strategy_panel()

    def init_style_menu(self):
        self.ui_controller.styleMenu = QtGui.QMenu(self)
        self.ui_controller.lineChartAction = QtGui.QAction("Line", self)
        self.ui_controller.areaChartAction = QtGui.QAction("Area", self)
        self.ui_controller.barChartAction = QtGui.QAction("Bar", self)
        self.ui_controller.candleChartAction = QtGui.QAction("Candle", self)
        self.ui_controller.styleMenu.addAction(self.ui_controller.lineChartAction)
        self.ui_controller.styleMenu.addAction(self.ui_controller.areaChartAction)
        self.ui_controller.styleMenu.addAction(self.ui_controller.barChartAction)
        self.ui_controller.styleMenu.addAction(self.ui_controller.candleChartAction)
        self.ui_controller.styleToolButton.setMenu(self.ui_controller.styleMenu)

    def init_indicator_menu(self):
        self.ui_controller.indicatorMenu = QtGui.QMenu(self)
        self.ui_controller.indicator_SMAAction = QtGui.QAction("Simple Moving Average (SMA)", self)
        self.ui_controller.indicator_EMAAction = QtGui.QAction("Exponential Moving Average (EMA)", self)
        self.ui_controller.indicator_MACDAction = QtGui.QAction("MACD", self)
        self.ui_controller.indicator_RSIAction = QtGui.QAction("Relative Strength Index (RSI)", self)
        self.ui_controller.indicatorMenu.addAction(self.ui_controller.indicator_SMAAction)
        self.ui_controller.indicatorMenu.addAction(self.ui_controller.indicator_EMAAction)
        self.ui_controller.indicatorMenu.addAction(self.ui_controller.indicator_MACDAction)
        self.ui_controller.indicatorMenu.addAction(self.ui_controller.indicator_RSIAction)
        self.ui_controller.indicatorToolButton.setMenu(self.ui_controller.indicatorMenu)

    def init_strategy_panel(self):
        strategy_files = sorted(glob.glob('%s/*.py' % strategy_path))
        for file in strategy_files:
            base = os.path.splitext(os.path.basename(file))[0]
            item = QtGui.QListWidgetItem(base, self.ui_controller.strategyListWidget)
            item.setData(QtCore.Qt.UserRole, QtCore.QVariant(file))
            self.ui_controller.strategyListWidget.addItem(item)
        self.ui_controller.strategyListWidget.customContextMenuRequested.connect(self.showMenu)

    def connect(self):
        self.ui_controller.loadQuoteButton.clicked.connect(self.on_loadQuoteClicked)
        for toolButton in self.ui_controller.buttonGroup.buttons():
            toolButton.clicked.connect(partial(self.on_toolButtonClicked, toolButton))
        self.ui_controller.actionRunStrategy.triggered.connect(self.on_runStrategy)
        self.ui_controller.actionEditStrategy.triggered.connect(self.on_editStrategy)

    def on_loadQuoteClicked(self):
        logger.info('load quote')

        fileName = QtGui.QFileDialog.getOpenFileName(
            self, self.tr("Open Quote Data"), data_path,
            self.tr("Quote Files (*.csv)"))
        logger.info("Filename %s" % fileName)

        if os.path.isfile(fileName):
            df = pd.read_csv(unicode(fileName))
            df.columns = [col.lower() for col in df.columns]
            if 'datetime' in df.columns:
                df = df.sort(['datetime'])
                df['datetime'] = df.apply(
                    lambda row: mdates.date2num(parser.parse(row['datetime'])),
                    axis=1)
            elif 'date' in df.columns:
                df = df.sort(['date'])
                df['datetime'] = df.apply(
                    lambda row: mdates.date2num(parser.parse(row['date'])),
                    axis=1)

            if 'datetime' in df.columns and not df['datetime'].empty:
                self.ui_controller.matplotlibWidget.set_data(df)
                self.ui_controller.matplotlibWidget.draw_data()

    def on_toolButtonClicked(self, button):
        name = str(button.objectName())
        button_values = {
            'oneDayToolButton': WindowSize.ONEDAY,
            'fiveDayToolButton': WindowSize.FIVEDAY,
            'oneMonthToolButton': WindowSize.ONEMONTH,
            'threeMonthToolButton': WindowSize.THREEMONTH,
            'sixMonthToolButton': WindowSize.SIXMONTH,
            'oneYearToolButton': WindowSize.ONEYEAR,
            'twoYearToolButton': WindowSize.TWOYEAR,
            'fiveYearToolButton': WindowSize.FIVEYEAR,
            'maxToolButton': WindowSize.MAX,
        }
        size = button_values[name]
        self.ui_controller.matplotlibWidget.setxlim(size)

    def showMenu(self, position):
        indexes = self.ui_controller.strategyListWidget.selectedIndexes()
        if len(indexes) > 0:
            menu = QtGui.QMenu()
            menu.addAction(self.ui_controller.actionRunStrategy)
            menu.addAction(self.ui_controller.actionEditStrategy)
            menu.exec_(self.ui_controller.strategyListWidget.viewport().mapToGlobal(position))

    def on_runStrategy(self, check):
        indexes = self.ui_controller.strategyListWidget.selectedIndexes()
        if len(indexes) > 0:
            logger.info('Run strategy')
            index = indexes[0].row()
            item = self.ui_controller.strategyListWidget.item(index)
            strategy_file = str(item.data(QtCore.Qt.UserRole).toPyObject())
            strategy = imp.load_source('strategy', strategy_file)
            if hasattr(strategy, 'initialize') and hasattr(strategy, 'run'):
                runner = StrategyRunner(initialize=strategy.initialize, run=strategy.run)
                runner.run('Data')
            else:
                logger.error("%s is not a valid strategy" % strategy_file)

    def on_editStrategy(self, check):
        indexes = self.ui_controller.strategyListWidget.selectedIndexes()
        if len(indexes) > 0:
            logger.info('Edit strategy')
            index = indexes[0].row()
            item = self.ui_controller.strategyListWidget.item(index)
            strategy_file = item.data(QtCore.Qt.UserRole).toPyObject()
            print strategy_file
