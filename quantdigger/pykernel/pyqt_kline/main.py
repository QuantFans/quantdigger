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
    #
    # Move to center;
    curr_desktop_center = \
        QtGui.QApplication.desktop().availableGeometry(main_form).center()
    main_form.move(
        curr_desktop_center.x() - main_form.width()*0.5,
        curr_desktop_center.y() - main_form.height()*0.5
    )
    sys.exit(app.exec_())