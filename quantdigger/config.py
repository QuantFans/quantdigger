# -*- coding: utf-8 -*-
settings = {
    'source': 'csv',
    'data_path': './data'
}

def set_config(cfg):
    """""" 
    from quantdigger.datasource.data import locd
    if 'source' in cfg:
        cfg['source'] = cfg['source'].lower()
        assert(cfg['source'] in ['sqlite', 'csv']) 
    settings.update(cfg)
    locd.set_source(settings)

# 默认设置
#from quantdigger.errors import FileDoesNotExist
set_config(settings)
#try:
#except FileDoesNotExist:
    ### @TODO ...
    ##print("默认的sqlite文件不存在")
    #pass

__all__ = ['settings', 'set_config']
