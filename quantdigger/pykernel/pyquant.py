#!/usr/bin/env python
# -*- coding: utf8 -*-
import os, sys
sys.path.append(os.path.join('.'))
from IPython.qt.console.rich_ipython_widget import RichIPythonWidget
from IPython.qt.inprocess import QtInProcessKernelManager
from PyQt4 import QtGui, QtCore
from plugin.qtwidgets.techwidget import TechWidget
from datasource import data
from plugin.mplotwidgets import widgets, indicator
price_data, entry_x, entry_y, exit_x, exit_y, colors = data.get_stock_signal_data()

class EmbedIPython(RichIPythonWidget):

    def __init__(self, **kwarg):
        super(RichIPythonWidget, self).__init__()
        self.kernel_manager = QtInProcessKernelManager()
        self.kernel_manager.start_kernel()
        self.kernel = self.kernel_manager.kernel
        self.kernel.gui = 'qt4'
        self.kernel.shell.push(kwarg)
        self.kernel_client = self.kernel_manager.client()
        self.kernel_client.start_channels()


class MainWindow(QtGui.QMainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.createToolBox()
        self.textEdit = QtGui.QTextEdit()

        self.center_widget = self.demo_plot()
        #self.center_widget.subplots_adjust(0.05, 0.05, 1, 1)

        self.createActions()
        self.createMenus()
        self.createToolBars()
        self.createStatusBar()
        self.createDockWindows()
        self.setWindowTitle("QuantDigger")
        self.setUnifiedTitleAndToolBarOnMac(True)
        self.setCentralWidget(self.center_widget)
        self.center_widget.setFocus(True)

    def about(self):
        QtGui.QMessageBox.about(self, "About Dock Widgets",
                "The <b>Dock Widgets</b> example demonstrates how to use "
                "Qt's dock widgets. You can enter your own text, click a "
                "customer to add a customer name and address, and click "
                "standard paragraphs to add them.")

    def createActions(self):
        #self.saveAct = QtGui.QAction(QtGui.QIcon(':/images/save.png'),
                #"&Save...", self, shortcut=QtGui.QKeySequence.Save,
                #statusTip="Save the current form letter",
                #triggered=self.save)


        self.quitAct = QtGui.QAction("&Quit", self, shortcut="Ctrl+Q",
                statusTip="Quit the application", triggered=self.close)

        self.aboutAct = QtGui.QAction("&About", self,
                statusTip="Show the application's About box",
                triggered=self.about)

        self.aboutQtAct = QtGui.QAction("About &Qt", self,
                statusTip="Show the Qt library's About box",
                triggered=QtGui.qApp.aboutQt)

    def createMenus(self):
        self.fileMenu = self.menuBar().addMenu("&File")
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.quitAct)
        self.viewMenu = self.menuBar().addMenu("&View")

        self.menuBar().addSeparator()

        self.helpMenu = self.menuBar().addMenu("&Help")
        self.helpMenu.addAction(self.aboutAct)
        self.helpMenu.addAction(self.aboutQtAct)

    def createToolBars(self):
        self.fileToolBar = self.addToolBar("File")
        self.fileToolBar.addAction(self.aboutQtAct)

        self.editToolBar = self.addToolBar("Edit")
        self.fileToolBar.addAction(self.quitAct)

    def createStatusBar(self):
        self.statusBar().showMessage("Ready")

    def createDockWindows(self):
        # Ipython终端栏
        self.console = EmbedIPython(testing=123)
        self.console.kernel.shell.run_cell('%pylab qt')
        dock = QtGui.QDockWidget("Ipython Console", self)
        dock.setWidget(self.console)
        dock.setAllowedAreas(QtCore.Qt.BottomDockWidgetArea | QtCore.Qt.TopDockWidgetArea)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, dock)
        self.viewMenu.addAction(dock.toggleViewAction())
        # ToolBox工具栏
        dock = QtGui.QDockWidget("Customers", self)
        dock.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
        dock.setWidget(self.toolBox)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, dock)
        self.viewMenu.addAction(dock.toggleViewAction())
        #self.customerList.currentTextChanged.connect(self.insertCustomer)
        #self.paragraphsList.currentTextChanged.connect(self.addParagraph)


    def demo_plot(self):
        frame = TechWidget(self, 80, 4, 3, 1)
        ax_candles, ax_rsi, ax_volume = frame

        # 把窗口传给techplot, 连接信号
        # 事件处理 ||||  绘图，数据的分离。
        # twins窗口。
        # rangew
        # 事件从techplot传到PYQT

        try:
            kwindow = widgets.CandleWindow("kwindow", price_data, 100, 50)
            frame.add_widget(0, kwindow, True)
            signal = indicator.TradingSignal(zip(zip(entry_x,entry_y),zip(exit_x,exit_y)), c=colors, lw=2)
            frame.add_indicator(0, signal)

            # 指标窗口
            frame.add_indicator(0, indicator.MA(price_data.close, 20, 'MA20', 'simple', 'y', 2))
            frame.add_indicator(0, indicator.MA(price_data.close, 30, 'MA30', 'simple', 'b', 2))
            frame.add_indicator(1, indicator.RSI(price_data.close, 14, name='RSI', fillcolor='b'))
            frame.add_indicator(2, indicator.Volume(price_data.open, price_data.close, price_data.vol))
            frame.draw_window()
        except Exception, e:
            print "----------------------" 
            print e

        return frame





    def createToolBox(self):
        self.buttonGroup = QtGui.QButtonGroup()
        self.buttonGroup.setExclusive(False)
        #self.buttonGroup.buttonClicked[int].connect(self.buttonGroupClicked)

        layout = QtGui.QGridLayout()
        #layout.addWidget(self.createCellWidget("Conditional", DiagramItem.Conditional), 0, 0)
        #layout.addWidget(self.createCellWidget("Process", DiagramItem.Step), 0, 1)
        #layout.addWidget(self.createCellWidget("Input/Output", DiagramItem.Io), 1, 0)

        textButton = QtGui.QToolButton()
        textButton.setCheckable(True)
        textButton.setIcon(QtGui.QIcon(QtGui.QPixmap(':/images/textpointer.png')
                            .scaled(30, 30)))
        textButton.setIconSize(QtCore.QSize(50, 50))

        textLayout = QtGui.QGridLayout()
        textLayout.addWidget(textButton, 0, 0, QtCore.Qt.AlignHCenter)
        textLayout.addWidget(QtGui.QLabel("Text"), 1, 0,
                QtCore.Qt.AlignCenter)
        textWidget = QtGui.QWidget()
        textWidget.setLayout(textLayout)
        layout.addWidget(textWidget, 1, 1)

        layout.setRowStretch(3, 10)
        layout.setColumnStretch(2, 10)

        itemWidget = QtGui.QWidget()
        itemWidget.setLayout(layout)

        self.backgroundButtonGroup = QtGui.QButtonGroup()
        #self.backgroundButtonGroup.buttonClicked.connect(self.backgroundButtonGroupClicked)

        backgroundLayout = QtGui.QGridLayout()
        backgroundLayout.addWidget(self.createBackgroundCellWidget("Blue Grid",
                ':/images/background1.png'), 0, 0)
        backgroundLayout.addWidget(self.createBackgroundCellWidget("White Grid",
                ':/images/background2.png'), 0, 1)
        backgroundLayout.addWidget(self.createBackgroundCellWidget("Gray Grid",
                ':/images/background3.png'), 1, 0)
        backgroundLayout.addWidget(self.createBackgroundCellWidget("No Grid",
                ':/images/background4.png'), 1, 1)

        backgroundLayout.setRowStretch(2, 10)
        backgroundLayout.setColumnStretch(2, 10)

        backgroundWidget = QtGui.QWidget()
        backgroundWidget.setLayout(backgroundLayout)

        self.toolBox = QtGui.QToolBox()
        self.toolBox.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Ignored))
        self.toolBox.setMinimumWidth(itemWidget.sizeHint().width())
        self.toolBox.addItem(itemWidget, "Basic Flowchart Shapes")
        self.toolBox.addItem(backgroundWidget, "Backgrounds")

    def createBackgroundCellWidget(self, text, image):
        button = QtGui.QToolButton()
        button.setText(text)
        button.setIcon(QtGui.QIcon(image))
        button.setIconSize(QtCore.QSize(50, 50))
        button.setCheckable(True)
        self.backgroundButtonGroup.addButton(button)

        layout = QtGui.QGridLayout()
        layout.addWidget(button, 0, 0, QtCore.Qt.AlignHCenter)
        layout.addWidget(QtGui.QLabel(text), 1, 0, QtCore.Qt.AlignCenter)

        widget = QtGui.QWidget()
        widget.setLayout(layout)
        return widget

    def keyPressEvent(self, event):
        key = event.key()
        print(key)
        if key == QtCore.Qt.Key_Left:
           print('Left Arrow Pressed')



if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())
    ## 执行终端语句
    ##self.console.execute("print('a[\\\'text\\\'] = \"'+ a['text'] +'\"')")
