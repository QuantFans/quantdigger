class _Logger:
    def info(self, tmpl, *args, **kwargs):
        self.output('INFO', tmpl, *args, **kwargs)

    def debug(self, tmpl, *args, **kwargs):
        self.output('DEBUG', tmpl, *args, **kwargs)

    def output(self, level, tmpl, *args, **kwargs):
        msg = tmpl.format(*args, **kwargs)
        msg = '[' + level + '] ' + msg
        print msg


logger = _Logger()
