#_*_ coding: utf-8 _*_
## @todo merge quantview to ContainerView

__author__ = 'TeaEra'
from PyQt4.QtGui import *
from PyQt4.QtCore import *

from QuantUtils import from_utf8
from QuantUtils import translate
from QuantUtils import get_random_series_list_from
from TrendsWidget import ContainerView

class MainForm(QWidget):
    """
    Class: MainWidget
    """

    def __init__(self):
        super(MainForm, self).__init__()
        #
        self._quotation_view = None
        self._container_view = None
        self._menus = list()
        #
        self.init_main_form()

    def init_main_form(self):
        self.setWindowTitle(
            translate("Form", "TE-K-Line", None)
        )
        # Layout for MainForm:
        main_form_grid_layout = QGridLayout(self)
        main_form_grid_layout.setContentsMargins(5, 0, 5, 5)
        # Tab widget:
        tab_widget = QTabWidget(self)
        tab_widget.setTabPosition(QTabWidget.North)
        # Menu bar:
        menu_bar_for_tab_widget = QMenuBar(self)
        # Add tab_widget & tab_k_line_menu_bar:
        main_form_grid_layout.addWidget(tab_widget, 1, 0, 1, 1)
        main_form_grid_layout.addWidget(menu_bar_for_tab_widget, 0, 0, 1, 1)
        #
        self.init_tab_widget(tab_widget)
        #
        self.init_menu_bar(menu_bar_for_tab_widget)
        #
        QObject.connect(
            tab_widget,
            SIGNAL("currentChanged(int)"),
            self.enable_menu_for_tab
        )

    def enable_menu_for_tab(self, idx):
        """ 根据ｔａｂ调整menu """
        self._menus[idx].setEnabled(True)
        for i in range(len(self._menus)):
            if i != idx:
                self._menus[i].setEnabled(False)

    def init_tab_widget(self, tab_widget):
        # 蜡烛线
        tab_k_line_view = QWidget()
        tab_k_line_view_grid_layout = QGridLayout(tab_k_line_view)
        tab_widget.addTab(tab_k_line_view, from_utf8("K-Line"))
        container_view = ContainerView()
        self._container_view = container_view
        tab_k_line_view_grid_layout.addWidget( container_view, 0, 0, 1, 1)
        QObject.connect(
            container_view,
            SIGNAL("updateSeries(PyQt_PyObject)"),
            container_view.update_k_line
        )
        QObject.connect(
            container_view,
            SIGNAL("appendDataFrame(PyQt_PyObject)"),
            container_view.append_k_line
        )

    def init_menu_bar(self, menu_bar):
        #
        # Add menu:
        menu_new_k_line = menu_bar.addMenu("K-Line")
        #
        menu_new_k_line.setEnabled(True)
        self._menus.append(menu_new_k_line)
        #
        # Menu for 'K-Line':
        new_action_load = menu_new_k_line.addAction("Load data file")
        menu_new_k_line.addSeparator()
        new_action_update = menu_new_k_line.addAction("Update last k-line")
        new_action_append = menu_new_k_line.addAction("Append one k-line")
        menu_new_k_line.addSeparator()
        new_action_show_average_line = \
            menu_new_k_line.addAction("Show average line")
        action_hide_average_line = \
            menu_new_k_line.addAction("Hide average line")
        new_action_update.setEnabled(False)
        new_action_append.setEnabled(False)
        new_action_show_average_line.setEnabled(False)
        action_hide_average_line.setEnabled(False)
        #
        QObject.connect( new_action_load,
                                SIGNAL("triggered()"),
                                lambda x=[
                                    new_action_update, new_action_append,
                                    new_action_show_average_line
                                ]:
                                self.on_load_data(x))
        QObject.connect( new_action_update,
                                SIGNAL("triggered()"),
                                self.on_update)
        QObject.connect( new_action_append,
                                SIGNAL("triggered()"),
                                self.on_append)
        QObject.connect( new_action_show_average_line,
                                SIGNAL("triggered()"),
                                lambda x=[
                                    new_action_show_average_line, action_hide_average_line
                                ]:
                                self.show_average_line(x))
        QObject.connect( action_hide_average_line,
                                SIGNAL("triggered()"),
                                lambda x=[
                                    new_action_show_average_line, action_hide_average_line
                                ]:
                                self.hide_average_line(x))


    def on_load_data(self, action_list):
        file_dialog = QFileDialog(self)
        file_dialog.setWindowTitle("Load data file")
        file_dialog.setNameFilter("Data files (*.csv)")
        file_dialog.show()
        if file_dialog.exec_():  # Click 'Open' will return 1;
            data_file = file_dialog.selectedFiles()[0]
            self._container_view.load_data(data_file)
            for action in action_list:
                action.setEnabled(True)

    def on_update(self):
        data = get_random_series_list_from(self._container_view.get_k_line().get_data())
        self._container_view.emit(SIGNAL("updateSeries(PyQt_PyObject)"), data)

    def on_append(self):
        data = get_random_series_list_from(self._container_view.get_k_line().get_data())
        self._container_view.emit(SIGNAL("appendDataFrame(PyQt_PyObject)"), data)

    def show_average_line(self, menu):
        self._container_view.show_average_line()
        menu[0].setEnabled(False)
        menu[1].setEnabled(True)

    def hide_average_line(self, menu):
        self._container_view.hide_average_line()
        menu[0].setEnabled(True)
        menu[1].setEnabled(False)
