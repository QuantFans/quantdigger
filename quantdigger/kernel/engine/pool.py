# -*- coding: utf8 -*-
class EventPool(object):
    """ 事件池。"""
    def __init__(self, container=[]):
        """ container决定是否是线程安全的。
        
        Args:
            container (list or Queue): 事件容器
        """
        self._pool = container

    def put(self, item):
        self._pool.append(item)

    def get(self):
        """docstring for get""" 
        return self._pool.pop(0)
