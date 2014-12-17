import abc

class PluginInterface(object):
    """ 插件接口"""

    def __init__(self):
        pass

    @abc.abstractmethod
    def get_icon(self):
        """ 获取插件的图标 """ 
        pass

    @abc.abstractmethod
    def clone(self):
        pass


