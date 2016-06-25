class IoCContainer(object):

    def __init__(self):
        self._container = {}

    def register(self, key, obj):
        if key in self._container:
            msg = 'IoC Error: %s already exists!\n\t' % key
            raise Exception(msg + str(self))
        self._container[key] = obj

    def resolve(self, key):
        if key not in self._container:
            msg = 'IoC Error: %s does not exist!\n\t' % key
            raise Exception(msg + str(self))
        return self._container[key]

    def set(self, key, obj):
        if key not in self._container:
            msg = 'IoC Error: %s does not exist!\n\t' % key
            raise Exception(msg + str(self))
        self._container[key] = obj

    def __str__(self):
        return 'IoC: %s' % str(self._container)


class IoCTrunk(object):

    def __init__(self, cls, args, kwargs):
        self.cls = cls
        self.args = args
        self.kwargs = kwargs

    def on_register(self, name):
        pass

    def construct(self):
        raise NotImplementedError


def register_to(ioc_container, trunk_cls):
    def register(name, *args, **kwargs):
        def wrapper(cls):
            trunk = trunk_cls(cls, args, kwargs)
            trunk.on_register(name)
            ioc_container.register(name, trunk)
            return cls
        return wrapper
    return register


def resolve_from(ioc_container):
    def resolve(name):
        obj = ioc_container.resolve(name)
        if isinstance(obj, IoCTrunk):
            instance = obj.construct()
            ioc_container.set(name, instance)
            return instance
        else:
            return obj
    return resolve
