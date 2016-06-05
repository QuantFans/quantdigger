class HashObject(object):
    @classmethod
    def new(cls, **kwargs):
        obj = cls
        for k, v in kwargs.items():
            setattr(obj, k, v)
        return obj
