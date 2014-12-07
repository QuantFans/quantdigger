#_*_ coding: utf-8 _*_
from QuantUtils import from_utf8
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from QxtSpanSlider import QxtSpanSlider
from CandleWidget import KLineView
class IndexRangeSelector(QWidget):
    """
    查看范围选择器
    """

    def __init__(self, from_index=0, to_index=99):
        super(IndexRangeSelector, self).__init__()
        #
        main_grid_layout = QGridLayout(self)
        #
        label_from = QLabel(from_utf8("From"))
        label_to = QLabel(from_utf8("To"))
        spin_box_from = QSpinBox()
        spin_box_to = QSpinBox()
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


class InfoView(QWidget):

    def __init__(self):
        super(InfoView, self).__init__()
        # 背景色与前景色
        self_palette = QPalette()
        self_palette.setColor(
            QPalette.Background, QColor(0, 0, 0)
        )
        self_palette.setColor(
            QPalette.Foreground, QColor(255, 0, 0)
        )
        self.setPalette(self_palette)
        #
        self.pix_map = QPixmap(self.size())
        self.pix_map.fill(self, 0, 0)

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.drawPixmap(0, 0, self.width(), self.height(), self.pix_map)
        painter.end()



class ContainerView(QMainWindow):
    """ k线窗口的容器 """

    def __init__(self):
        super(ContainerView, self).__init__()
        #
        main_splitter = QSplitter(Qt.Horizontal)
        center_splitter = QSplitter(Qt.Vertical)
        right_splitter = QSplitter(Qt.Vertical)
        #
        main_splitter.addWidget(center_splitter)
        main_splitter.addWidget(right_splitter)
        main_splitter.setSizes( [800, 160])
        #
        k_line_view = KLineView()
        k_line_slider = QxtSpanSlider()
        center_splitter.addWidget(k_line_view)
        center_splitter.addWidget(k_line_slider)
        center_splitter.setSizes( [480, 20])
        k_line_slider.setEnabled(False)
        #
        info_view = InfoView()
        index_range_selector = IndexRangeSelector()
        right_splitter.addWidget(info_view)
        right_splitter.addWidget(index_range_selector)
        right_splitter.setSizes( [400, 100])
        index_range_selector.setEnabled(False)
        #
        self.setCentralWidget(main_splitter)
        #
        # Instance variables:
        self._k_line = k_line_view
        self._max_offset = 0
        self._k_line_slider = k_line_slider
        self._index_range_selector = index_range_selector
        #
        self._item_moved = 0
        QObject.connect(k_line_slider,
                        SIGNAL("lowerPositionChanged(int)"),
                        self.slide_lower_handle)
        QObject.connect(k_line_slider,
                        SIGNAL("upperPositionChanged(int)"),
                        self.slide_upper_handle)
        QObject.connect(k_line_slider,
                        SIGNAL("sliderReleased()"),
                        self.change_span)
        QObject.connect(k_line_view,
                        SIGNAL("kLineSpanChanged()"),
                        self.update_span_relevant_items)
        QObject.connect(self._index_range_selector.get_spin_box_from(),
                        SIGNAL("valueChanged(int)"),
                        self.update_curr_from_index)
        QObject.connect(self._index_range_selector.get_spin_box_to(),
                        SIGNAL("valueChanged(int)"),
                        self.update_curr_to_index)

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
        self.update_span_relevant_items()

    def append_k_line(self, data_frame):
        self._k_line.append_k_line(data_frame)
        self.update_span_relevant_items()

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
                QMessageBox.about(
                    None, "Lower", "Not so little"
                )
            elif self._item_moved == 2:
                upper_value = lower_value + max_k_line_size
                #
                QMessageBox.about(
                    None, "Upper", "Not so much"
                )
        self._k_line.draw_candles(lower_value, upper_value)

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
            QMessageBox.about(
                None,
                "From index",
                "Too small"
            )
            temp_curr_from_idx = \
                self._k_line.get_curr_to_idx() + 1 \
                - self._k_line.get_max_k_line_size()
        #
        self._k_line.draw_candles(
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
            QMessageBox(
                None,
                "To index",
                "Too big"
            )
            temp_curr_to_idx = \
                self._k_line.get_curr_from_idx() \
                + self._k_line.get_max_k_line_size() - 1
        #
        self._k_line.draw_candles(
            self._k_line.get_curr_from_idx(),
            temp_curr_to_idx
        )
        '''
        pass

    def get_k_line(self):
        #
        # TODO: should be removed?
        return self._k_line
