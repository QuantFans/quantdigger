# -*- coding: utf-8 -*-

import six
from quantdigger.configutil import ConfigUtil
from quantdigger.infras.ioc import *
from quantdigger.util import log

_ds_container = IoCContainer()


class _DatasourceTrunk(IoCTrunk):

    def __init__(self, cls, args, kwargs):
        super(_DatasourceTrunk, self).__init__(cls, args, kwargs)

    def on_register(self, name):
        log.info('register datasource: {0} => {1}'.format(self.cls, name))

    def construct(self):
        a = [ConfigUtil.get(k, None) for k in self.args]
        ka = {k: ConfigUtil.get(name, None) for k, name in six.iteritems(self.kwargs)}
        return self.cls(*a, **ka)


register_datasource = register_to(_ds_container, _DatasourceTrunk)
resolve_datasource = resolve_from(_ds_container)


def get_setting_datasource():
    ds_type = ConfigUtil.get('source')
    return resolve_datasource(ds_type), ds_type
