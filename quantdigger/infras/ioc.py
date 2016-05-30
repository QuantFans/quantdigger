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

    def __str__(self):
        return 'IoC: %s' % str(self._container)


def register_to(ioc_container):
    def register(name, *args, **kwargs):
        def decorator(cls):
            instance = cls(*args, **kwargs)
            ioc_container.register(name, instance)
            return cls
        return decorator
    return register


def resolve_from(ioc_container):
    def resolve(name):
        return ioc_container.resolve(name)
    return resolve
