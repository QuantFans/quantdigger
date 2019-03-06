# -*- coding: utf-8 -*-


class PlotterDelegator(object):
    """docstring for PlotterDele"""
    def __init__(self):
        self.marks = [{}, {}]

    def plot_line(self, name, ith_window, x, y,
                  styles, lw=1, ms=10, twinx=False):
        """ 绘制曲线

        Args:
            name (str): 标志名称
            ith_window (int): 在第几个窗口显示，从1开始。
            x (datetime): 时间坐标
            y (float): y坐标
            styles (str): 控制颜色，线的风格，点的风格
            lw (int): 线宽
            ms (int): 点的大小
        """
        mark = self.marks[0].setdefault(name, [])
        mark.append((ith_window - 1, twinx, x - 1, float(y), styles, lw, ms))

    def plot_text(self, name, ith_window, x, y, text,
                  color='black', size=15, rotation=0):

        """ 绘制文本

        Args:
            name (str): 标志名称
            ith_window (int): 在第几个窗口显示，从1开始。
            x (float): x坐标
            y (float): y坐标
            text (str): 文本内容
            color (str): 颜色
            size (int): 字体大小
            rotation (float): 旋转角度
        """
        mark = self.marks[1].setdefault(name, [])
        mark.append((ith_window - 1, x - 1, float(y), text, color, size, rotation))
