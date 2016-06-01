def overload_setter(setter):

    def multiple_set(d):
        for k, v in d.items():
            setter(k, v)

    def wrapper(*args, **kwargs):
        # args
        if len(args) == 1:
            multiple_set(args[0])
        elif len(args) >= 2:
            setter(args[0], args[1])
        # kwargs
        multiple_set(kwargs)

    return wrapper
