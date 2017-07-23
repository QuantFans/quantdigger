import six
def overload_setter(setter):

    def multiple_set(d):
        for k, v in six.iteritems(d):
            setter(k, v)

    def new_setter(*args, **kwargs):
        # args
        if len(args) == 1:
            multiple_set(args[0])
        elif len(args) >= 2:
            setter(args[0], args[1])
        # kwargs
        multiple_set(kwargs)

    return new_setter
