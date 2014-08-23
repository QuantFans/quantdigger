__author__ = 'TeaEra'

from PyQt4 import QtGui
from PyQt4 import QtCore
import pandas as pd

from QuantUtils import from_utf8
from QuantUtils import translate
from QuantUtils import get_k_line_data_by_path
from QuantUtils import get_min_and_max_price
from QuantUtils import get_random_series_from
from QuantUtils import get_random_series_list_from

from QuantModel import RectLikeLine
from QuantModel import PixMapSettings

from QuantTestData import AllDataForTest

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
        self, pix_map_settings
    ):
        super(KLine, self).__init__()
        #
        # Init the instance variables:
        self._k_line_data = None
        self._k_line_data_index = None
        self.pix_map = None
        self._is_loaded = False
        #
        # Get settings:
        self._settings = pix_map_settings.get_settings()
        # Background and foreground:
        self_palette = QtGui.QPalette()
        self_palette.setColor(
            QtGui.QPalette.Background, QtGui.QColor(0, 0, 0)
        )
        self_palette.setColor(
            QtGui.QPalette.Foreground, QtGui.QColor(255, 0, 0)
        )
        self.setPalette(self_palette)
        # Init pix map:
        self.start_index = 0
        self._curr_x_offset = 0
        self._curr_y_offset = 0
        self._curr_k_line_size = 20
        self._curr_width = \
            self._curr_k_line_size * self._settings['pix_map_x_step_width']
        self._curr_height = self.height()
        self.pix_map = QtGui.QPixmap(
            self._settings['pix_map_max_width'],
            self._settings['pix_map_max_height']
        )
        self.the_max = 0.0
        self.the_min = 0.0
        # TODO: should adapt to actions like update and append;
        self._curr_the_max = 0.0
        self._curr_the_min = 0.0
        # TODO: this is counted manually by now, should be dynamic;
        self._curr_k_line_index = 0
        self._valid_k_line_data = None
        #
        self.temp_layout = QtGui.QGridLayout()
        self.temp_layout.addWidget(
            QtGui.QLabel(
                "Please click the 'Load data file' "
                + "from menu bar 'K-Line'"
            ),
            0, 1, 1, 1
        )
        self.setLayout(self.temp_layout)

    # TODO: for test; to be removed;
    def get_data(self):
        return self._k_line_data

    def get_curr_width(self):
        return self._curr_width

    def init_pix_map(self):
        self.pix_map.fill(self, 0, 0)
        pix_map_painter = QtGui.QPainter(self.pix_map)
        pix_map_painter.initFrom(self)
        #
        self.init_k_lines_on_pix_map(pix_map_painter)
        #
        self.update()

    def init_k_lines_on_pix_map(self, painter):
        #
        pix_map_margin_top = self._settings['pix_map_margin_top']
        pix_map_margin_left = self._settings['pix_map_margin_left']
        pix_map_x_history_size = \
            self._settings['pix_map_x_history_size']
        #
        temp_k_line_data = \
            self._k_line_data[
                self.start_index: self.start_index + pix_map_x_history_size]
        self._valid_k_line_data = temp_k_line_data
        #
        the_min, the_max = get_min_and_max_price(temp_k_line_data)
        the_min -= 5.0
        the_max += 5.0
        self.the_min = the_min
        self.the_max = the_max
        #
        self.draw_k_lines(
            painter,
            temp_k_line_data,
            pix_map_margin_left, pix_map_margin_top,
            the_max, the_min)

    def draw_k_lines(
            self, painter,
            temp_k_line_data,
            x_from, y_from,
            the_max, the_min
    ):
        #
        pix_map_x_step_width = self._settings['pix_map_x_step_width']
        pix_map_k_line_rect_width = \
            self._settings['pix_map_k_line_rect_width']
        y_range = self._settings['pix_map_y_range']
        #
        k_line_rectangles_red = []
        k_line_rectangles_white = []
        k_line_lines_red = []
        k_line_lines_white = []
        k_line_rect_like_lines_red = []
        k_line_rect_like_lines_white = []
        #
        for i in list(xrange(len(temp_k_line_data))):
            #
            # Current row:
            curr_data = temp_k_line_data.ix[i]
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
                x_from + pix_map_x_step_width * (i + 1) \
                - pix_map_k_line_rect_width / 2
            y_start = \
                y_from \
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
                    x_start, y_start, pix_map_k_line_rect_width, y_height
                )
            #
            # Otherwise: line instead of rect
            else:
                curr_rect_like_line.set_line_with_pen_width(
                    x_start, y_start,
                    x_start + pix_map_k_line_rect_width, y_start,
                    y_height
                )
            #
            # The high & low price line:
            curr_line = QtCore.QLineF(
                x_from + pix_map_x_step_width * (i + 1),
                y_from
                + abs(high_price - the_max) / (the_max - the_min) * y_range,
                x_from + pix_map_x_step_width * (i + 1),
                y_from
                + abs(low_price - the_max) / (the_max - the_min) * y_range
            )
            #
            # Red:
            if close_price > open_price:
                painter.fillRect(curr_rect, QtCore.Qt.red)
                k_line_rectangles_red.append(curr_rect)
                k_line_lines_red.append(curr_line)
                k_line_rect_like_lines_red.append(curr_rect_like_line)
            #
            # White:
            else:
                painter.fillRect(curr_rect, QtCore.Qt.white)
                k_line_rectangles_white.append(curr_rect)
                k_line_lines_white.append(curr_line)
                k_line_rect_like_lines_white.append(curr_rect_like_line)
        #
        # Red pen & white pen;
        pen_red = QtGui.QPen(QtCore.Qt.red)
        painter.setPen(pen_red)
        painter.drawRects(k_line_rectangles_red)
        painter.drawLines(k_line_lines_red)
        pen_white = QtGui.QPen(QtCore.Qt.white)
        painter.setPen(pen_white)
        painter.drawRects(k_line_rectangles_white)
        painter.drawLines(k_line_lines_white)
        #
        pen_red_for_rect_like_line = QtGui.QPen(QtCore.Qt.red)
        for each_rect_like_line in k_line_rect_like_lines_red:
            pen_red_for_rect_like_line.setWidth(
                each_rect_like_line.get_pen_width()
            )
            painter.setPen(pen_red_for_rect_like_line)
            painter.drawLine(
                each_rect_like_line.get_line()
            )
        pen_white_for_rect_like_line = QtGui.QPen(QtCore.Qt.white)
        for each_rect_like_line in k_line_rect_like_lines_white:
            pen_white_for_rect_like_line.setWidth(
                each_rect_like_line.get_pen_width()
            )
            painter.setPen(pen_white_for_rect_like_line)
            painter.drawLine(
                each_rect_like_line.get_line()
            )
        #

    def paintEvent(self, event):
        #
        if self._is_loaded:
            painter = QtGui.QPainter(self)
            painter.begin(self)
            temp_the_min, temp_the_max = \
                get_min_and_max_price(
                    self._valid_k_line_data[
                        self._curr_k_line_index:
                        self._curr_k_line_index + self._curr_k_line_size
                    ]
                )
            self._curr_y_offset = \
                self._settings['pix_map_margin_top'] \
                + abs(temp_the_max - self.the_max) \
                / (self.the_max - self.the_min) \
                * self._settings['pix_map_y_range'] \
                - 5
            self._curr_height = \
                (temp_the_max - temp_the_min) / (self.the_max - self.the_min) \
                * self._settings['pix_map_y_range'] \
                + 10
            painter.drawPixmap(
                0.0, 0.0,
                self.width(), self.height(),
                self.pix_map,
                self._curr_x_offset, self._curr_y_offset,
                self._curr_width
                + self._settings['pix_map_x_step_width'] / 2.0 + 1,
                self._curr_height
            )
            painter.end()

    def refresh_pix_map(self, x_offset):
        #
        self._curr_x_offset = x_offset
        # TODO: rough calculation;
        self._curr_k_line_index = \
            int((x_offset - self._settings['pix_map_margin_left']) / 50.0)
        self.update()

    # Update last datum:
    def update_the_last_k_line(self, the_last_datum):
        #
        y_range = self._settings['pix_map_y_range']
        pix_map_margin_top = self._settings['pix_map_margin_top']
        pix_map_margin_left = self._settings['pix_map_margin_left']
        pix_map_x_step_width = self._settings['pix_map_x_step_width']
        pix_map_x_history_size = \
            self._settings['pix_map_x_history_size']
        pix_map_k_line_rect_width = \
            self._settings['pix_map_k_line_rect_width']
        #
        pix_map_painter = QtGui.QPainter(self.pix_map)
        pix_map_painter.initFrom(self)
        #
        open_price = the_last_datum['open']
        close_price = the_last_datum['close']
        high_price = the_last_datum['high']
        low_price = the_last_datum['low']
        #
        x_start = \
            pix_map_margin_left \
            + pix_map_x_step_width * pix_map_x_history_size
        # TODO: now just make the assumption, price is in the y_range;
        # TODO: thus self.the_min & self.the_max is valid;
        y_start = \
            pix_map_margin_top \
            + abs(max(open_price, close_price) - self.the_max) \
            / (self.the_max - self.the_min) * y_range
        y_height = \
            abs(
                max(open_price, close_price) - min(open_price, close_price)
            ) \
            / (self.the_max - self.the_min) * y_range
        #
        # To erase rectangle:
        #   extend to +1 and -1 to avoid potential erasing problem;
        erase_rect = QtCore.QRectF(
            x_start - pix_map_k_line_rect_width/2 - 1, 0,
            pix_map_k_line_rect_width+2, self._settings['pix_map_max_height']
        )
        pix_map_painter.eraseRect(erase_rect)
        #
        # To draw the new rectangle:
        new_rect = QtCore.QRectF(
            x_start - pix_map_k_line_rect_width/2, y_start,
            pix_map_k_line_rect_width, y_height)
        new_line = QtCore.QLineF(
            x_start,
            pix_map_margin_top
            + abs(high_price - self.the_max) / (self.the_max - self.the_min)
            * y_range,
            x_start,
            pix_map_margin_top
            + abs(low_price - self.the_max) / (self.the_max - self.the_min)
            * y_range
        )
        #
        if close_price > open_price:
            red_pen = QtGui.QPen(QtCore.Qt.red)
            pix_map_painter.setPen(red_pen)
            pix_map_painter.fillRect(new_rect, QtCore.Qt.red)
            pix_map_painter.drawRect(new_rect)
            pix_map_painter.drawLine(new_line)
        else:
            white_pen = QtGui.QPen(QtCore.Qt.white)
            pix_map_painter.setPen(white_pen)
            pix_map_painter.fillRect(new_rect, QtCore.Qt.white)
            pix_map_painter.drawRect(new_rect)
            pix_map_painter.drawLine(new_line)
        #
        # TODO: modify self._valid_k_line_data to adapt to the new data;
        self._valid_k_line_data.ix[-1] = the_last_datum
        #
        self.update()

    # Append a new k-line:
    def append_one_k_line(self, new_k_line_datum):
        #
        pix_map_painter = QtGui.QPainter(self.pix_map)
        pix_map_painter.initFrom(self)
        x_from = \
            self._settings['pix_map_margin_left'] \
            + self._settings['pix_map_x_step_width']\
            * self._settings['pix_map_x_history_size']
        y_from = \
            self._settings['pix_map_margin_top']
        # TODO: now just make the assumption, price is in the y_range;
        # TODO: thus self.the_min & self.the_max is valid;
        self.draw_k_lines(
            pix_map_painter,
            new_k_line_datum,
            x_from, y_from,
            self.the_max, self.the_min

        )
        #
        # TODO: adaptive!
        concatenated_temp_data = \
            pd.concat([self._valid_k_line_data, new_k_line_datum])
        self._valid_k_line_data = concatenated_temp_data
        #
        self._curr_k_line_size += 1
        self._settings['pix_map_x_history_size'] += 1
        #
        self.update()

    def get_curr_x_offset(self):
        return self._curr_x_offset

    def get_curr_k_line_size(self):
        return self._curr_k_line_size

    def set_curr_k_line_size(self, curr_k_line_size):
        self._curr_k_line_size = curr_k_line_size

    def set_curr_width(self, curr_width):
        """
        Setter for 'self._curr_width';
        """
        self._curr_width = curr_width

    def load_data_from_file(self, data_file):
        """
        Load k-line data from given file;
        """
        # About k-line data:
        self._k_line_data = get_k_line_data_by_path(data_file)
        self._k_line_data_index = self._k_line_data.index
        #self.k_line_data_size = len(self._k_line_data)
        self.pix_map = QtGui.QPixmap(
            self._settings['pix_map_max_width'],
            self._settings['pix_map_max_height']
        )
        self._is_loaded = True
        #
        for i in reversed(range(self.temp_layout.count())):
            self.temp_layout.itemAt(i).widget().setParent(None)
        #
        self.init_pix_map()

    def load_k_line(self, data_file):
        self.load_data_from_file(data_file)

################################################################################


class KLineContainer(QtGui.QMainWindow):
    """
    """

    def __init__(self, pix_map_settings):
        super(KLineContainer, self).__init__()
        #
        self._pix_map_settings = pix_map_settings
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
        k_line = KLine(
            pix_map_settings
        )
        k_line_slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        k_line_slider.setEnabled(False)
        left_splitter.addWidget(k_line)
        left_splitter.addWidget(k_line_slider)
        left_splitter.setSizes(
            [self.height()*0.9, self.height()*0.1]
        )
        #
        info_area = InfoArea()
        index_range_selector = IndexRangeSelector()
        k_line_size_setter = KLineSizeSetter()
        index_range_selector.setEnabled(False)
        k_line_size_setter.setEnabled(False)
        QtCore.QObject.connect(
            k_line_size_setter.get_spin_box_size(),
            QtCore.SIGNAL("valueChanged(int)"), self.refresh_k_line_size
        )
        right_splitter.addWidget(info_area)
        right_splitter.addWidget(index_range_selector)
        right_splitter.addWidget(k_line_size_setter)
        right_splitter.setSizes(
            [self.height()*0.8, self.height()*0.1, self.height()*0.1]
        )
        #
        self.setCentralWidget(main_splitter)
        #
        max_offset = \
            pix_map_settings.get_pix_map_max_width() - k_line.get_curr_width()
        k_line_slider.setMinimum(0)
        k_line_slider.setMaximum(max_offset)
        k_line_slider.setPageStep(pix_map_settings.get_pix_map_x_step_width())
        QtCore.QObject.connect(
            k_line_slider,
            QtCore.SIGNAL("valueChanged(int)"), self.slide_to_offset
        )
        #
        self._k_line = k_line
        self._max_offset = max_offset
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

    def update_k_line(self, updated_data):
        self._k_line.update_the_last_k_line(updated_data)
        self._k_line_slider.setValue(self._max_offset)
        self.slide_to_offset(self._max_offset)

    def append_k_line(self, appended_data):
        self._k_line.append_one_k_line(appended_data)
        self._k_line_slider.setValue(self._max_offset)
        self.slide_to_offset(self._max_offset)

    def load_k_line(self, data_file):
        self._k_line.load_k_line(data_file)
        #
        self._k_line_size_setter.set_size_min(1)
        self._k_line_size_setter.set_size_max(1000)
        self._k_line_size_setter.set_curr_value(
            self._k_line.get_curr_k_line_size()
        )
        self._k_line_size_setter.setEnabled(True)
        #
        self.slide_to_offset(self._max_offset)
        self._k_line_slider.setEnabled(True)

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
        print(self._pix_map.width())
        print(self._pix_map.height())
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
        pix_map_settings = PixMapSettings()
        k_line_container = KLineContainer(pix_map_settings)
        self._k_line_container = k_line_container
        tab_k_line_grid_layout.addWidget(
            k_line_container,
            0, 0, 1, 1
        )
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
        action_update.setEnabled(False)
        action_append.setEnabled(False)
        #
        QtCore.QObject.connect(
            action_load,
            QtCore.SIGNAL("triggered()"),
            lambda x=[action_update, action_append]: self.load_k_line(x)
        )
        QtCore.QObject.connect(
            action_update,
            QtCore.SIGNAL("triggered()"), self.update_k_line
        )
        QtCore.QObject.connect(
            action_append,
            QtCore.SIGNAL("triggered()"),
            lambda x=[action_append]: self.append_k_line(x)
        )
        #
        # Menu 'menu_k_line':
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
        updated_data = \
            get_random_series_from(
                self._k_line_container.get_k_line().get_data()
            )
        #
        self._k_line_container.update_k_line(updated_data)

    def append_k_line(self, action_list):
        # TODO: should be refactored as API;
        appended_data = \
            get_random_series_list_from(
                self._k_line_container.get_k_line().get_data()
            )
        #
        self._k_line_container.append_k_line(appended_data)
        #
        for action in action_list:
            action.setEnabled(False)

    def load_k_line(self, action_list):
        file_dialog = QtGui.QFileDialog(self)
        file_dialog.setWindowTitle("Load data file")
        file_dialog.setNameFilter("Data files (*.csv)")
        file_dialog.show()
        if file_dialog.exec_():  # Click 'Open' will return 1;
            data_file = file_dialog.selectedFiles()[0]
            print(">>> Selected file: " + data_file)
            self._k_line_container.load_k_line(data_file)
            for action in action_list:
                action.setEnabled(True)

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
            self._container_view.load_k_line(data_file)
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