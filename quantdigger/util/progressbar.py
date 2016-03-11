# -*- coding:utf-8 -*-

# Copyright: Lustralisk
# Author: Cedric Liu
# Date: 2015-11-08

import sys
import time


class ProgressBar:
    def __init__(self, count=0, total=0, width=50):
        self.count = count
        self.total = total
        self.width = width

    def move(self):
        self.count += 1

    def log(self, s):
        sys.stdout.write(' ' * (self.width + 9) + '\r')
        sys.stdout.flush()
        if s:
            print(s)
        progress = self.width * self.count / self.total
        # sys.stdout.write('{0:3}/{1:3}: '.format(self.count, self.total))
        sys.stdout.write('%0.1f' % (float(self.count)/self.total*100)+'% ')
        sys.stdout.write('#' * progress + '-' * (self.width - progress) + '\r')
        if progress == self.width:
            sys.stdout.write('\n')
        sys.stdout.flush()
