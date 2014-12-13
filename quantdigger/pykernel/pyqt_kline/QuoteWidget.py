from PyQt4.QtGui import *
from PyQt4.QtCore import *
class QuoteWidget(QTableView):
    """
    """

    def __init__(
        self, data=None,
        horizontal_header_info=None,
        vertical_header_info=None
    ):
        super(QuoteWidget, self).__init__()
        self._model = QStandardItemModel()
        self.setModel(self._model)
        self._is_data_loaded = False
        #
        if data:
            self.set_data(data)
        #
        if horizontal_header_info:
            self.set_horizontal_header(horizontal_header_info)
        #
        if vertical_header_info:
            self.set_vertical_header(vertical_header_info)

    def clean_data(self):
        self._model.removeRows(0, self._model.rowCount())

    def remove_data(self):
        self.clean_data()
        self.horizontalHeader().hide()
        self.verticalHeader().hide()

    def set_data(self, data):
        #
        self.clean_data()
        #
        for each_row in data:
            each_row_items = \
                [
                    QStandardItem(from_utf8(str(item)))
                    for item in each_row
                ]
            self._model.appendRow(each_row_items)
        #
        self._is_data_loaded = True
        self.show_header()

    def set_horizontal_header(self, horizontal_header_info):
        for i in range(len(horizontal_header_info)):
            self._model.setHeaderData(
                i, Qt.Horizontal,
                QVariant(from_utf8(str(horizontal_header_info[i])))
            )

    def set_vertical_header(self, vertical_header_info):
        for i in range(len(vertical_header_info)):
            self._model.setHeaderData(
                i, Qt.Vertical,
                QVariant(from_utf8(str(vertical_header_info[i])))
            )

    def set_data_color(self):
        for i in range(self._model.rowCount()):
            for j in range(self._model.columnCount()):
                self._model.setData(
                    self._model.index(i, j),
                    QColor(Qt.black),
                    Qt.BackgroundRole
                )
                self._model.setData(
                    self._model.index(i, j),
                    QColor(Qt.yellow),
                    Qt.ForegroundRole
                )

    def show_header(self):
        self.horizontalHeader().show()
        self.verticalHeader().show()

    def enable_header_sorting(self):
        self.setSortingEnabled(True)

    def enable_popup_context_menu(self):
        horizontal_header = self.horizontalHeader()
        vertical_header = self.verticalHeader()
        #horizontal_header.setClickable(True)
        #vertical_header.setClickable(True)
        horizontal_header.setContextMenuPolicy(Qt.CustomContextMenu)
        vertical_header.setContextMenuPolicy(Qt.CustomContextMenu)
        horizontal_header.customContextMenuRequested.connect(
            self.popup_context_menu
        )
        vertical_header.customContextMenuRequested.connect(
            self.popup_context_menu
        )

    def popup_context_menu(self, position):
        menu = QMenu()
        all_cols = []
        for i in range(self._model.columnCount()):
            all_cols.append(
                menu.addAction(
                    self._model.headerData(
                        i, Qt.Horizontal
                    ).toString()
                )
            )
            #menu.actions()[i]
        # Add a separator:
        menu.addSeparator()
        all_cols.append(menu.addAction("Show all"))
        all_cols.append(menu.addAction("Hide all"))
        ac = menu.exec_(self.mapToGlobal(position))
        if ac in all_cols:
            idx = all_cols.index(ac)
            if idx < len(all_cols) - 2:
                if self.isColumnHidden(idx):
                    self.showColumn(idx)
                elif not self.isColumnHidden(idx):
                    self.hideColumn(idx)
            elif idx == len(all_cols) - 2:
                for i in range(self._model.columnCount()):
                    self.showColumn(i)
            elif idx == len(all_cols) - 1:
                for i in range(self._model.columnCount()):
                    self.hideColumn(i)

    def update_data(self, updated_data):
        for i in range(len(updated_data)):
            for j in range(len(updated_data[0])):
                if self._model.item(i, j).text()\
                        .compare(
                            from_utf8(str(updated_data[i][j]))
                        ) != 0:
                    self._model.setData(
                        self._model.index(i, j),
                        QVariant(from_utf8(str(updated_data[i][j])))
                    )
                    self._model.setData(
                        self._model.index(i, j),
                        QColor(Qt.red), Qt.BackgroundRole
                    )
                    self._model.setData(
                        self._model.index(i, j),
                        QColor(Qt.black), Qt.ForegroundRole
                    )

    def is_data_loaded(self):
        return self._is_data_loaded
