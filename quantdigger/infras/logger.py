class _Logger:
    def __init__(self):
        self.ignore_list = []

    def info(self, tmpl, *args, **kwargs):
        self.output('INFO', tmpl, *args, **kwargs)

    def debug(self, tmpl, *args, **kwargs):
        self.output('DEBUG', tmpl, *args, **kwargs)

    def warn(self, tmpl, *args, **kwargs):
        self.output('WARN', tmpl, *args, **kwargs)

    def error(self, tmpl, *args, **kwargs):
        self.output('ERROR', tmpl, *args, **kwargs)

    def output(self, level, tmpl, *args, **kwargs):
        if level in self.ignore_list:
            return
        msg = tmpl.format(*args, **kwargs)
        msg = '[' + level + '] ' + msg
        print msg

    def ignore(self, *args):
        self.ignore_list.extend(args)


logger = _Logger()


def deprecated(f):
    def ff(*args, **kwargs):
        logger.warn('{0} is deprecated!', str(f))
        return f(*args, **kwargs)
    return ff
