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

################################################################################
# TODO: for test; to be removed;


class BlankArea(QtGui.QWidget):

    def __init__(self):
        super(BlankArea, self).__init__()
        #
        self_palette = QtGui.QPalette()
        self_palette.setColor(
            QtGui.QPalette.Background, QtGui.QColor(255, 0, 0)
        )
        self.setPalette(self_palette)
        self._pix_map = QtGui.QPixmap(self.size())
        self.refresh_pix_map()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.begin(self)
        painter.drawPixmap(0, 0, self._pix_map)
        painter.end()

    def refresh_pix_map(self):
        self._pix_map.fill(self, 0, 0)
        #
        self.update()

################################################################################
# TODO: to be used for showing info;


class InfoArea(QtGui.QWidget):

    def __init__(self):
        super(InfoArea, self).__init__()
        #
        self_palette = QtGui.QPalette()
        self_palette.setColor(
            QtGui.QPalette.Background, QtGui.QColor(0, 0, 255)
        )
        self.setPalette(self_palette)
        self.pix_map = QtGui.QPixmap(self.size())
        self.refresh_pix_map()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.begin(self)
        painter.drawPixmap(0, 0, self.pix_map)
        painter.end()

    def refresh_pix_map(self):
        self.pix_map.fill(self, 0, 0)
        #
        self.update()

################################################################################


class KLine(QtGui.QWidget):
    """
    Class: KLine
    """

    def __init__(
        self
    ):
        super(KLine, self).__init__()
        #
        # Init the instance variables:
        self._data = None
        self._data_size = 0
        self._sliced_models = None
        #
        # CONSTANT private variable:
        self._CONST_SETTINGS = dict()
        self._CONST_SETTINGS['max_sliced_data_size'] = 1000
        self._CONST_SETTINGS['max_width'] = 30000.0
        self._CONST_SETTINGS['y_range'] = 4000.0
        self._CONST_SETTINGS['margin_top'] = 20.0
        self._CONST_SETTINGS['margin_bottom'] = 20.0
        self._CONST_SETTINGS['max_height'] = \
            self._CONST_SETTINGS['y_range'] \
            + self._CONST_SETTINGS['margin_top'] \
            + self._CONST_SETTINGS['margin_bottom']
        self._CONST_SETTINGS['x_step'] = 30.0
        self._CONST_SETTINGS['rect_width'] = 24.0
        #
        # Background and foreground:
        self_palette = QtGui.QPalette()
        self_palette.setColor(
            QtGui.QPalette.Background, QtGui.QColor(0, 0, 0)
        )
        self_palette.setColor(
            QtGui.QPalette.Foreground, QtGui.QColor(255, 0, 0)
        )
        self.setPalette(self_palette)
        #
        self._curr_start_idx = 0
        self._curr_end_idx = 0
        self._the_min = 0
        self._the_max = 0
        self._is_data_loaded = False

    def load_data(self, data_file):
        self._data = get_k_line_data_by_path(data_file)[0: 2000]
        #self._data = get_k_line_data_by_path(data_file)
        #
        self._sliced_models = list()
        #
        data_size = len(self._data)
        self._data_size = data_size
        #
        # TODO: try idx:
        self._curr_start_idx = data_size - 20
        self._curr_end_idx = data_size - 1
        #
        max_sliced_data_size = self._CONST_SETTINGS['max_sliced_data_size']
        slice_size = int(math.ceil(1.0 * data_size / max_sliced_data_size))
        for i in range(slice_size):
            temp_data = \
                self._data[i*max_sliced_data_size: (i+1)*max_sliced_data_size]
            temp_data_size = len(temp_data)
            from_idx = i*max_sliced_data_size
            to_idx = i*max_sliced_data_size + temp_data_size - 1
            print(str(from_idx) + " - " + str(to_idx))
            self._sliced_models.append(
                SlicedPixMapModel(self._data, from_idx, to_idx)
            )
        self.draw_sliced_models()
        #
        self._is_data_loaded = True

    def draw_sliced_models(self):
        the_min, the_max = get_min_and_max_price(self._data)
        self._the_min = the_min - 5.0
        self._the_max = the_max + 5.0
        for each_model in self._sliced_models:
            self.draw_each_model(each_model)
        self.update()

    def draw_each_model(self, each_model):
        temp_data = each_model.get_data()
        temp_size = each_model.get_size()
        max_width = (temp_size + 1) * self._CONST_SETTINGS['x_step']
        max_height = self._CONST_SETTINGS['max_height']
        pix_map = QtGui.QPixmap(max_width, max_height)
        #
        pix_map.fill(self, 0, 0)
        pix_map_painter = QtGui.QPainter(pix_map)
        pix_map_painter.initFrom(self)
        #
        x_step = self._CONST_SETTINGS['x_step']
        rect_width = self._CONST_SETTINGS['rect_width']
        y_range = self._CONST_SETTINGS['y_range']
        margin_top = self._CONST_SETTINGS['margin_top']
        #
        k_line_rectangles_red = []
        k_line_rectangles_white = []
        k_line_lines_red = []
        k_line_lines_white = []
        k_line_rect_like_lines_red = []
        k_line_rect_like_lines_white = []
        #
        for i in list(xrange(temp_size)):
            #
            # Current row:
            curr_data = temp_data.ix[i]
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
            x_start = \
                (x_step - rect_width) / 2.0 + i * x_step
            y_start = \
                margin_top \
                + abs(max(open_price, close_price) - self._the_max) \
                / (self._the_max - self._the_min) * y_range
            y_height = \
                abs(
                    max(open_price, close_price) - min(open_price, close_price)
                ) \
                / (self._the_max - self._the_min) * y_range
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
                # TODO: set a min height;
                y_height = 2
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
                + abs(high_price - self._the_max)
                / (self._the_max - self._the_min) * y_range,
                x_step / 2.0 + x_step * i,
                margin_top
                + abs(low_price - self._the_max)
                / (self._the_max - self._the_min) * y_range
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
        each_model.set_pix_map(pix_map)

    def paintEvent(self, event):
        if not self._is_data_loaded:
            return
        #
        painter = QtGui.QPainter()
        painter.begin(self)
        #
        #print(">>> painting")
        curr_start_idx = self._curr_start_idx
        curr_end_idx = self._curr_end_idx
        max_sliced_data_size = self._CONST_SETTINGS['max_sliced_data_size']
        x_step = self._CONST_SETTINGS['x_step']
        margin_top = self._CONST_SETTINGS['margin_top']
        y_range = self._CONST_SETTINGS['y_range']
        from_slice_idx = int(curr_start_idx / max_sliced_data_size)
        to_slice_idx = int(curr_end_idx / max_sliced_data_size)
        inside_from_idx = curr_start_idx % max_sliced_data_size
        inside_to_idx = curr_end_idx % max_sliced_data_size
        #
        if from_slice_idx == to_slice_idx:
            temp_min, temp_max = get_min_and_max_price(
                self._data[curr_start_idx: curr_end_idx+1]
            )
            temp_min -= 5
            temp_max += 5
            painter.drawPixmap(
                QtCore.QRectF(0, 0, self.width(), self.height()),
                self._sliced_models[from_slice_idx].get_pix_map(),
                QtCore.QRectF(
                    inside_from_idx * x_step,
                    margin_top
                    + abs(temp_max - self._the_max)
                    / (self._the_max - self._the_min) * y_range,
                    (inside_to_idx - inside_from_idx + 1) * x_step,
                    (temp_max - temp_min)
                    / (self._the_max - self._the_min) * y_range
                )
            )
        else:
            #
            #print(complete_slice_indexes)
            complete_slice_indexes = range(from_slice_idx+1, to_slice_idx)
            complete_size = len(complete_slice_indexes)
            #
            temp_min, temp_max = get_min_and_max_price(
                self._data[int(curr_start_idx): int(curr_end_idx)+1]
            )
            temp_min -= 5
            temp_max += 5
            #
            first_width = [max_sliced_data_size - inside_from_idx]
            last_width = [inside_to_idx+1]
            middles = list()
            for i in range(complete_size):
                middles.append(max_sliced_data_size)
            all_width = first_width + middles + last_width
            all_width_ratio = [
                1.0 * x / sum(all_width) for x in all_width
            ]
            all_offset_ratio = [0.0] + all_width_ratio[:-1]
            for i in range(1, len(all_offset_ratio)):
                all_offset_ratio[i] += all_offset_ratio[i-1]
            #
            windowed_pix_map_model_list = list()
            #
            first_windowed_pix_map_model = WindowedPixMapModel()
            first_windowed_pix_map_model.set_pix_map(
                self._sliced_models[from_slice_idx].get_pix_map()
            )
            first_windowed_pix_map_model.set_widget_window(
                all_offset_ratio[0] * self.width(),
                0,
                all_width_ratio[0] * self.width(),
                self.height()
            )
            first_windowed_pix_map_model.set_pix_map_window(
                inside_from_idx * x_step,
                margin_top
                + abs(temp_max - self._the_max)
                / (self._the_max - self._the_min) * y_range,
                (max_sliced_data_size - inside_from_idx) * x_step,
                (temp_max - temp_min)
                / (self._the_max - self._the_min) * y_range
            )
            #
            last_windowed_pix_map_model = WindowedPixMapModel()
            last_windowed_pix_map_model.set_pix_map(
                self._sliced_models[to_slice_idx].get_pix_map()
            )
            last_windowed_pix_map_model.set_widget_window(
                all_offset_ratio[-1] * self.width(),
                0,
                all_width_ratio[-1] * self.width(),
                self.height()
            )
            last_windowed_pix_map_model.set_pix_map_window(
                0,
                margin_top
                + abs(temp_max - self._the_max)
                / (self._the_max - self._the_min) * y_range,
                (inside_to_idx + 1) * x_step,
                (temp_max - temp_min)
                / (self._the_max - self._the_min) * y_range
            )
            #
            for curr_idx in complete_slice_indexes:
                temp_windowed_pix_map_model = WindowedPixMapModel()
                temp_windowed_pix_map_model.set_pix_map(
                    self._sliced_models[curr_idx].get_pix_map()
                )
                temp_windowed_pix_map_model.set_widget_window(
                    all_offset_ratio[curr_idx - from_slice_idx] * self.width(),
                    0,
                    all_width_ratio[curr_idx - from_slice_idx] * self.width(),
                    self.height()
                )
                temp_windowed_pix_map_model.set_pix_map_window(
                    0,
                    margin_top
                    + abs(temp_max - self._the_max)
                    / (self._the_max - self._the_min) * y_range,
                    max_sliced_data_size * x_step,
                    (temp_max - temp_min)
                    / (self._the_max - self._the_min) * y_range
                )
                windowed_pix_map_model_list.append(temp_windowed_pix_map_model)
            #
            windowed_pix_map_model_list = \
                [first_windowed_pix_map_model] \
                + windowed_pix_map_model_list \
                + [last_windowed_pix_map_model]
            #
            for each in windowed_pix_map_model_list:
                painter.drawPixmap(
                    each.get_widget_window(),
                    each.get_pix_map(),
                    each.get_pix_map_window()
                )
            #
        #
        painter.end()

    def update_the_last_k_line(self, data_frame):
        # If temp_max OR temp_min is out of self._the_max, self._the_min:
        #   - re-draw all pix-maps;
        # If in the range:
        #   - locate the last pix-map;
        #   - draw the last k-line;
        #
        data = data_frame.get_data_frame()
        the_last_datum = data.ix[0]
        self._data.ix[-1] = the_last_datum
        #
        temp_min, temp_max = \
            get_min_and_max_price(data[:1])
        temp_min -= 5
        temp_max += 5
        #
        if temp_min >= self._the_min and temp_max <= self._the_max:
            print(">>> Updating scenario: in-range")
            #
            x_step = self._CONST_SETTINGS['x_step']
            y_range = self._CONST_SETTINGS['y_range']
            rect_width = self._CONST_SETTINGS['rect_width']
            margin_top = self._CONST_SETTINGS['margin_top']
            #
            the_last_sliced_model = self._sliced_models[-1]
            the_last_pix_map = the_last_sliced_model.get_pix_map()
            the_last_inside_idx = the_last_sliced_model.get_size() - 1
            #
            pix_map_painter = QtGui.QPainter(the_last_pix_map)
            pix_map_painter.initFrom(self)
            #
            # To erase rectangle:
            #   extend to -1 and +1 to avoid potential erasing problem;
            erase_rect = QtCore.QRectF(
                the_last_inside_idx * x_step - 1, 0,
                x_step + 2, the_last_pix_map.height()
            )
            pix_map_painter.eraseRect(erase_rect)
            #
            open_price = the_last_datum['open']
            close_price = the_last_datum['close']
            high_price = the_last_datum['high']
            low_price = the_last_datum['low']
            #
            x_start = \
                the_last_inside_idx * x_step + (x_step - rect_width) / 2.0
            y_start = \
                margin_top \
                + abs(max(open_price, close_price) - self._the_max) \
                / (self._the_max - self._the_min) * y_range
            y_height = \
                (max(open_price, close_price) - min(open_price, close_price)) \
                / (self._the_max - self._the_min) * y_range
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
                # TODO: set a min height;
                y_height = 2
                curr_rect_like_line.set_line_with_pen_width(
                    x_start, y_start,
                    x_start + rect_width, y_start,
                    y_height
                )
            #
            # The high & low price line:
            curr_line = QtCore.QLineF(
                x_start + rect_width / 2.0,
                margin_top
                + abs(high_price - self._the_max)
                / (self._the_max - self._the_min) * y_range,
                x_start + rect_width / 2.0,
                margin_top
                + abs(low_price - self._the_max)
                / (self._the_max - self._the_min) * y_range
            )
            #
            if close_price > open_price:
                pix_map_painter.fillRect(curr_rect, QtCore.Qt.red)
                pen_red = QtGui.QPen(QtCore.Qt.red)
                pix_map_painter.setPen(pen_red)
                pix_map_painter.drawRect(curr_rect)
                pix_map_painter.drawLine(curr_line)
                #
                pen_red.setWidth(
                    curr_rect_like_line.get_pen_width()
                )
                pix_map_painter.setPen(pen_red)
                pix_map_painter.drawLine(
                    curr_rect_like_line.get_line()
                )
            else:
                pix_map_painter.fillRect(curr_rect, QtCore.Qt.white)
                pen_white = QtGui.QPen(QtCore.Qt.white)
                pix_map_painter.setPen(pen_white)
                pix_map_painter.drawRect(curr_rect)
                pix_map_painter.drawLine(curr_line)
                #
                pen_white.setWidth(
                    curr_rect_like_line.get_pen_width()
                )
                pix_map_painter.setPen(pen_white)
                pix_map_painter.drawLine(
                    curr_rect_like_line.get_line()
                )
        else:
            print(">>> Updating scenario: out-of-range")
            #
            self.draw_sliced_models()
        #
        # Fix bug: add the following two lines to fix the problem, which is
        #   that when updating, pix map is not located correctly;
        self._curr_start_idx = self._data_size - self.get_curr_span()
        self._curr_end_idx = self._data_size - 1
        self.update()

    def append_one_k_line(self, data_frame):
        # If another pix-map is needed:
        #   - create new pix-map; AND:
        #   - if temp_max OR temp_min is out of range, re-draw all;
        #   - if in the range, just add the new pix-map to list;
        # If enough space:
        #   - consider temp_max OR temp_min to decide whether to re-draw or not;
        #
        data = data_frame.get_data_frame()[:1]
        the_last_datum = data.ix[0]
        self._data = pd.concat([self._data, data])
        self._data_size += 1
        #
        max_sliced_data_size = self._CONST_SETTINGS['max_sliced_data_size']  #
        temp_min, temp_max = get_min_and_max_price(data)
        temp_min -= 5
        temp_max += 5
        #
        if int(math.ceil(1.0 * self._data_size / max_sliced_data_size)) \
                > int(len(self._sliced_models)):
            #
            self._sliced_models.append(
                SlicedPixMapModel(
                    self._data, self._data_size-1, self._data_size-1
                )
            )
            #
            if temp_min >= self._the_min and temp_max <= self._the_max:
                #
                print(">>> Appending scenario: new pix-map & in-range")
                #
                x_step = self._CONST_SETTINGS['x_step']
                y_range = self._CONST_SETTINGS['y_range']
                rect_width = self._CONST_SETTINGS['rect_width']
                margin_top = self._CONST_SETTINGS['margin_top']
                max_height = self._CONST_SETTINGS['max_height']
                max_width = self._CONST_SETTINGS['max_width']
                #
                the_last_sliced_model = self._sliced_models[-1]
                pix_map = \
                    QtGui.QPixmap(
                        max_width,
                        max_height
                    )
                pix_map.fill(self, 0, 0)
                the_last_sliced_model.set_pix_map(
                    pix_map
                )
                the_last_pix_map = the_last_sliced_model.get_pix_map()
                the_last_inside_idx = the_last_sliced_model.get_size() - 1
                #
                pix_map_painter = QtGui.QPainter(the_last_pix_map)
                pix_map_painter.initFrom(self)
                #
                open_price = the_last_datum['open']
                close_price = the_last_datum['close']
                high_price = the_last_datum['high']
                low_price = the_last_datum['low']
                #
                x_start = \
                    the_last_inside_idx * x_step + (x_step - rect_width) / 2.0
                y_start = \
                    margin_top \
                    + abs(max(open_price, close_price) - self._the_max) \
                    / (self._the_max - self._the_min) * y_range
                y_height = \
                    (max(open_price, close_price) - min(open_price, close_price)) \
                    / (self._the_max - self._the_min) * y_range
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
                    # TODO: set a min height;
                    y_height = 2
                    curr_rect_like_line.set_line_with_pen_width(
                        x_start, y_start,
                        x_start + rect_width, y_start,
                        y_height
                    )
                #
                # The high & low price line:
                curr_line = QtCore.QLineF(
                    x_start + rect_width / 2.0,
                    margin_top
                    + abs(high_price - self._the_max)
                    / (self._the_max - self._the_min) * y_range,
                    x_start + rect_width / 2.0,
                    margin_top
                    + abs(low_price - self._the_max)
                    / (self._the_max - self._the_min) * y_range
                )
                #
                if close_price > open_price:
                    pix_map_painter.fillRect(curr_rect, QtCore.Qt.red)
                    pen_red = QtGui.QPen(QtCore.Qt.red)
                    pix_map_painter.setPen(pen_red)
                    pix_map_painter.drawRect(curr_rect)
                    pix_map_painter.drawLine(curr_line)
                    #
                    pen_red.setWidth(
                        curr_rect_like_line.get_pen_width()
                    )
                    pix_map_painter.setPen(pen_red)
                    pix_map_painter.drawLine(
                        curr_rect_like_line.get_line()
                    )
                else:
                    pix_map_painter.fillRect(curr_rect, QtCore.Qt.white)
                    pen_white = QtGui.QPen(QtCore.Qt.white)
                    pix_map_painter.setPen(pen_white)
                    pix_map_painter.drawRect(curr_rect)
                    pix_map_painter.drawLine(curr_line)
                    #
                    pen_white.setWidth(
                        curr_rect_like_line.get_pen_width()
                    )
                    pix_map_painter.setPen(pen_white)
                    pix_map_painter.drawLine(
                        curr_rect_like_line.get_line()
                    )
                #
                #self._curr_start_idx = self._data_size - self.get_curr_span()
                #self._curr_end_idx = self._data_size - 1
            else:
                #
                self.draw_sliced_models()
        else:
            #
            if temp_min >= self._the_min and temp_max <= self._the_max:
                #
                print(">>> Appending scenario: enough space & in-range")
                #
                x_step = self._CONST_SETTINGS['x_step']
                y_range = self._CONST_SETTINGS['y_range']
                rect_width = self._CONST_SETTINGS['rect_width']
                margin_top = self._CONST_SETTINGS['margin_top']
                #
                the_last_sliced_model = self._sliced_models[-1]
                the_last_pix_map = the_last_sliced_model.get_pix_map()
                the_last_sliced_model.set_to_idx(
                    the_last_sliced_model.get_to_idx() + 1
                )
                the_last_inside_idx = the_last_sliced_model.get_size() - 1
                #
                pix_map_painter = QtGui.QPainter(the_last_pix_map)
                pix_map_painter.initFrom(self)
                #
                open_price = the_last_datum['open']
                close_price = the_last_datum['close']
                high_price = the_last_datum['high']
                low_price = the_last_datum['low']
                #
                x_start = \
                    the_last_inside_idx * x_step + (x_step - rect_width) / 2.0
                y_start = \
                    margin_top \
                    + abs(max(open_price, close_price) - self._the_max) \
                    / (self._the_max - self._the_min) * y_range
                y_height = \
                    (max(open_price, close_price) - min(open_price, close_price)) \
                    / (self._the_max - self._the_min) * y_range
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
                    # TODO: set a min height;
                    y_height = 2
                    curr_rect_like_line.set_line_with_pen_width(
                        x_start, y_start,
                        x_start + rect_width, y_start,
                        y_height
                    )
                #
                # The high & low price line:
                curr_line = QtCore.QLineF(
                    x_start + rect_width / 2.0,
                    margin_top
                    + abs(high_price - self._the_max)
                    / (self._the_max - self._the_min) * y_range,
                    x_start + rect_width / 2.0,
                    margin_top
                    + abs(low_price - self._the_max)
                    / (self._the_max - self._the_min) * y_range
                )
                #
                if close_price > open_price:
                    pix_map_painter.fillRect(curr_rect, QtCore.Qt.red)
                    pen_red = QtGui.QPen(QtCore.Qt.red)
                    pix_map_painter.setPen(pen_red)
                    pix_map_painter.drawRect(curr_rect)
                    pix_map_painter.drawLine(curr_line)
                    #
                    pen_red.setWidth(
                        curr_rect_like_line.get_pen_width()
                    )
                    pix_map_painter.setPen(pen_red)
                    pix_map_painter.drawLine(
                        curr_rect_like_line.get_line()
                    )
                else:
                    pix_map_painter.fillRect(curr_rect, QtCore.Qt.white)
                    pen_white = QtGui.QPen(QtCore.Qt.white)
                    pix_map_painter.setPen(pen_white)
                    pix_map_painter.drawRect(curr_rect)
                    pix_map_painter.drawLine(curr_line)
                    #
                    pen_white.setWidth(
                        curr_rect_like_line.get_pen_width()
                    )
                    pix_map_painter.setPen(pen_white)
                    pix_map_painter.drawLine(
                        curr_rect_like_line.get_line()
                    )
                #
                #self._curr_start_idx = self._data_size - self.get_curr_span()
                #self._curr_end_idx = self._data_size - 1
            else:
                #
                self.draw_sliced_models()
        #
        self._curr_start_idx = self._data_size - self.get_curr_span()
        self._curr_end_idx = self._data_size - 1
        self.update()

    def show_average_line(self):
        """
        [en]

        [zh]
        平均线绘制
        """
        #
        print(">>> Show average line")
        #
        max_sliced_data_size = self._CONST_SETTINGS['max_sliced_data_size']
        x_step = self._CONST_SETTINGS['x_step']
        y_range = self._CONST_SETTINGS['y_range']
        margin_top = self._CONST_SETTINGS['margin_top']
        #
        for i in range(len(self._sliced_models)):
            curr_sliced_model = self._sliced_models[i]
            curr_pix_map = curr_sliced_model.get_pix_map()
            points = []
            for j in range(
                curr_sliced_model.get_from_idx(),
                curr_sliced_model.get_to_idx() + 1
            ):
                curr_entry = self._data.ix[j]
                #
                open_price = curr_entry['open']
                close_price = curr_entry['close']
                #
                mid_price = (open_price + close_price) / 2.0
                #
                temp_idx = j % max_sliced_data_size
                #
                points.append(
                    QtCore.QPointF(
                        temp_idx * x_step + x_step / 2.0,
                        margin_top
                        + abs(mid_price - self._the_max)
                        / (self._the_max - self._the_min) * y_range
                    )
                )
            painter = QtGui.QPainter(curr_pix_map)
            painter.initFrom(self)
            pen_yellow = QtGui.QPen(QtCore.Qt.yellow)
            painter.setPen(pen_yellow)
            # TODO: could draw, but pen width is not fit???
            painter.drawPolyline(*points)
        #
        self.update()

    def get_curr_start_idx(self):
        return self._curr_start_idx

    def get_curr_end_idx(self):
        return self._curr_end_idx

    def get_curr_span(self):
        return self._curr_end_idx - self._curr_start_idx + 1

    def get_data_size(self):
        return self._data_size

    # TODO: should be removed later;
    def get_data(self):
        return self._data

    def set_curr_start_idx(self, curr_start_idx):
        self._curr_start_idx = curr_start_idx
        self.update()

    def set_curr_end_idx(self, curr_end_idx):
        self._curr_end_idx = curr_end_idx
        self.update()

    def set_idx(self, curr_start_idx, curr_end_idx):
        self._curr_start_idx = curr_start_idx
        self._curr_end_idx = curr_end_idx
        self.update()

################################################################################


class KLineContainer(QtGui.QMainWindow):
    """
    """

    def __init__(self):
        super(KLineContainer, self).__init__()
        #
        main_splitter = QtGui.QSplitter(QtCore.Qt.Horizontal)
        left_splitter = QtGui.QSplitter(QtCore.Qt.Vertical)
        right_splitter = QtGui.QSplitter(QtCore.Qt.Vertical)
        #
        main_splitter.addWidget(left_splitter)
        main_splitter.addWidget(right_splitter)
        main_splitter.setSizes(
            [self.width()*0.8, self.width()*0.2]
        )
        #
        k_line = KLine()
        k_line_slider = QxtSpanSlider()
        left_splitter.addWidget(k_line)
        left_splitter.addWidget(k_line_slider)
        left_splitter.setSizes(
            [self.height()*0.9, self.height()*0.1]
        )
        '''
        QtCore.QObject.connect(
            k_line_slider,
            QtCore.SIGNAL("lowerPositionChanged(int)"),
            self.change_lower_value
        )
        QtCore.QObject.connect(
            k_line_slider,
            QtCore.SIGNAL("upperPositionChanged(int)"),
            self.change_upper_value
        )
        '''
        QtCore.QObject.connect(
            k_line_slider,
            QtCore.SIGNAL("sliderReleased()"),
            self.change_value
        )
        k_line_slider.setEnabled(False)
        #
        info_area = InfoArea()
        index_range_selector = IndexRangeSelector()
        k_line_size_setter = KLineSizeSetter()
        right_splitter.addWidget(info_area)
        right_splitter.addWidget(index_range_selector)
        right_splitter.addWidget(k_line_size_setter)
        right_splitter.setSizes(
            [self.height()*0.8, self.height()*0.1, self.height()*0.1]
        )
        index_range_selector.setEnabled(False)
        k_line_size_setter.setEnabled(False)
        #
        self.setCentralWidget(main_splitter)
        #
        self._k_line = k_line
        self._max_offset = 0
        self._k_line_slider = k_line_slider
        self._k_line_size_setter = k_line_size_setter

    def slide_to_offset(self, x_offset):
        self._k_line.refresh_pix_map(x_offset)
        self._k_line_slider.setValue(x_offset)

    def refresh_k_line_size(self, k_line_size):
        self._k_line.set_curr_width(
            k_line_size * self._pix_map_settings.get_pix_map_x_step_width()
        )
        self._k_line.set_curr_k_line_size(k_line_size)
        self._k_line.update()

    def get_k_line(self):
        return self._k_line

    def get_max_offset(self):
        return self._max_offset

    def get_k_line_slider(self):
        return self._k_line_slider

    def update_k_line(self, series):
        self._k_line.update_the_last_k_line(series)
        #
        curr_span = self._k_line.get_curr_span()
        print(curr_span)
        self._k_line_slider.setSpan(
            self._k_line_slider.maximum() - curr_span + 1,
            self._k_line_slider.maximum()
        )

    def append_k_line(self, data_frame):
        self._k_line.append_one_k_line(data_frame)
        #
        self._k_line_slider.setRange(
            0,
            self._k_line.get_data_size() - 1
        )
        #
        # Fix bug:
        #   add span settings to set the value of slider;
        curr_span = self._k_line.get_curr_span()
        print(curr_span)
        self._k_line_slider.setSpan(
            self._k_line_slider.maximum() - curr_span + 1,
            self._k_line_slider.maximum()
        )

    def load_data(self, data_file):
        """
        Load
        """
        self._k_line.load_data(data_file)
        #
        self._k_line_slider.setRange(
            0,
            self._k_line.get_data_size() - 1
        )
        self._k_line_slider.setSpan(
            self._k_line.get_curr_start_idx(),
            self._k_line.get_curr_end_idx()
        )
        self._k_line_slider.setEnabled(True)

    def change_lower_value(self, lower_value):
        print("Lower value: " + str(lower_value))
        self._k_line.set_curr_start_idx(lower_value)

    def change_upper_value(self, upper_value):
        print("Upper value: " + str(upper_value))
        self._k_line.set_curr_end_idx(upper_value)

    def change_value(self):
        print("Lower value: " + str(self._k_line_slider.lowerValue))
        print("Upper value: " + str(self._k_line_slider.upperValue))
        self._k_line.set_idx(
            self._k_line_slider.lowerValue,
            self._k_line_slider.upperValue
        )

    def show_average_line(self):
        self._k_line.show_average_line()

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
        self._data = None
        self._data_size = None
        #
        self._curr_data = None
        self._curr_data_size = None
        #
        self._window_k_line_size = 20
        #
        self._min_offset = 0
        self._max_offset = 0
        self._curr_offset = 0
        self._min_setter = 1
        self._max_setter = 999
        #
        self._CONST_SETTINGS = dict()
        self._CONST_SETTINGS['max_width'] = 30000
        self._CONST_SETTINGS['y_range'] = 600
        self._CONST_SETTINGS['margin_top'] = 20
        self._CONST_SETTINGS['margin_bottom'] = 20
        self._CONST_SETTINGS['x_step'] = 30
        self._CONST_SETTINGS['rect_width'] = 24
        self._CONST_SETTINGS['max_k_line_size'] = 999
        self._CONST_SETTINGS['max_height'] = \
            self._CONST_SETTINGS['y_range'] \
            + self._CONST_SETTINGS['margin_top'] \
            + self._CONST_SETTINGS['margin_bottom']
        #
        self._pix_map = None
        #
        # Background and foreground:
        self_palette = QtGui.QPalette()
        self_palette.setColor(
            QtGui.QPalette.Background, QtGui.QColor(0, 0, 0)
        )
        self_palette.setColor(
            QtGui.QPalette.Foreground, QtGui.QColor(255, 0, 0)
        )
        self.setPalette(self_palette)
        #
        self.init_pix_map()
        self.update()

    def paintEvent(self, event):
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.drawPixmap(
            0, 0, self.width(), self.height(),
            self._pix_map,
            0, 0, self._pix_map.width(), self._pix_map.height()
        )
        #print(self._pix_map.width())
        #print(self._pix_map.height())
        painter.end()

    def init_pix_map(self):
        self._pix_map = QtGui.QPixmap(self.size())
        self._pix_map.load("_no_data.png")

    def load_k_line(self, data_file):
        self._data = get_k_line_data_by_path(data_file)
        self._data_size = len(self._data)
        temp_width = \
            (self._data_size + 1) * self._CONST_SETTINGS['x_step'] \
            if self._data_size < self._window_k_line_size \
            else \
            (self._window_k_line_size+1) * self._CONST_SETTINGS['x_step']
        self._curr_data_size = \
            self._data_size if self._data_size < self._window_k_line_size \
            else self._window_k_line_size
        self._curr_data = self._data[0-self._curr_data_size:]
        self._pix_map = QtGui.QPixmap(
            temp_width, self._CONST_SETTINGS['max_height']
        )
        #
        self._max_offset = \
            0 if self._data_size < self._window_k_line_size \
            else self._data_size - self._window_k_line_size
        self._curr_offset = self._max_offset
        self._max_setter = \
            self._data_size \
            if self._data_size < self._CONST_SETTINGS['max_k_line_size'] \
            else self._CONST_SETTINGS['max_k_line_size']
        #
        self.draw_data_on_pix_map()
        self.update()

    def draw_data_on_pix_map(self):
        self._pix_map.fill(self, 0, 0)
        pix_map_painter = QtGui.QPainter(self._pix_map)
        pix_map_painter.initFrom(self)
        #
        the_min, the_max = get_min_and_max_price(self._curr_data)
        the_min -= 5.0
        the_max += 5.0
        #
        x_step = self._CONST_SETTINGS['x_step']
        rect_width = self._CONST_SETTINGS['rect_width']
        y_range = self._CONST_SETTINGS['y_range']
        margin_top = self._CONST_SETTINGS['margin_top']
        #
        k_line_rectangles_red = []
        k_line_rectangles_white = []
        k_line_lines_red = []
        k_line_lines_white = []
        k_line_rect_like_lines_red = []
        k_line_rect_like_lines_white = []
        #
        for i in list(xrange(self._curr_data_size)):
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
            x_start = \
                x_step * (i + 1) \
                - rect_width / 2
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
            if y_height >= 5:
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
                x_step * (i + 1),
                margin_top
                + abs(high_price - the_max) / (the_max - the_min) * y_range,
                x_step * (i + 1),
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
        self.update()

    def get_min_offset(self):
        """
        Getter
        """
        return self._min_offset

    def get_max_offset(self):
        """
        Getter
        """
        return self._max_offset

    def get_min_setter(self):
        """
        Getter
        """
        return self._min_setter

    def get_max_setter(self):
        """
        Getter
        """
        return self._max_setter

    def get_curr_data_size(self):
        return self._curr_data_size

    def get_curr_offset(self):
        return self._curr_offset

    def set_curr_offset(self, offset):
        self._curr_offset = offset
        self._curr_data = self._data[offset:offset+self._curr_data_size]
        #
        self.draw_data_on_pix_map()
        self.update()

    def set_k_line_size(self, k_line_size):
        #
        self._curr_data_size = k_line_size
        self._curr_data = self._data[0-self._curr_data_size:]
        #
        temp_width = \
            (k_line_size+1) * self._CONST_SETTINGS['x_step']
        self._pix_map = QtGui.QPixmap(
            temp_width, self._CONST_SETTINGS['max_height']
        )
        #
        self._max_offset = self._data_size - k_line_size
        self._curr_offset = self._max_offset
        #
        self.draw_data_on_pix_map()
        self.update()

    def get_data(self):
        return self._data

    def update_k_line(self, updated_datum):
        self._data.ix[-1] = updated_datum
        self._curr_offset = self._max_offset
        #
        self.draw_data_on_pix_map()
        self.update()

    def append_k_line(self, appended_data):
        self._data = pd.concat([self._data, appended_data])
        self._data_size = len(self._data)
        temp_width = \
            (self._curr_data_size+1) * self._CONST_SETTINGS['x_step']
        self._curr_data = self._data[0-self._curr_data_size:]
        self._pix_map = QtGui.QPixmap(
            temp_width, self._CONST_SETTINGS['max_height']
        )
        #
        self._max_offset += 1
        self._curr_offset = self._max_offset
        self._max_setter = \
            self._data_size \
            if self._data_size < self._CONST_SETTINGS['max_k_line_size'] \
            else self._CONST_SETTINGS['max_k_line_size']
        #
        self.draw_data_on_pix_map()
        self.update()

################################################################################


class ContainerView(QtGui.QMainWindow):

    def __init__(self):
        super(ContainerView, self).__init__()
        #
        main_splitter = QtGui.QSplitter(QtCore.Qt.Horizontal)
        left_splitter = QtGui.QSplitter(QtCore.Qt.Vertical)
        right_splitter = QtGui.QSplitter(QtCore.Qt.Vertical)
        #
        main_splitter.addWidget(left_splitter)
        main_splitter.addWidget(right_splitter)
        main_splitter.setSizes(
            [self.width()*0.8, self.width()*0.2]
        )
        #
        k_line_view = KLineView()
        k_line_slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        left_splitter.addWidget(k_line_view)
        left_splitter.addWidget(k_line_slider)
        left_splitter.setSizes(
            [self.height()*0.9, self.height()*0.1]
        )
        k_line_slider.setEnabled(False)
        #
        info_area = InfoArea()
        k_line_size_setter = KLineSizeSetter()
        right_splitter.addWidget(info_area)
        right_splitter.addWidget(k_line_size_setter)
        right_splitter.setSizes(
            [self.height()*0.8, self.height()*0.2]
        )
        k_line_size_setter.setEnabled(False)
        #
        self.setCentralWidget(main_splitter)
        #
        # Instance variables:
        self._k_line = k_line_view
        self._max_offset = 0
        self._k_line_slider = k_line_slider
        self._k_line_size_setter = k_line_size_setter
        #
        # sliderReleased is better than valueChanged:
        #   - will not delay;
        QtCore.QObject.connect(
            k_line_slider,
            QtCore.SIGNAL("sliderReleased()"), self.slide_to_offset
        )
        QtCore.QObject.connect(
            k_line_size_setter.get_spin_box_size(),
            QtCore.SIGNAL("valueChanged(int)"), self.set_to_size
        )

    def load_k_line(self, data_file):
        self._k_line.load_k_line(data_file)
        #
        if self._k_line.get_min_offset() < self._k_line.get_max_offset():
            self._k_line_slider.setMinimum(self._k_line.get_min_offset())
            self._k_line_slider.setMaximum(self._k_line.get_max_offset())
            self._k_line_slider.setPageStep(1)
            self._k_line_slider.setValue(self._k_line.get_curr_offset())
            self._k_line_slider.setEnabled(True)
        #
        self._k_line_size_setter.set_size_min(self._k_line.get_min_setter())
        self._k_line_size_setter.set_size_max(self._k_line.get_max_setter())
        self._k_line_size_setter.set_curr_value(
            self._k_line.get_curr_data_size()
        )
        self._k_line_size_setter.setEnabled(True)

    def slide_to_offset(self):
        self._k_line.set_curr_offset(self._k_line_slider.value())

    def set_to_size(self, k_line_size):
        self._k_line.set_k_line_size(k_line_size)
        #
        if self._k_line.get_min_offset() < self._k_line.get_max_offset():
            self._k_line_slider.setMinimum(self._k_line.get_min_offset())
            self._k_line_slider.setMaximum(self._k_line.get_max_offset())
            self._k_line_slider.setPageStep(1)
            self._k_line_slider.setValue(self._k_line.get_curr_offset())
            self._k_line_slider.setEnabled(True)

    def get_k_line(self):
        return self._k_line

    def update_k_line(self, updated_datum):
        self._k_line.update_k_line(updated_datum)
        self._k_line_slider.setValue(self._k_line.get_curr_offset())

    def append_k_line(self, appended_data):
        self._k_line.append_k_line(appended_data)
        self._k_line_slider.setValue(self._k_line.get_curr_offset())
        #
        if self._k_line.get_min_offset() < self._k_line.get_max_offset():
            self._k_line_slider.setMinimum(self._k_line.get_min_offset())
            self._k_line_slider.setMaximum(self._k_line.get_max_offset())
            self._k_line_slider.setPageStep(1)
            self._k_line_slider.setValue(self._k_line.get_curr_offset())
            self._k_line_slider.setEnabled(True)
        #
        self._k_line_size_setter.set_size_min(self._k_line.get_min_setter())
        self._k_line_size_setter.set_size_max(self._k_line.get_max_setter())
        self._k_line_size_setter.set_curr_value(
            self._k_line.get_curr_data_size()
        )

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
        self._k_line_container = None
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
        tab_k_line = QtGui.QWidget()
        tab_k_line_grid_layout = QtGui.QGridLayout(tab_k_line)
        tab_widget.addTab(tab_k_line, from_utf8("K-Line"))
        k_line_container = KLineContainer()
        self._k_line_container = k_line_container
        tab_k_line_grid_layout.addWidget(
            k_line_container,
            0, 0, 1, 1
        )
        QtCore.QObject.connect(
            k_line_container,
            QtCore.SIGNAL("updateSeries(PyQt_PyObject)"),
            k_line_container.update_k_line
        )
        QtCore.QObject.connect(
            k_line_container,
            QtCore.SIGNAL("appendDataFrame(PyQt_PyObject)"),
            k_line_container.append_k_line
        )
        #
        #
        tab_k_line_view = QtGui.QWidget()
        tab_k_line_view_grid_layout = QtGui.QGridLayout(tab_k_line_view)
        tab_widget.addTab(tab_k_line_view, from_utf8("New K-Line"))
        container_view = ContainerView()
        self._container_view = container_view
        tab_k_line_view_grid_layout.addWidget(
            container_view,
            0, 0, 1, 1
        )

    def init_menu_bar(self, menu_bar):
        #
        # Add menu:
        menu_quotation_list = menu_bar.addMenu("Quotation-List")
        menu_k_line = menu_bar.addMenu("K-Line")
        menu_new_k_line = menu_bar.addMenu("New K-Line")
        menu_k_line.setEnabled(False)
        menu_new_k_line.setEnabled(False)
        self._menus.append(menu_quotation_list)
        self._menus.append(menu_k_line)
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
        # Menu 'menu_k_line':
        action_load = menu_k_line.addAction("Load data file")
        menu_k_line.addSeparator()
        action_update = menu_k_line.addAction("Update last k-line")
        action_append = menu_k_line.addAction("Append one k-line")
        menu_k_line.addSeparator()
        action_show_average_line = menu_k_line.addAction("Show average line")
        action_update.setEnabled(False)
        action_append.setEnabled(False)
        action_show_average_line.setEnabled(False)
        #
        QtCore.QObject.connect(
            action_load,
            QtCore.SIGNAL("triggered()"),
            lambda x=[
                action_update, action_append, action_show_average_line
            ]: self.load_data(x)
        )
        QtCore.QObject.connect(
            action_update,
            QtCore.SIGNAL("triggered()"),
            self.update_k_line
        )
        QtCore.QObject.connect(
            action_append,
            QtCore.SIGNAL("triggered()"),
            self.append_k_line
        )
        QtCore.QObject.connect(
            action_show_average_line,
            QtCore.SIGNAL("triggered()"),
            lambda x = action_show_average_line: self.show_average_line(x)
        )
        #
        # Menu for 'new k-line':
        new_action_load = menu_new_k_line.addAction("Load data file")
        menu_new_k_line.addSeparator()
        new_action_update = menu_new_k_line.addAction("Update last k-line")
        new_action_append = menu_new_k_line.addAction("Append one k-line")
        new_action_update.setEnabled(False)
        new_action_append.setEnabled(False)
        #
        QtCore.QObject.connect(
            new_action_load,
            QtCore.SIGNAL("triggered()"),
            lambda x=[new_action_update, new_action_append]:
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

    def update_k_line(self):
        # TODO: should be refactored as API;
        updated_data_frame = AppendedDataFrameModel(
            get_random_series_list_from(
                self._k_line_container.get_k_line().get_data()
            )
        )
        self._k_line_container.emit(
            QtCore.SIGNAL("updateSeries(PyQt_PyObject)"),
            updated_data_frame
        )

    def append_k_line(self):
        # TODO: should be refactored as API;
        appended_data_frame = AppendedDataFrameModel(
            get_random_series_list_from(
                self._k_line_container.get_k_line().get_data()
            )
        )
        self._k_line_container.emit(
            QtCore.SIGNAL("appendDataFrame(PyQt_PyObject)"),
            appended_data_frame
        )

    def load_data(self, action_list):
        file_dialog = QtGui.QFileDialog(self)
        file_dialog.setWindowTitle("Load data file")
        file_dialog.setNameFilter("Data files (*.csv)")
        file_dialog.show()
        if file_dialog.exec_():  # Click 'Open' will return 1;
            data_file = file_dialog.selectedFiles()[0]
            print(">>> Selected file: " + data_file)
            self._k_line_container.load_data(data_file)
            for action in action_list:
                action.setEnabled(True)

    def show_average_line(self, self_action):
        self._k_line_container.show_average_line()
        #
        self_action.setEnabled(False)

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
        updated_datum = \
            get_random_series_from(
                self._container_view.get_k_line().get_data()
            )
        #
        self._container_view.update_k_line(updated_datum)

    def new_append_k_line(self):
        # TODO: should be refactored as API;
        appended_data = \
            get_random_series_list_from(
                self._container_view.get_k_line().get_data()
            )
        #
        self._container_view.append_k_line(appended_data)