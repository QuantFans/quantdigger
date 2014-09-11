#_*_ coding: utf-8 _*_

__author__ = 'TeaEra'

from PyQt4 import QtGui
from PyQt4 import QtCore
import pandas as pd
import math

from QuantUtils import from_utf8
from QuantUtils import translate
from QuantUtils import get_k_line_data_by_path
from QuantUtils import get_min_and_max_price
from QuantUtils import get_random_series_from
from QuantUtils import get_random_series_list_from

from QuantModel import RectLikeLine
from QuantModel import SlicedPixMapModel
from QuantModel import WindowedPixMapModel
from QuantModel import UpdatedSeriesModel
from QuantModel import AppendedDataFrameModel

from QuantTestData import AllDataForTest

from QxtSpanSlider import QxtSpanSlider

################################################################################


class KLineSizeSetter(QtGui.QWidget):
    """
    """

    def __init__(self, size_min=1, size_max=100, curr_value=1):
        super(KLineSizeSetter, self).__init__()
        #
        main_grid_layout = QtGui.QGridLayout(self)
        #
        label_size = QtGui.QLabel(from_utf8("K-Line size: "))
        spin_box_size = QtGui.QSpinBox()
        #
        main_grid_layout.addWidget(label_size, 0, 0, 1, 1)
        main_grid_layout.addWidget(spin_box_size, 1, 0, 1, 1)
        #
        spin_box_size.setMinimum(size_min)
        spin_box_size.setMaximum(size_max)
        spin_box_size.setValue(curr_value)
        #
        self._spin_box_size = spin_box_size

    def get_spin_box_size(self):
        """
        Getter for widget: self._spin_box_size;
        """
        return self._spin_box_size

    def get_spin_box_size_value(self):
        """
        Getter for value of self._spin_box_size;
        """
        return self._spin_box_size.value()

    def set_size_min(self, size_min):
        """
        Setter for minimum value of self._spin_box_size;
        """
        self._spin_box_size.setMinimum(size_min)

    def set_size_max(self, size_max):
        """
        Setter for maximum value of self._spin_box_size;
        """
        self._spin_box_size.setMaximum(size_max)

    def set_curr_value(self, curr_value):
        """
        Setter for value of self._spin_box_size;
        """
        self._spin_box_size.setValue(curr_value)

################################################################################
# TODO: not enables for now;


class IndexRangeSelector(QtGui.QWidget):
    """
    """

    def __init__(self, from_index=0, to_index=99):
        super(IndexRangeSelector, self).__init__()
        #
        main_grid_layout = QtGui.QGridLayout(self)
        #
        label_from = QtGui.QLabel(from_utf8("From"))
        label_to = QtGui.QLabel(from_utf8("To"))
        spin_box_from = QtGui.QSpinBox()
        spin_box_to = QtGui.QSpinBox()
        #
        main_grid_layout.addWidget(label_from, 0, 0, 1, 1)
        main_grid_layout.addWidget(spin_box_from, 0, 1, 1, 1)
        main_grid_layout.addWidget(label_to, 1, 0, 1, 1)
        main_grid_layout.addWidget(spin_box_to, 1, 1, 1, 1)
        #
        spin_box_from.setMinimum(from_index + 1)
        spin_box_from.setMaximum(to_index + 1)
        spin_box_to.setMinimum(from_index + 1)
        spin_box_to.setMaximum(to_index + 1)
        #
        self._spin_box_from = spin_box_from
        self._spin_box_to = spin_box_to

    def get_spin_box_from(self):
        """
        Getter
        """
        return self._spin_box_from

    def get_spin_box_to(self):
        """
        Getter
        """
        return self._spin_box_to

    def get_from_value(self):
        """
        Getter for value
        """
        return self._spin_box_from.value()

    def get_to_value(self):
        """
        Getter for value
        """
        return self._spin_box_to.value()

    def set_from_value(self, from_index):
        """
        Setter
        """
        self._spin_box_from.setValue(from_index + 1)

    def set_to_value(self, to_index):
        """
        Setter
        """
        self._spin_box_to.setValue(to_index + 1)

    def set_ranges(self, from_index, to_index):
        """
        Setter
        """
        #
        self._spin_box_from.setMinimum(from_index + 1)
        self._spin_box_from.setMaximum(to_index + 1)
        self._spin_box_to.setMinimum(from_index + 1)
        self._spin_box_to.setMaximum(to_index + 1)

    def set_values(self, curr_from_idx, curr_to_idx):
        """
        Setter
        """
        self._spin_box_from.setValue(curr_from_idx + 1)
        self._spin_box_to.setValue(curr_to_idx + 1)

################################################################################


class InfoView(QtGui.QWidget):

    def __init__(self):
        super(InfoView, self).__init__()
        #
        # [en]
        # Background and foreground:
        #
        # [zh]
        # 背景色与前景色
        self_palette = QtGui.QPalette()
        self_palette.setColor(
            QtGui.QPalette.Background, QtGui.QColor(0, 0, 0)
        )
        self_palette.setColor(
            QtGui.QPalette.Foreground, QtGui.QColor(255, 0, 0)
        )
        self.setPalette(self_palette)
        #
        self.pix_map = QtGui.QPixmap(self.size())
        self.pix_map.fill(self, 0, 0)

    def paintEvent(self, event):
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.drawPixmap(0, 0, self.width(), self.height(), self.pix_map)
        painter.end()

################################################################################


class PriceAxisView(QtGui.QWidget):
    """
    """

    def __init__(self):
        super(PriceAxisView, self).__init__()
        #
        # [en]
        # Background and foreground:
        #
        # [zh]
        # 背景色与前景色
        self_palette = QtGui.QPalette()
        self_palette.setColor(
            QtGui.QPalette.Background, QtGui.QColor(0, 0, 0)
        )
        self_palette.setColor(
            QtGui.QPalette.Foreground, QtGui.QColor(255, 0, 0)
        )
        self.setPalette(self_palette)
        #
        self._the_min = 0.0
        self._the_max = 0.0
        #
        self._pix_map_width = 80
        self._pix_map_y_step_height = 100
        self._pix_map_y_steps = 6
        self._pix_map_margin_top = 3
        self._pix_map_margin_bottom = 30
        self._pix_map_height = \
            self._pix_map_y_step_height * self._pix_map_y_steps \
            + self._pix_map_margin_top \
            + self._pix_map_margin_bottom
        self._pix_map_margin_left = 15
        self._pix_map_margin_right = 10
        self._pix_map_indicator_width = 5
        self._pix_map_text_rect_width = \
            self._pix_map_width \
            - self._pix_map_margin_left - self._pix_map_margin_right \
            - self._pix_map_indicator_width - 5
        self._pix_map_text_rect_height = 40
        #
        self._pix_map = QtGui.QPixmap(self.size())
        self._pix_map.fill(self, 0, 0)

    def set_min_and_max_price(self, the_min, the_max):
        #
        self._the_min = the_min
        self._the_max = the_max
        price_step = 1.0 * (the_max - the_min) / (self._pix_map_y_steps - 1)
        #
        self._pix_map = QtGui.QPixmap(
            self._pix_map_width,
            self._pix_map_height
        )
        self._pix_map.fill(self, 0, 0)
        pix_map_painter = QtGui.QPainter(self._pix_map)
        pix_map_painter.initFrom(self)
        #
        price_axis = QtCore.QLineF(
            self._pix_map_width - self._pix_map_margin_right,
            self._pix_map_margin_top,
            self._pix_map_width - self._pix_map_margin_right,
            self._pix_map_margin_top
            + self._pix_map_y_steps * self._pix_map_y_step_height
        )
        for i in range(self._pix_map_y_steps + 1):
            temp_line = QtCore.QLineF(
                self._pix_map_width - self._pix_map_margin_right
                - self._pix_map_indicator_width,
                self._pix_map_margin_top + self._pix_map_y_step_height * i,
                self._pix_map_width - self._pix_map_margin_right,
                self._pix_map_margin_top + self._pix_map_y_step_height * i
            )
            pix_map_painter.drawLine(temp_line)
            #
            temp_rect = QtCore.QRectF(
                self._pix_map_margin_left,
                self._pix_map_margin_top/2.0 + self._pix_map_y_step_height * i,
                self._pix_map_text_rect_width,
                self._pix_map_text_rect_height
            )
            pix_map_painter.drawText(
                temp_rect,
                QtCore.Qt.AlignRight,
                QtCore.QString(str(the_max - price_step * i))
            )
        #
        pix_map_painter.drawLine(price_axis)
        #
        self.update()

    def paintEvent(self, event):
        painter = QtGui.QPainter()
        painter.begin(self)
        if self._pix_map:
            painter.drawPixmap(
                0, 0, self.width(), self.height(),
                self._pix_map,
                0, 0, self._pix_map_width, self._pix_map_height
            )
        painter.end()

################################################################################


class TimestampAxisView(QtGui.QWidget):
    """
    #
    """

    def __init__(self):
        super(TimestampAxisView, self).__init__()
        #
        # [en]
        # Background and foreground:
        #
        # [zh]
        # 背景色与前景色
        self_palette = QtGui.QPalette()
        self_palette.setColor(
            QtGui.QPalette.Background, QtGui.QColor(0, 0, 0)
        )
        self_palette.setColor(
            QtGui.QPalette.Foreground, QtGui.QColor(255, 0, 0)
        )
        self.setPalette(self_palette)
        #
        self._pix_map = QtGui.QPixmap(self.size())
        self._pix_map.fill(self, 0, 0)
        self.update()

    def paintEvent(self, event):
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.drawPixmap(
            0, 0, self.width(), self.height(),
            self._pix_map,
            0, 0, self._pix_map.width(), self._pix_map.height()
        )
        painter.end()

    def set_timestamps(self, timestamps):
        # TODO: codes;
        self._pix_map = QtGui.QPixmap(self.size())
        self._pix_map.fill(self, 0, 0)
        #
        size = len(timestamps)
        x_step = 1.0 * self.width() / size
        #
        painter = QtGui.QPainter(self._pix_map)
        painter.initFrom(self)
        timestamp_axis = QtCore.QLineF(
            x_step / 2.0, self.height() - 40,
            self.width() - x_step / 2.0, self.height() - 40
        )
        painter.drawLine(timestamp_axis)
        #
        for i in range(size + 1):
            painter.drawLine(
                x_step / 2.0 + x_step * i,
                self.height() - 40,
                x_step / 2.0 + x_step * i,
                self.height() - 40 + 5,
            )
        self.update()

################################################################################


class QuotationView(QtGui.QTableView):
    """
    """

    def __init__(
        self, data=None,
        horizontal_header_info=None,
        vertical_header_info=None
    ):
        super(QuotationView, self).__init__()
        self._model = QtGui.QStandardItemModel()
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
                    QtGui.QStandardItem(from_utf8(str(item)))
                    for item in each_row
                ]
            self._model.appendRow(each_row_items)
        #
        self._is_data_loaded = True
        self.show_header()

    def set_horizontal_header(self, horizontal_header_info):
        for i in range(len(horizontal_header_info)):
            self._model.setHeaderData(
                i, QtCore.Qt.Horizontal,
                QtCore.QVariant(from_utf8(str(horizontal_header_info[i])))
            )

    def set_vertical_header(self, vertical_header_info):
        for i in range(len(vertical_header_info)):
            self._model.setHeaderData(
                i, QtCore.Qt.Vertical,
                QtCore.QVariant(from_utf8(str(vertical_header_info[i])))
            )

    def set_data_color(self):
        for i in range(self._model.rowCount()):
            for j in range(self._model.columnCount()):
                self._model.setData(
                    self._model.index(i, j),
                    QtGui.QColor(QtCore.Qt.black),
                    QtCore.Qt.BackgroundRole
                )
                self._model.setData(
                    self._model.index(i, j),
                    QtGui.QColor(QtCore.Qt.yellow),
                    QtCore.Qt.ForegroundRole
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
        horizontal_header.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        vertical_header.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        horizontal_header.customContextMenuRequested.connect(
            self.popup_context_menu
        )
        vertical_header.customContextMenuRequested.connect(
            self.popup_context_menu
        )

    def popup_context_menu(self, position):
        menu = QtGui.QMenu()
        all_cols = []
        for i in range(self._model.columnCount()):
            all_cols.append(
                menu.addAction(
                    self._model.headerData(
                        i, QtCore.Qt.Horizontal
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
                        QtCore.QVariant(from_utf8(str(updated_data[i][j])))
                    )
                    self._model.setData(
                        self._model.index(i, j),
                        QtGui.QColor(QtCore.Qt.red), QtCore.Qt.BackgroundRole
                    )
                    self._model.setData(
                        self._model.index(i, j),
                        QtGui.QColor(QtCore.Qt.black), QtCore.Qt.ForegroundRole
                    )

    def is_data_loaded(self):
        return self._is_data_loaded

################################################################################


class KLineView(QtGui.QWidget):

    def __init__(self):
        super(KLineView, self).__init__()
        #
        # [zh]
        # 与所有数据相关的实例化变量
        self._data = None
        self._data_size = None
        self._data_start_idx = 0
        self._data_end_idx = 0
        self._the_max = 0.0
        self._the_min = 0.0
        #
        # [zh]
        # 与当前窗口显示的数据相关的实例化变量
        self._curr_data = None
        self._curr_data_size = None
        self._curr_span = 20
        self._curr_from_idx = 0
        self._curr_to_idx = 0
        #
        # [zh]
        # 控制当前窗口状态的实例化变量
        self._is_data_loaded = False
        self._is_average_line_shown = False
        self._cached_pix_map = None
        self._curr_x_step = 0
        self._curr_rect_width = 0
        self._curr_cursor_pos = QtCore.QPointF()
        self._click_status = 0
        #
        # [zh]
        # 预设的画图参考值
        self._CONST_SETTINGS = dict()
        self._CONST_SETTINGS['max_width'] = 30000
        self._CONST_SETTINGS['y_range'] = 4000
        self._CONST_SETTINGS['margin_top'] = 20
        self._CONST_SETTINGS['margin_bottom'] = 200
        #self._CONST_SETTINGS['y_range'] = self.height() - 10 - 20
        #self._CONST_SETTINGS['margin_top'] = 10
        #self._CONST_SETTINGS['margin_bottom'] = 20
        #
        #
        self._CONST_SETTINGS['x_step'] = 30
        self._CONST_SETTINGS['rect_width'] = 24
        self._CONST_SETTINGS['max_height'] = \
            self._CONST_SETTINGS['y_range'] \
            + self._CONST_SETTINGS['margin_top'] \
            + self._CONST_SETTINGS['margin_bottom']
        #
        # [en]
        # The calculation formula:
        #   MAX_K_LINE_SIZE * MIN_X_STEP = MAX_WIDTH
        #
        # [zh]
        # 参考值，计算公式如英文所示；
        self._CONST_SETTINGS['max_k_line_size'] = 6000
        self._CONST_SETTINGS['min_x_step'] = 5
        self._CONST_SETTINGS['min_rect_width'] = 3
        #
        self._pix_map = None
        #
        # [en]
        # Background and foreground:
        #
        # [zh]
        # 背景色与前景色
        self_palette = QtGui.QPalette()
        self_palette.setColor(
            QtGui.QPalette.Background, QtGui.QColor(0, 0, 0)
        )
        self_palette.setColor(
            QtGui.QPalette.Foreground, QtGui.QColor(255, 0, 0)
        )
        self.setPalette(self_palette)
        #
        # [zh]
        # 初始化
        self.init_pix_map()
        self.update()

    def paintEvent(self, event):
        #
        if self._is_average_line_shown:
            self.draw_average_line()
        #
        painter = QtGui.QPainter()
        painter.begin(self)
        #
        painter.drawPixmap(
            0, 0, self.width(), self.height(),
            self._pix_map,
            0, 0, self._pix_map.width(), self._pix_map.height()
        )
        #
        if self._click_status == 1:
            painter.setPen(QtGui.QPen(QtCore.Qt.darkCyan))
            #
            cursor_pos = QtGui.QCursor.pos()
            cursor_pos = self.mapFromGlobal(cursor_pos)
            #print(cursor_pos)
            cursor_x = cursor_pos.x()
            cursor_y = cursor_pos.y()
            painter.drawLine(cursor_x, 0, cursor_x, self.height())
            painter.drawLine(0, cursor_y, self.width(), cursor_y)
        elif self._click_status == 0:
            painter.eraseRect(0, 0, self.width(), self.height())
            painter.drawPixmap(
                0, 0, self.width(), self.height(),
                self._pix_map,
                0, 0, self._pix_map.width(), self._pix_map.height()
            )
        #
        painter.end()

    def init_pix_map(self):
        self._pix_map = QtGui.QPixmap(self.size())
        self._pix_map.load("_no_data.png")

    def load_k_line(self, data_file):
        self._data = get_k_line_data_by_path(data_file)[:2000]
        #self._data = get_k_line_data_by_path(data_file)
        #
        self._is_data_loaded = True
        #
        self._data_size = len(self._data)
        if self._data_size == 0:
            print(">>> No data!")
            return False
        self._data_start_idx = 0
        self._data_end_idx = self._data_size - 1
        self._curr_span = 20
        if self._data_size < self._curr_span:
            self._curr_from_idx = 0
            self._curr_to_idx = self._data_size - 1
            self._curr_span = self._data_size
        else:
            self._curr_from_idx = self._data_size - self._curr_span
            self._curr_to_idx = self._data_size - 1
            #
        #
        self.draw_data_on_pix_map()
        self.update()

    def draw_data_on_pix_map(self):
        temp_width = 0.0
        #
        x_step = self._CONST_SETTINGS['x_step']
        rect_width = self._CONST_SETTINGS['rect_width']
        y_range = self._CONST_SETTINGS['y_range']
        margin_top = self._CONST_SETTINGS['margin_top']
        #
        if self._curr_span <= 1000:
            temp_width = self._curr_span * x_step
            #
            self._curr_x_step = x_step
            self._curr_rect_width = rect_width
        elif self._curr_span <= 6000:
            x_step = math.ceil(
                self._CONST_SETTINGS['max_width'] / self._curr_span
            )
            rect_width = math.ceil(x_step * 0.8)
            temp_width = self._CONST_SETTINGS['max_width']
            #
            self._curr_x_step = x_step
            self._curr_rect_width = rect_width
        self._curr_data = self._data[self._curr_from_idx: self._curr_to_idx + 1]
        self._pix_map = QtGui.QPixmap(
            temp_width, self._CONST_SETTINGS['max_height']
        )
        self._pix_map.fill(self, 0, 0)
        pix_map_painter = QtGui.QPainter(self._pix_map)
        pix_map_painter.initFrom(self)
        #
        the_min, the_max = get_min_and_max_price(self._curr_data)
        the_min -= 1.0
        the_max += 1.0
        self._the_min = the_min
        self._the_max = the_max
        #
        k_line_rectangles_red = []
        k_line_rectangles_white = []
        k_line_lines_red = []
        k_line_lines_white = []
        k_line_rect_like_lines_red = []
        k_line_rect_like_lines_white = []
        #
        for i in list(xrange(self._curr_span)):
            #
            # Current row:
            curr_data = self._curr_data.ix[i]
            #
            # Open price:
            open_price = curr_data["open"]
            #
            # Close price:
            close_price = curr_data["close"]
            #
            # High price:
            high_price = curr_data["high"]
            #
            # Low price:
            low_price = curr_data["low"]
            #
            # Mid price:
            mid_price = (open_price + close_price) / 2.0
            #
            x_start = \
                (x_step - rect_width) / 2.0 + x_step * i
            y_start = \
                margin_top \
                + abs(max(open_price, close_price) - the_max) \
                / (the_max - the_min) * y_range
            y_height = \
                abs(
                    max(open_price, close_price) - min(open_price, close_price)
                ) \
                / (the_max - the_min) * y_range
            #
            curr_rect = QtCore.QRectF()
            curr_rect_like_line = RectLikeLine()
            #
            # High enough: rect
            if y_height >= 2:
                curr_rect.setRect(
                    x_start, y_start, rect_width, y_height
                )
            #
            # Otherwise: line instead of rect
            else:
                curr_rect_like_line.set_line_with_pen_width(
                    x_start, y_start,
                    x_start + rect_width, y_start,
                    y_height
                )
            #
            # The high & low price line:
            curr_line = QtCore.QLineF(
                x_step / 2.0 + x_step * i,
                margin_top
                + abs(high_price - the_max) / (the_max - the_min) * y_range,
                x_step / 2.0 + x_step * i,
                margin_top
                + abs(low_price - the_max) / (the_max - the_min) * y_range
            )
            #
            # Red:
            if close_price > open_price:
                pix_map_painter.fillRect(curr_rect, QtCore.Qt.red)
                k_line_rectangles_red.append(curr_rect)
                k_line_lines_red.append(curr_line)
                k_line_rect_like_lines_red.append(curr_rect_like_line)
            #
            # White:
            else:
                pix_map_painter.fillRect(curr_rect, QtCore.Qt.white)
                k_line_rectangles_white.append(curr_rect)
                k_line_lines_white.append(curr_line)
                k_line_rect_like_lines_white.append(curr_rect_like_line)
            #
        #
        # Red pen & white pen;
        pen_red = QtGui.QPen(QtCore.Qt.red)
        pix_map_painter.setPen(pen_red)
        pix_map_painter.drawRects(k_line_rectangles_red)
        pix_map_painter.drawLines(k_line_lines_red)
        pen_white = QtGui.QPen(QtCore.Qt.white)
        pix_map_painter.setPen(pen_white)
        pix_map_painter.drawRects(k_line_rectangles_white)
        pix_map_painter.drawLines(k_line_lines_white)
        #
        pen_red_for_rect_like_line = QtGui.QPen(QtCore.Qt.red)
        for each_rect_like_line in k_line_rect_like_lines_red:
            pen_red_for_rect_like_line.setWidth(
                each_rect_like_line.get_pen_width()
            )
            pix_map_painter.setPen(pen_red_for_rect_like_line)
            pix_map_painter.drawLine(
                each_rect_like_line.get_line()
            )
        pen_white_for_rect_like_line = QtGui.QPen(QtCore.Qt.white)
        for each_rect_like_line in k_line_rect_like_lines_white:
            pen_white_for_rect_like_line.setWidth(
                each_rect_like_line.get_pen_width()
            )
            pix_map_painter.setPen(pen_white_for_rect_like_line)
            pix_map_painter.drawLine(
                each_rect_like_line.get_line()
            )
        #
        # TODO: test;
        print(self.size())
        print(self._pix_map.size())

    def update_k_line(self, data_frame):
        data = data_frame.get_data_frame()
        the_last_datum = data.ix[0]
        self._data.ix[-1] = the_last_datum
        #
        self._curr_from_idx = self._data_end_idx - self._curr_span + 1
        self._curr_to_idx = self._data_end_idx
        #
        self.draw_data_on_pix_map()
        self.update()

    def append_k_line(self, data_frame):
        data = data_frame.get_data_frame()[:1]
        the_last_datum = data.ix[0]
        self._data = pd.concat([self._data, data])
        self._data_size += 1
        self._data_end_idx += 1
        #
        self._curr_from_idx = self._data_end_idx - self._curr_span + 1
        self._curr_to_idx = self._data_end_idx
        #
        self.draw_data_on_pix_map()
        self.update()

    def set_span(self, from_idx, to_idx):
        self._curr_from_idx = from_idx
        self._curr_to_idx = to_idx
        self._curr_span = self._curr_to_idx - self._curr_from_idx + 1
        #
        self.draw_data_on_pix_map()
        self.update()
        #
        self.emit(QtCore.SIGNAL("kLineSpanChanged()"))

    def draw_average_line(self):
        if not self._is_average_line_shown:
            return
        #
        #self._cached_pix_map = self._pix_map.copy(
        #    QtCore.QRect(0, 0, self._pix_map.width(), self._pix_map.height())
        #)
        #
        pix_map_painter = QtGui.QPainter(self._pix_map)
        pix_map_painter.initFrom(self)
        #
        y_range = self._CONST_SETTINGS['y_range']
        margin_top = self._CONST_SETTINGS['margin_top']
        x_step = self._curr_x_step
        rect_width = self._curr_rect_width
        points = list()
        for i in range(self._curr_from_idx, self._curr_to_idx + 1):
            curr_entry = self._data.ix[i]
            open_price = curr_entry['open']
            close_price = curr_entry['close']
            #
            mid_price = (open_price + close_price) / 2.0
            #
            points.append(
                QtCore.QPointF(
                    x_step / 2.0 + x_step * (i - self._curr_from_idx),
                    margin_top
                    + abs(mid_price - self._the_max)
                    / (self._the_max - self._the_min) * y_range
                )
            )
        pen_yellow = QtGui.QPen(QtCore.Qt.yellow)
        pen_yellow.setWidth(2)
        pix_map_painter.setPen(pen_yellow)
        # TODO: could draw, but pen width is not fit???
        #pix_map_painter.drawPolyline(*points)
        for i in range(len(points) - 1):
            pix_map_painter.drawLine(QtCore.QLineF(points[i], points[i+1]))

    def show_average_line(self):
        #
        print(">>> Show average line;")
        #
        self._is_average_line_shown = True  # This could be use to undo drawing;
        #
        self.update()

    def hide_average_line(self):
        #
        print(">>> Hide average line;")
        #
        self._is_average_line_shown = False
        self.draw_data_on_pix_map()
        #
        self.update()

    def mousePressEvent(self, event):
        if not self._is_data_loaded:
            return  # Nothing happened because of no data loaded
        #
        print(">>> Mouse pressed;")
        self._curr_cursor_pos = event.pos()
        #
        if self._is_data_loaded:
            self.setCursor(QtCore.Qt.OpenHandCursor)

    def mouseReleaseEvent(self, event):
        if not self._is_data_loaded:
            return  # Nothing happened because of no data loaded
        #
        print(">>> Mouse released;")
        #
        if self._is_data_loaded:
            if self._click_status == 0:
                self.setCursor(QtCore.Qt.ArrowCursor)
            elif self._click_status == 1:
                self.setCursor(QtCore.Qt.CrossCursor)
        self.update()

    def mouseMoveEvent(self, event):
        if not self._is_data_loaded:
            return  # Nothing happened because of no data loaded;
        #
        print(">>> Mouse moving;")
        #
        if self._click_status == 0:
            moved_pos = event.pos()
            curr_pos_x = moved_pos.x()
            if 0 <= curr_pos_x <= self.width():
                last_pos_x = self._curr_cursor_pos.x()
                one_step = 1.0 * self.width() / self._curr_span
                if abs(curr_pos_x - last_pos_x) >= one_step:
                    self._curr_cursor_pos = moved_pos
                    if curr_pos_x < last_pos_x:
                        if self._curr_to_idx < self._data_end_idx:
                            self.set_span(
                                self._curr_from_idx + 1,
                                self._curr_to_idx + 1
                            )
                        else:
                            QtGui.QMessageBox.about(
                                None,
                                "Right forbidden",
                                "Could not drag to right any more"
                            )
                    else:
                        if self._curr_from_idx > self._data_start_idx:
                            self.set_span(
                                self._curr_from_idx - 1,
                                self._curr_to_idx - 1
                            )
                        else:
                            QtGui.QMessageBox.about(
                                None,
                                "Left forbidden",
                                "Could not drag to left any more"
                            )
                    #
        elif self._click_status == 1:
            self.update()

    def mouseDoubleClickEvent(self, event):
        if not self._is_data_loaded:
            return  # Nothing happened because of no data loaded
        #
        print(">>> Double clicked;")
        #
        if self._click_status == 0:
            self._click_status = 1
            #
            self.setMouseTracking(True)
        elif self._click_status == 1:
            self._click_status = 0
            #
            self.setMouseTracking(False)

    def get_data(self):
        """
        Getter
        """
        return self._data

    def get_curr_data(self):
        """
        Getter
        """
        return self._curr_data

    def get_curr_span(self):
        """
        Getter
        """
        return self._curr_span

    def get_curr_from_idx(self):
        """
        Getter
        """
        return self._curr_from_idx

    def get_curr_to_idx(self):
        """
        Getter
        """
        return self._curr_to_idx

    def get_data_start_idx(self):
        """
        Getter
        """
        return self._data_start_idx

    def get_data_end_idx(self):
        """
        Getter
        """
        return self._data_end_idx

    def get_the_min(self):
        """
        Getter
        """
        return self._the_min

    def get_the_max(self):
        """
        Getter
        """
        return self._the_max

    def get_max_k_line_size(self):
        """
        Getter
        """
        return self._CONST_SETTINGS['max_k_line_size']

    def is_data_loaded(self):
        """
        Getter
        """
        return self._is_data_loaded

################################################################################


class ContainerView(QtGui.QMainWindow):

    def __init__(self):
        super(ContainerView, self).__init__()
        #
        main_splitter = QtGui.QSplitter(QtCore.Qt.Horizontal)
        left_splitter = QtGui.QSplitter(QtCore.Qt.Vertical)
        center_splitter = QtGui.QSplitter(QtCore.Qt.Vertical)
        right_splitter = QtGui.QSplitter(QtCore.Qt.Vertical)
        #
        main_splitter.addWidget(left_splitter)
        main_splitter.addWidget(center_splitter)
        main_splitter.addWidget(right_splitter)
        main_splitter.setSizes(
            [self.width()*0.15, self.width()*0.7, self.width()*0.15]
        )
        #
        price_axis_view = PriceAxisView()
        empty_widget = QtGui.QWidget()
        left_splitter.addWidget(price_axis_view)
        left_splitter.addWidget(empty_widget)
        left_splitter.setSizes(
            [self.height()*0.8, self.height()*0.2]
        )
        price_axis_view.setEnabled(False)
        #
        k_line_view = KLineView()
        timestamp_view = TimestampAxisView()
        k_line_slider = QxtSpanSlider()
        center_splitter.addWidget(k_line_view)
        center_splitter.addWidget(timestamp_view)
        center_splitter.addWidget(k_line_slider)
        center_splitter.setSizes(
            [self.height()*0.8, self.height()*0.15, self.height()*0.05]
        )
        #k_line_slider.setHandleMovementMode(2)  # No crossing, no overlapping;
        timestamp_view.setEnabled(False)
        k_line_slider.setEnabled(False)
        #
        info_view = InfoView()
        index_range_selector = IndexRangeSelector()
        right_splitter.addWidget(info_view)
        right_splitter.addWidget(index_range_selector)
        right_splitter.setSizes(
            [self.height()*0.85, self.height()*0.15]
        )
        index_range_selector.setEnabled(False)
        #
        self.setCentralWidget(main_splitter)
        #
        # Instance variables:
        self._k_line = k_line_view
        self._max_offset = 0
        self._k_line_slider = k_line_slider
        self._index_range_selector = index_range_selector
        self._price_axis_view = price_axis_view
        self._timestamp_view = timestamp_view
        #
        # sliderReleased is better than valueChanged:
        #   - will not delay;
        self._item_moved = 0
        QtCore.QObject.connect(
            k_line_slider,
            QtCore.SIGNAL("lowerPositionChanged(int)"),
            self.slide_lower_handle
        )
        QtCore.QObject.connect(
            k_line_slider,
            QtCore.SIGNAL("upperPositionChanged(int)"),
            self.slide_upper_handle
        )
        QtCore.QObject.connect(
            k_line_slider,
            QtCore.SIGNAL("sliderReleased()"),
            self.change_span
        )
        #
        #
        QtCore.QObject.connect(
            k_line_view,
            QtCore.SIGNAL("kLineSpanChanged()"),
            self.update_span_relevant_items
        )
        #
        #
        QtCore.QObject.connect(
            self,
            QtCore.SIGNAL("updateKLine()"),
            self.update_span_relevant_items
        )
        QtCore.QObject.connect(
            self,
            QtCore.SIGNAL("appendKLine()"),
            self.update_span_relevant_items
        )
        #
        #
        QtCore.QObject.connect(
            self._index_range_selector.get_spin_box_from(),
            QtCore.SIGNAL("valueChanged(int)"),
            self.update_curr_from_index
        )
        QtCore.QObject.connect(
            self._index_range_selector.get_spin_box_to(),
            QtCore.SIGNAL("valueChanged(int)"),
            self.update_curr_to_index
        )

    def load_data(self, data_file):
        self._k_line.load_k_line(data_file)
        #
        # [zh]
        # 载入数据后，启用双节点滚动条；
        self._k_line_slider.setRange(
            self._k_line.get_data_start_idx(),
            self._k_line.get_data_end_idx()
        )
        self._k_line_slider.setSpan(
            self._k_line.get_curr_from_idx(),
            self._k_line.get_curr_to_idx()
        )
        self._k_line_slider.setEnabled(True)
        #
        # [zh]
        # 载入数据后，启用价格坐标轴；
        self._price_axis_view.set_min_and_max_price(
            self._k_line.get_the_min(),
            self._k_line.get_the_max()
        )
        #
        # [zh]
        # 载入数据后，启用时间坐标轴；
        self._timestamp_view.set_timestamps(
            self._k_line.get_curr_data()
        )
        #
        self._index_range_selector.set_ranges(
            self._k_line.get_data_start_idx(),
            self._k_line.get_data_end_idx()
        )
        self._index_range_selector.set_values(
            self._k_line.get_curr_from_idx(),
            self._k_line.get_curr_to_idx()
        )
        self._index_range_selector.setEnabled(True)

    def update_k_line(self, updated_datum):
        self._k_line.update_k_line(updated_datum)
        #
        '''
        self._k_line_slider.setSpan(
            self._k_line.get_curr_from_idx(),
            self._k_line.get_curr_to_idx()
        )
        '''
        self.emit(QtCore.SIGNAL("updateKLine()"))

    def append_k_line(self, data_frame):
        self._k_line.append_k_line(data_frame)
        #
        '''
        self._k_line_slider.setSpan(
            self._k_line.get_curr_from_idx(),
            self._k_line.get_curr_to_idx()
        )
        '''
        self.emit(QtCore.SIGNAL("appendKLine()"))

    def slide_lower_handle(self, value):
        self._item_moved = 1

    def slide_upper_handle(self, value):
        self._item_moved = 2

    def change_span(self):
        lower_value = self._k_line_slider.lowerValue
        upper_value = self._k_line_slider.upperValue
        #
        max_k_line_size = self._k_line.get_max_k_line_size() - 1  # 6000 - 1
        if upper_value - lower_value > max_k_line_size:
            #
            if self._item_moved == 1:
                lower_value = upper_value - max_k_line_size
                #
                QtGui.QMessageBox.about(
                    None, "Lower", "Not so little"
                )
            elif self._item_moved == 2:
                upper_value = lower_value + max_k_line_size
                #
                QtGui.QMessageBox.about(
                    None, "Upper", "Not so much"
                )
        self._k_line.set_span(lower_value, upper_value)

    def update_span_relevant_items(self):
        #
        self._k_line_slider.setRange(
            self._k_line.get_data_start_idx(),
            self._k_line.get_data_end_idx()
        )
        self._k_line_slider.setSpan(
            self._k_line.get_curr_from_idx(),
            self._k_line.get_curr_to_idx()
        )
        #
        self._price_axis_view.set_min_and_max_price(
            self._k_line.get_the_min(),
            self._k_line.get_the_max()
        )
        #
        self._timestamp_view.set_timestamps(
            self._k_line.get_curr_data()
        )
        #
        self._index_range_selector.set_ranges(
            self._k_line.get_data_start_idx(),
            self._k_line.get_data_end_idx()
        )
        self._index_range_selector.set_values(
            self._k_line.get_curr_from_idx(),
            self._k_line.get_curr_to_idx()
        )

    def show_average_line(self):
        self._k_line.show_average_line()

    def hide_average_line(self):
        self._k_line.hide_average_line()

    def update_curr_from_index(self, curr_from_idx):
        '''
        temp_curr_from_idx = curr_from_idx
        if temp_curr_from_idx < \
                self._k_line.get_curr_to_idx() + 1 \
                - self._k_line.get_max_k_line_size():
            QtGui.QMessageBox.about(
                None,
                "From index",
                "Too small"
            )
            temp_curr_from_idx = \
                self._k_line.get_curr_to_idx() + 1 \
                - self._k_line.get_max_k_line_size()
        #
        self._k_line.set_span(
            temp_curr_from_idx,
            self._k_line.get_curr_to_idx()
        )
        '''
        pass

    def update_curr_to_index(self, curr_to_idx):
        '''
        temp_curr_to_idx = curr_to_idx
        if temp_curr_to_idx > \
                self._k_line.get_curr_from_idx() \
                + self._k_line.get_max_k_line_size() - 1:
            QtGui.QMessageBox(
                None,
                "To index",
                "Too big"
            )
            temp_curr_to_idx = \
                self._k_line.get_curr_from_idx() \
                + self._k_line.get_max_k_line_size() - 1
        #
        self._k_line.set_span(
            self._k_line.get_curr_from_idx(),
            temp_curr_to_idx
        )
        '''
        pass

    def get_k_line(self):
        #
        # TODO: should be removed?
        return self._k_line

################################################################################
# TODO: my refactoring main form;


class MainForm(QtGui.QWidget):
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
        #
        self.setWindowTitle(
            translate("Form", "TE-K-Line", None)
        )
        #
        # Size of MainForm:
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        #
        # Layout for MainForm:
        main_form_grid_layout = QtGui.QGridLayout(self)
        main_form_grid_layout.setContentsMargins(5, 0, 5, 5)
        #
        # Tab widget:
        tab_widget = QtGui.QTabWidget(self)
        tab_widget.setTabPosition(QtGui.QTabWidget.South)
        #
        # Menu bar:
        menu_bar_for_tab_widget = QtGui.QMenuBar(self)
        #
        # Add tab_widget & tab_k_line_menu_bar:
        main_form_grid_layout.addWidget(tab_widget, 1, 0, 1, 1)
        main_form_grid_layout.addWidget(menu_bar_for_tab_widget, 0, 0, 1, 1)
        #
        self.init_tab_widget(tab_widget)
        #
        self.init_menu_bar(menu_bar_for_tab_widget)
        #
        QtCore.QObject.connect(
            tab_widget,
            QtCore.SIGNAL("currentChanged(int)"),
            self.enable_menu_for_tab
        )

    def enable_menu_for_tab(self, idx):
        self._menus[idx].setEnabled(True)
        for i in range(len(self._menus)):
            if i != idx:
                self._menus[i].setEnabled(False)

    def init_tab_widget(self, tab_widget):
        #
        # Tab 'List':
        tab_list = QtGui.QWidget()
        tab_list_grid_layout = QtGui.QGridLayout(tab_list)
        tab_widget.addTab(tab_list, from_utf8("List"))
        quotation_view = QuotationView()
        self._quotation_view = quotation_view
        tab_list_grid_layout.addWidget(
            quotation_view,
            0, 0, 1, 1
        )
        #
        # Tab 'K-Line':
        tab_k_line_view = QtGui.QWidget()
        tab_k_line_view_grid_layout = QtGui.QGridLayout(tab_k_line_view)
        tab_widget.addTab(tab_k_line_view, from_utf8("K-Line"))
        container_view = ContainerView()
        self._container_view = container_view
        tab_k_line_view_grid_layout.addWidget(
            container_view,
            0, 0, 1, 1
        )
        QtCore.QObject.connect(
            container_view,
            QtCore.SIGNAL("updateSeries(PyQt_PyObject)"),
            container_view.update_k_line
        )
        QtCore.QObject.connect(
            container_view,
            QtCore.SIGNAL("appendDataFrame(PyQt_PyObject)"),
            container_view.append_k_line
        )

    def init_menu_bar(self, menu_bar):
        #
        # Add menu:
        menu_quotation_list = menu_bar.addMenu("Quotation-List")
        menu_new_k_line = menu_bar.addMenu("K-Line")
        #
        menu_new_k_line.setEnabled(False)
        self._menus.append(menu_quotation_list)
        self._menus.append(menu_new_k_line)
        #
        # Menu 'menu_quotation_list':
        action_list_load = menu_quotation_list.addAction("Load data")
        menu_quotation_list.addSeparator()
        action_update_list = menu_quotation_list.addAction("Update data")
        action_restore_list = menu_quotation_list.addAction("Restore data")
        action_remove_list = menu_quotation_list.addAction("Remove data")
        action_update_list.setEnabled(False)
        action_restore_list.setEnabled(False)
        action_remove_list.setEnabled(False)
        # TODO: the following method 'lambda' to pass extra parameters;
        QtCore.QObject.connect(
            action_list_load,
            QtCore.SIGNAL("triggered()"),
            lambda x=AllDataForTest.get_model_data0(),
            y=AllDataForTest.get_header_info0(),
            z=[action_update_list, action_restore_list, action_remove_list]:
            self.load_list_data(x, y, z)
        )
        QtCore.QObject.connect(
            action_update_list,
            QtCore.SIGNAL("triggered()"),
            lambda x=AllDataForTest.get_updated_model_data0():
            self.update_list_data(x)
        )
        QtCore.QObject.connect(
            action_restore_list,
            QtCore.SIGNAL("triggered()"),
            lambda x=AllDataForTest.get_model_data0(),
            y=AllDataForTest.get_header_info0():
            self.restore_list_data(x, y)
        )
        QtCore.QObject.connect(
            action_remove_list,
            QtCore.SIGNAL("triggered()"),
            lambda x=[
                action_update_list, action_restore_list, action_remove_list
            ]:
            self.remove_list_data(x)
        )
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
        QtCore.QObject.connect(
            new_action_load,
            QtCore.SIGNAL("triggered()"),
            lambda x=[
                new_action_update, new_action_append,
                new_action_show_average_line
            ]:
            self.new_load_k_line(x)
        )
        QtCore.QObject.connect(
            new_action_update,
            QtCore.SIGNAL("triggered()"),
            self.new_update_k_line
        )
        QtCore.QObject.connect(
            new_action_append,
            QtCore.SIGNAL("triggered()"),
            self.new_append_k_line
        )
        QtCore.QObject.connect(
            new_action_show_average_line,
            QtCore.SIGNAL("triggered()"),
            lambda x=[
                new_action_show_average_line, action_hide_average_line
            ]:
            self.show_average_line(x)
        )
        QtCore.QObject.connect(
            action_hide_average_line,
            QtCore.SIGNAL("triggered()"),
            lambda x=[
                new_action_show_average_line, action_hide_average_line
            ]:
            self.hide_average_line(x)
        )

    def load_list_data(self, data, horizontal_header_info, action_list):
        self._quotation_view.set_data(data)
        self._quotation_view.set_horizontal_header(horizontal_header_info)
        self._quotation_view.set_data_color()
        self._quotation_view.enable_header_sorting()
        self._quotation_view.enable_popup_context_menu()
        #
        for action in action_list:
            action.setEnabled(True)

    def update_list_data(self, updated_data):
        self._quotation_view.update_data(updated_data)

    def restore_list_data(self, data, horizontal_header_info):
        self._quotation_view.set_data(data)
        self._quotation_view.set_horizontal_header(horizontal_header_info)
        self._quotation_view.show_header()
        self._quotation_view.set_data_color()
        self._quotation_view.enable_header_sorting()
        self._quotation_view.enable_popup_context_menu()

    def remove_list_data(self, action_list):
        self._quotation_view.remove_data()
        #
        for action in action_list:
            action.setEnabled(False)

    def new_load_k_line(self, action_list):
        file_dialog = QtGui.QFileDialog(self)
        file_dialog.setWindowTitle("Load data file")
        file_dialog.setNameFilter("Data files (*.csv)")
        file_dialog.show()
        if file_dialog.exec_():  # Click 'Open' will return 1;
            data_file = file_dialog.selectedFiles()[0]
            print(">>> Selected file: " + data_file)
            self._container_view.load_data(data_file)
            for action in action_list:
                action.setEnabled(True)

    def new_update_k_line(self):
        # TODO: should be refactored as API;
        updated_data_frame = AppendedDataFrameModel(
            get_random_series_list_from(
                self._container_view.get_k_line().get_data()
            )
        )
        self._container_view.emit(
            QtCore.SIGNAL("updateSeries(PyQt_PyObject)"),
            updated_data_frame
        )

    def new_append_k_line(self):
        # TODO: should be refactored as API;
        appended_data_frame = AppendedDataFrameModel(
            get_random_series_list_from(
                self._container_view.get_k_line().get_data()
            )
        )
        self._container_view.emit(
            QtCore.SIGNAL("appendDataFrame(PyQt_PyObject)"),
            appended_data_frame
        )

    def show_average_line(self, x):
        self._container_view.show_average_line()
        #
        x[0].setEnabled(False)
        x[1].setEnabled(True)

    def hide_average_line(self, x):
        self._container_view.hide_average_line()
        #
        x[0].setEnabled(True)
        x[1].setEnabled(False)