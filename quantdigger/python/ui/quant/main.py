# -*- coding: utf-8 -*-

__author__ = 'TeaEra'

from PyQt4 import QtGui

from QuantView import MainForm

################################################################################
# Main portal:
if __name__ == "__main__":
    print(">>> Main portal")
    #
    import sys
    app = QtGui.QApplication(sys.argv)
    main_form = MainForm()
    main_form.show()
    sys.exit(app.exec_())