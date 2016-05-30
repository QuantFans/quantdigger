from quantdigger.infras.ioc import *
from quantdigger.infras.logger import logger
from quantdigger.config import settings

_ds_container = IoCContainer()

resolve_datasource = resolve_from(_ds_container)


def register_datasource(name, *args, **kwargs):
    logger.info('register datasource: {name}', name=name)
    r = register_to(_ds_container)
    a = [settings[k] for k in args]
    ka = {k: settings[name] for k, name in kwargs.items()}
    return r(name, *a, **ka)


def get_setting_datasource():
    ds_type = settings['source']
    return resolve_datasource(ds_type)
