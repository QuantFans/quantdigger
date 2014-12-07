#_*_ coding: utf-8 _*_
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import pandas as pd
from QuantUtils import get_k_line_data_by_path
from QuantUtils import get_min_and_max_price

class KLineView(QWidget):

    def __init__(self):
        super(KLineView, self).__init__()
        #
        # TODO: size;
        self.setMinimumWidth(800)
        self.setMinimumHeight(480)
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
        self._cached_pixmap = None
        self._curr_x_step = 0
        self._curr_rect_width = 0
        self._curr_cursor_pos = QPointF()
        self._click_status = 0
        #
        # [zh]
        # 预设的画图参考值
        self._CONST_SETTINGS = dict()
        self._CONST_SETTINGS['max_width'] = 30000
        self._CONST_SETTINGS['y_range'] = 4000
        self._CONST_SETTINGS['margin_top'] = 10
        self._CONST_SETTINGS['margin_bottom'] = 10
        #
        # TODO: new settings;
        self._CONST_SETTINGS['price_pixmap_width'] = 160
        self._CONST_SETTINGS['timestamp_pixmap_height'] = 80
        #
        #
        self._CONST_SETTINGS['x_step'] = 30
        self._CONST_SETTINGS['rect_width'] = 24
        self._CONST_SETTINGS['max_height'] = \
            self._CONST_SETTINGS['y_range'] \
            + self._CONST_SETTINGS['margin_top'] \
            + self._CONST_SETTINGS['margin_bottom']

        # 参考值，计算公式如英文所示；
        self._CONST_SETTINGS['max_k_line_size'] = 6000
        self._CONST_SETTINGS['min_x_step'] = 5
        self._CONST_SETTINGS['min_rect_width'] = 3
        #
        self._pixmap = None
        self._timestamp_pixmap = None
        self._price_pixmap = None
        self._corner_pixmap = None
        #
        # [en]
        # Background and foreground:
        #
        # 背景色与前景色
        palette = QPalette()
        palette.setColor( QPalette.Background, QColor(0, 0, 0))
        palette.setColor( QPalette.Foreground, QColor(255, 0, 0))
        self.setPalette(palette)
        self._init_pixmap()
        self.update()

    def paintEvent(self, event):
        #
        painter = QPainter()
        painter.begin(self)
        #
        painter.drawPixmap(
            0, 0,
            self._CONST_SETTINGS['price_pixmap_width'],
            self.height(),
            self._price_pixmap,
            0, 0,
            self._price_pixmap.width(),
            self._price_pixmap.height()
        )
        painter.drawPixmap(
            self._CONST_SETTINGS['price_pixmap_width'],
            0,
            self.width()
            - self._CONST_SETTINGS['price_pixmap_width'],
            self.height()
            - self._CONST_SETTINGS['timestamp_pixmap_height'],
            self._pixmap,
            0,
            0,
            self._pixmap.width(),
            self._pixmap.height()
        )
        painter.drawPixmap(
            self._CONST_SETTINGS['price_pixmap_width'],
            self.height()
            - self._CONST_SETTINGS['timestamp_pixmap_height'],
            self.width()
            - self._CONST_SETTINGS['price_pixmap_width'],
            self._CONST_SETTINGS['timestamp_pixmap_height'],
            self._timestamp_pixmap,
            0,
            0,
            self._timestamp_pixmap.width(),
            self._timestamp_pixmap.height()
        )
        #
        if self._click_status == 1:
            painter.setPen(QPen(Qt.darkCyan))
            #
            cursor_pos = QCursor.pos()
            cursor_pos = self.mapFromGlobal(cursor_pos)
            cursor_x = cursor_pos.x()
            cursor_y = cursor_pos.y()
            if self._CONST_SETTINGS['price_pixmap_width'] <= \
                    cursor_x <= self.width() \
                    and 0 <= cursor_y <= \
                    self.height() - \
                    self._CONST_SETTINGS['timestamp_pixmap_height']:
                painter.drawLine(cursor_x, 0, cursor_x, self.height())
                painter.drawLine(0, cursor_y, self.width(), cursor_y)
        elif self._click_status == 0:
            painter.eraseRect(0, 0, self.width(), self.height())
            painter.drawPixmap(
                0, 0,
                self._CONST_SETTINGS['price_pixmap_width'],
                self.height(),
                self._price_pixmap,
                0, 0,
                self._price_pixmap.width(),
                self._price_pixmap.height()
            )
            painter.drawPixmap(
                self._CONST_SETTINGS['price_pixmap_width'],
                0,
                self.width()
                - self._CONST_SETTINGS['price_pixmap_width'],
                self.height()
                - self._CONST_SETTINGS['timestamp_pixmap_height'],
                self._pixmap,
                0,
                0,
                self._pixmap.width(),
                self._pixmap.height()
            )
            painter.drawPixmap(
                self._CONST_SETTINGS['price_pixmap_width'],
                self.height()
                - self._CONST_SETTINGS['timestamp_pixmap_height'],
                self.width()
                - self._CONST_SETTINGS['price_pixmap_width'],
                self._CONST_SETTINGS['timestamp_pixmap_height'],
                self._timestamp_pixmap,
                0,
                0,
                self._timestamp_pixmap.width(),
                self._timestamp_pixmap.height()
            )
        #
        painter.end()

    def _init_pixmap(self):
        # k线区域；
        self._pixmap = QPixmap(
            self.width() - self._CONST_SETTINGS['price_pixmap_width'],
            self.height() - self._CONST_SETTINGS['timestamp_pixmap_height']
        )
        #self._pixmap.load("_no_data.png")
        # 横坐标轴，i.e.时间戳坐标轴；
        self._timestamp_pixmap = QPixmap(
            self.width() - self._CONST_SETTINGS['price_pixmap_width'],
            self._CONST_SETTINGS['timestamp_pixmap_height']
        )
        self._timestamp_pixmap.fill(self, 0, 0)
        #
        # [zh]
        # 纵坐标轴，i.e.价格坐标轴；
        self._price_pixmap = QPixmap(
            self._CONST_SETTINGS['price_pixmap_width'],
            self.height()
        )
        self._price_pixmap.fill(self, 0, 0)

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
        self.draw_all_pixmaps()
        self.update()

    def draw_candle_pixmap(self):
        #
        pixmap_width = \
            self.width() - self._CONST_SETTINGS['price_pixmap_width']
        pixmap_height = \
            self.height() - self._CONST_SETTINGS['timestamp_pixmap_height']
        #
        margin_top = self._CONST_SETTINGS['margin_top']
        x_step = 1.0 * pixmap_width / self._curr_span
        rect_width = 0.0
        if x_step >= 3:
            rect_width = x_step * 0.8
        y_range = pixmap_height - margin_top
        #
        self._curr_data = self._data[self._curr_from_idx: self._curr_to_idx + 1]
        self._pixmap = QPixmap(
            pixmap_width, pixmap_height
        )
        self._pixmap.fill(self, 0, 0)
        pixmap_painter = QPainter(self._pixmap)
        pixmap_painter.initFrom(self)
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
            curr_rect = QRectF()
            curr_rect_like_line = QLineF()
            #
            # High enough: rect
            if y_height >= 1:
                curr_rect.setRect(
                    x_start, y_start, rect_width, y_height
                )
            #
            # Otherwise: line instead of rect
            else:
                curr_rect_like_line.setLine(
                    x_start, y_start,
                    x_start + rect_width, y_start
                )
            #
            # The high & low price line:
            curr_line = QLineF(
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
                pixmap_painter.fillRect(curr_rect, Qt.red)
                k_line_rectangles_red.append(curr_rect)
                k_line_lines_red.append(curr_line)
                k_line_lines_red.append(curr_rect_like_line)
            #
            # White:
            else:
                pixmap_painter.fillRect(curr_rect, Qt.white)
                k_line_rectangles_white.append(curr_rect)
                k_line_lines_white.append(curr_line)
                k_line_lines_white.append(curr_rect_like_line)
            #
        # 用红白笔触画图
        pixmap_painter.setPen(QPen(Qt.red))
        pixmap_painter.drawRects(k_line_rectangles_red)
        pixmap_painter.drawLines(k_line_lines_red)
        pixmap_painter.setPen(QPen(Qt.white))
        pixmap_painter.drawRects(k_line_rectangles_white)
        pixmap_painter.drawLines(k_line_lines_white)

    def draw_timestamp_pixmap(self):
        """ 画时间轴 """
        #
        timestamp_pixmap_width = \
            self.width() - self._CONST_SETTINGS['price_pixmap_width']
        timestamp_pixmap_height = \
            self._CONST_SETTINGS['timestamp_pixmap_height']
        #
        self._timestamp_pixmap = QPixmap(
            timestamp_pixmap_width,
            timestamp_pixmap_height
        )
        self._timestamp_pixmap.fill(self, 0, 0)
        pixmap_painter = QPainter(self._timestamp_pixmap)
        pixmap_painter.initFrom(self)
        #
        x_step = 1.0 * timestamp_pixmap_width / self._curr_span
        #
        timestamp_axis = QLineF(
            x_step / 2.0,
            timestamp_pixmap_height * 0.5,
            timestamp_pixmap_width - x_step / 2.0,
            timestamp_pixmap_height * 0.5
        )
        pixmap_painter.drawLine(timestamp_axis)
        #
        for i in range(self._curr_span):
            pixmap_painter.drawLine(
                x_step / 2.0 + x_step * i,
                timestamp_pixmap_height * 0.5,
                x_step / 2.0 + x_step * i,
                timestamp_pixmap_height * 0.5 + 5,
            )
        #

    def draw_price_pixmap(self):
        """ 画价格轴 """
        #
        price_pixmap_width = self._CONST_SETTINGS['price_pixmap_width']
        price_pixmap_height = self.height()
        #
        margin_top = self._CONST_SETTINGS['margin_top']
        y_range = \
            self.height() \
            - self._CONST_SETTINGS['timestamp_pixmap_height'] \
            - margin_top
        y_steps = 3
        #
        the_min = self._the_min
        the_max = self._the_max
        price_step = 1.0 * (the_max - the_min) / y_steps
        #
        self._price_pixmap = QPixmap(
            price_pixmap_width,
            price_pixmap_height
        )
        self._price_pixmap.fill(self, 0, 0)
        pixmap_painter = QPainter(self._price_pixmap)
        pixmap_painter.initFrom(self)
        #
        price_axis = QLineF(
            price_pixmap_width * 0.9,
            margin_top,
            price_pixmap_width * 0.9,
            price_pixmap_height
            - self._CONST_SETTINGS['timestamp_pixmap_height']
        )
        pixmap_painter.drawLine(price_axis)
        #
        for i in range(y_steps + 1):
            pixmap_painter.drawLine(
                price_pixmap_width * 0.9,
                margin_top + 1.0 * y_range / y_steps * i,
                price_pixmap_width * 0.9 - 5,
                margin_top + 1.0 * y_range / y_steps * i
            )
            text_rect = QRectF(
                0,
                margin_top * 0.5 + 1.0 * y_range / y_steps * i,
                price_pixmap_width * 0.9 - 10,
                1.0 * y_range / y_steps * 0.4
            )
            pixmap_painter.drawText(
                text_rect,
                Qt.AlignRight,
                QString(str(the_max - price_step*i))
            )
        #

    def draw_all_pixmaps(self):
        self.draw_candle_pixmap()
        self.draw_timestamp_pixmap()
        self.draw_price_pixmap()
        #
        if self._is_average_line_shown:
            self.draw_average_line()

    def update_k_line(self, data):
        the_last_datum = data.ix[0]
        self._data.ix[-1] = the_last_datum
        #
        self._curr_from_idx = self._data_end_idx - self._curr_span + 1
        self._curr_to_idx = self._data_end_idx
        #
        self.draw_all_pixmaps()
        self.update()

    def append_k_line(self, data_frame):
        data = data_frame[:1]
        self._data = pd.concat([self._data, data])
        self._data_size += 1
        self._data_end_idx += 1
        #
        self._curr_from_idx = self._data_end_idx - self._curr_span + 1
        self._curr_to_idx = self._data_end_idx
        #
        self.draw_all_pixmaps()
        self.update()

    def draw_candles(self, from_idx, to_idx):
        self._curr_from_idx = from_idx
        self._curr_to_idx = to_idx
        self._curr_span = self._curr_to_idx - self._curr_from_idx + 1
        #
        self.draw_all_pixmaps()
        self.update()
        #
        self.emit(SIGNAL("kLineSpanChanged()"))

    def draw_average_line(self):
        if not self._is_average_line_shown:
            return
        #
        pixmap_painter = QPainter(self._pixmap)
        pixmap_painter.initFrom(self)
        #
        pixmap_width = \
            self.width() - self._CONST_SETTINGS['price_pixmap_width']
        pixmap_height = \
            self.height() - self._CONST_SETTINGS['timestamp_pixmap_height']
        #
        margin_top = self._CONST_SETTINGS['margin_top']
        x_step = 1.0 * pixmap_width / self._curr_span
        y_range = pixmap_height - margin_top
        #
        points = list()
        for i in range(self._curr_from_idx, self._curr_to_idx + 1):
            curr_entry = self._data.ix[i]
            open_price = curr_entry['open']
            close_price = curr_entry['close']
            #
            mid_price = (open_price + close_price) / 2.0
            #
            points.append(
                QPointF(
                    x_step / 2.0 + x_step * (i - self._curr_from_idx),
                    margin_top
                    + abs(mid_price - self._the_max)
                    / (self._the_max - self._the_min) * y_range
                )
            )
        pen_yellow = QPen(Qt.yellow)
        pen_yellow.setWidth(1)
        pixmap_painter.setPen(pen_yellow)
        pixmap_painter.drawPolyline(*points)

    def show_average_line(self):
        self._is_average_line_shown = True  # This could be use to undo drawing;
        self.draw_average_line()
        self.update()

    def hide_average_line(self):
        self._is_average_line_shown = False
        self.draw_candle_pixmap()
        self.update()

    def mousePressEvent(self, event):
        if not self._is_data_loaded:
            return  # Nothing happened because of no data loaded;
        if not event.button() == Qt.LeftButton:
            return  # Nothing happened;
        #
        print(">>> Mouse pressed;")
        self._curr_cursor_pos = event.pos()
        #
        if self._is_data_loaded:
            self.setCursor(Qt.OpenHandCursor)

    def mouseReleaseEvent(self, event):
        if not self._is_data_loaded:
            return  # Nothing happened because of no data loaded
        if not event.button() == Qt.LeftButton:
            return  # Nothing happened;
        #
        print(">>> Mouse released;")
        #
        if self._is_data_loaded:
            if self._click_status == 0:
                self.setCursor(Qt.ArrowCursor)
            elif self._click_status == 1:
                self.setCursor(Qt.CrossCursor)
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
                            self.draw_candles(
                                self._curr_from_idx + 1,
                                self._curr_to_idx + 1
                            )
                        else:
                            QMessageBox.about(
                                None,
                                "Right forbidden",
                                "Could not drag to right any more"
                            )
                    else:
                        if self._curr_from_idx > self._data_start_idx:
                            self.draw_candles(
                                self._curr_from_idx - 1,
                                self._curr_to_idx - 1
                            )
                        else:
                            QMessageBox.about(
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
