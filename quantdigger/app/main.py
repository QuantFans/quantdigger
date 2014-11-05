__author__ = 'Wenwei Huang'

import logging
from PyQt4 import QtGui

from mainwindow import MainWindow

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)
    logger.info("Start")
    import sys
    app = QtGui.QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())

