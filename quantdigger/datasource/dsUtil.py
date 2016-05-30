from quantdigger.infras.ioc import *
from quantdigger.infras.logger import logger
from quantdigger.config import settings

_ds_container = IoCContainer()


class _DatasourceTrunk(IoCTrunk):

    def __init__(self, cls, args, kwargs):
        super(_DatasourceTrunk, self).__init__(cls, args, kwargs)

    def on_register(self, name):
        logger.info('register datasource: {cls} => {name}',
                    cls=self.cls, name=name)

    def construct(self):
        a = [settings[k] for k in self.args]
        ka = {k: settings[name] for k, name in self.kwargs.items()}
        return self.cls(*a, **ka)


register_datasource = register_to(_ds_container, _DatasourceTrunk)
resolve_datasource = resolve_from(_ds_container)


def get_setting_datasource():
    ds_type = settings['source']
    return resolve_datasource(ds_type)
