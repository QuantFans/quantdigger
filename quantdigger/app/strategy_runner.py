
class StrategyRunner(object):
    def __init__(self, **kwargs):
        self._run = kwargs.get('run', None)
        self._initialize = kwargs.get('initialize', None)

    def run(self, data):
        self._run(data)


