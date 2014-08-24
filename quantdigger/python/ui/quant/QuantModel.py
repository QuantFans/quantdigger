__author__ = 'TeaEra'

from PyQt4 import QtCore

################################################################################


class RectLikeLine(object):

    def __init__(self):
        super(RectLikeLine, self).__init__()
        #
        self._line = QtCore.QLineF()
        self._pen_width = 0.0

    def set_line_with_pen_width(self, x1, y1, x2, y2, pen_width):
        """
        :param x1
        :param y1
        :param x2
        :param y2
        :param pen_width
        """
        self._line.setLine(x1, y1 - pen_width/2.0, x2, y2 - pen_width/2.0)

    def get_line(self):
        """
        :return self._line
        """
        return self._line

    def get_pen_width(self):
        """
        :return self._pen_width
        """
        return self._pen_width

################################################################################
# Status: OK


class PixMapSettings(object):
    """
    PixMapSettings
    """

    def __init__(self):
        super(PixMapSettings, self).__init__()
        self._settings = {}
        #
        self.init_settings()

    def init_settings(self):
        """
        Initialize settings;

        :return: nothing
        """
        # The size of pix_map:
        self._settings['pix_map_max_width'] = 30000.0
        self._settings['pix_map_max_height'] = 800.0
        # The margins:
        self._settings['pix_map_margin_top'] = 0.0
        self._settings['pix_map_margin_right'] = 0.0
        self._settings['pix_map_margin_bottom'] = 0.0
        self._settings['pix_map_margin_left'] = 0.0
        # The size of window:
        self._settings['window_width'] = 1000.0
        self._settings['window_height'] = 600.0
        # The x step:
        self._settings['pix_map_x_step_width'] = 50.0
        # To calculate pix_map_x_step_size:
        self.calc_settings_about_x()
        # To calculate pix_map_y_range:
        self.calc_pix_map_y_range()

    def calc_settings_about_x(self):
        """
        According to:
          - pix_map_max_width
          - pix_map_margin_left
          - pix_map_margin_right
          - pix_map_x_step_width
        Results:
          - pix_map_x_step_size
          - pix_map_x_history_size
          - pix_map_x_reserve_size
          - pix_map_k_line_rect_width

        :return: nothing
        """
        temp_total_width = \
            self._settings['pix_map_max_width'] \
            - self._settings['pix_map_margin_left'] \
            - self._settings['pix_map_margin_right'] \
            - self._settings['pix_map_x_step_width']
        temp_total_size = \
            int(
                temp_total_width
                / self._settings['pix_map_x_step_width']
            )
        self._settings['pix_map_x_step_size'] = \
            temp_total_size
        self._settings['pix_map_x_history_size'] = \
            temp_total_size - 1
        self._settings['pix_map_x_reserve_size'] = 1
        rect_step_ratio = 0.8
        self._settings['pix_map_k_line_rect_width'] = \
            rect_step_ratio * self._settings['pix_map_x_step_width']

    def calc_pix_map_y_range(self):
        """
        According to:
          - pix_map_max_height
          - pix_map_margin_top
          - pix_map_margin_bottom
        Results:
          - pix_map_y_range

        :return: nothing
        """
        self._settings['pix_map_y_range'] = \
            self._settings['pix_map_max_height'] \
            - self._settings['pix_map_margin_top'] \
            - self._settings['pix_map_margin_bottom']

    def get_settings(self):
        """
        Getter of _settings;

        :return: self._settings
        """
        return self._settings

    def set_margins(
            self, margin_top=0, margin_right=0, margin_bottom=0, margin_left=0):
        """

        :param margin_top: top margin
        :param margin_right: right margin
        :param margin_bottom: bottom margin
        :param margin_left: left margin
        :return: nothing
        """
        # TODO: exception raise?
        self._settings['pix_map_margin_top'] = 1.0 * margin_top
        self._settings['pix_map_margin_right'] = 1.0 * margin_right
        self._settings['pix_map_margin_bottom'] = 1.0 * margin_bottom
        self._settings['pix_map_margin_left'] = 1.0 * margin_left
        #
        self.calc_settings_about_x()
        self.calc_pix_map_y_range()

    def set_pix_map_size(self, max_width=30000, max_height=600):
        """

        :param max_width
        :param max_height
        :return: nothing
        """
        if max_width <= 0 or max_height <= 0:
            raise MaxSizeInvalidException()
        else:
            self._settings['pix_map_max_width'] = 1.0 * max_width
            self._settings['pix_map_max_height'] = 1.0 * max_height
            self.calc_settings_about_x()
            self.calc_pix_map_y_range()

    def set_pix_map_x_step_width(self, pix_map_x_step_width):
        if pix_map_x_step_width <= 0:
            raise XStepWidthInvalidException()
        else:
            self._settings['pix_map_x_step_width'] = \
                1.0 * pix_map_x_step_width
            self.calc_settings_about_x()

    def set_window_size(self, window_width=1000, window_height=600):
        if window_width <= 0 or window_height <= 0:
            raise WindowSizeInvalidException
        else:
            self._settings['window_width'] = 1.0 * window_width
            self._settings['window_height'] = 1.0 * window_height

    def get_pix_map_max_width(self):
        """
        Getter for 'pix_map_max_width'
        """
        return self._settings['pix_map_max_width']

    def get_pix_map_x_step_width(self):
        """
        Getter for 'pix_map_x_step_width'
        """
        return self._settings['pix_map_x_step_width']

################################################################################
# Status: OK


class MaxSizeInvalidException(Exception):
    """
    Exception: MaxSizeInvalidException
    """

    def __init__(self, msg="Max size is invalid."):
        self._msg = msg

    def __str__(self):
        return repr(self._msg)


class XStepWidthInvalidException(Exception):
    """
    Exception: XStepWidthInvalidException
    """

    def __init__(self, msg="X step width is invalid."):
        self._msg = msg

    def __str__(self):
        return repr(self._msg)


class WindowSizeInvalidException(Exception):
    """
    Exception: WindowSizeInvalidException
    """

    def __init__(self, msg="Window size is invalid"):
        self._msg = msg

    def __str__(self):
        return repr(self._msg)

################################################################################


class QuotationModel(object):
    """
    """

    def __init__(
        self, data=None, horizontal_header=None, vertical_header=None
    ):
        super(QuotationModel, self).__init__()
        #
        self._data = data
        self._horizontal_header = horizontal_header
        self._vertical_header = vertical_header

################################################################################


class SlicedPixMapModel(object):
    """
    """

    def __init__(self, data, from_idx, to_idx):
        super(SlicedPixMapModel, self).__init__()
        #
        self._data = data
        self._from_idx = from_idx
        self._to_idx = to_idx
        #
        self._pix_map = None

    def set_pix_map(self, pix_map):
        self._pix_map = pix_map

    def get_pix_map(self):
        return self._pix_map

    def get_from_idx(self):
        return self._from_idx

    def get_to_idx(self):
        return self._to_idx

    def get_data(self):
        return self._data[self._from_idx:self._to_idx+1]

    def get_size(self):
        return self._to_idx - self._from_idx + 1

    def get_pix_map_width(self):
        if not self._pix_map:
            return 0.0
        return self._pix_map.width()

    def get_pix_map_height(self):
        if not self._pix_map:
            return 0.0
        return self._pix_map.height()

################################################################################


class WindowedPixMapModel(object):

    def __init__(self):
        super(WindowedPixMapModel, self).__init__()
        #
        self._widget_window = QtCore.QRectF()
        self._pix_map_window = QtCore.QRectF()
        #
        self._pix_map = None

    def set_widget_window(self, x, y, width, height):
        self._widget_window.setRect(x, y, width, height)

    def set_pix_map_window(self, x, y, width, height):
        self._pix_map_window.setRect(x, y, width, height)

    def set_pix_map(self, pix_map):
        self._pix_map = pix_map

    def get_widget_window(self):
        return self._widget_window

    def get_pix_map_window(self):
        return self._pix_map_window

    def get_pix_map(self):
        return self._pix_map