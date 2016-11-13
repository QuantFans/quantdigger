from quantdigger.infras.function import overload_setter
from quantdigger.config import settings


class ConfigUtil(object):
    @staticmethod
    @overload_setter
    def set(key, val):
        settings[key] = val

    @staticmethod
    def get(key, d=KeyError):
        if d == KeyError:
            return settings[key]
        else:
            return settings.get(key, d)
