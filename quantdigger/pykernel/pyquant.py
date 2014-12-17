#!/usr/bin/env python
# -*- coding: utf8 -*-
from IPython.qt.console.rich_ipython_widget import RichIPythonWidget
from IPython.qt.inprocess import QtInProcessKernelManager
from PyQt4 import QtGui, QtCore
from plugin.techwidget import TechWidget
from datasource import data
from  mplot_widgets import widgets as mwidgets



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

        self.center_widget = TechWidget(self, 1)
        self.center_widget.subplots_adjust(0.05, 0.05, 1, 1)
        axk = self.center_widget.axes[0]
        axk.grid(True)
        self.kwindow = mwidgets.CandleWindow(axk, "kwindow", price_data, 100, 50)

        self.setCentralWidget(self.center_widget)
        self.createActions()
        self.createMenus()
        self.createToolBars()
        self.createStatusBar()
        self.createDockWindows()
        self.setWindowTitle("QuantDigger")
        self.setUnifiedTitleAndToolBarOnMac(True)

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



if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())
    ## 执行终端语句
    ##self.console.execute("print('a[\\\'text\\\'] = \"'+ a['text'] +'\"')")
