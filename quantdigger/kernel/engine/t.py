#def assign_algo(method):
    #def wrapper(self, price, *args):
        #self._algo = method
        #return method(self, price, *args)
    #return wrapper

class A(object):
    """"""
    def __init__(self):
        pass

    def fun(self):
        """""" 
        apply(self._algo, self._args)


class B(A):
    """"""
    def __init__(self, price, n):
        self._args = (price, n)
    
    def _algo(self, price, n):
        """docstring for tes""" 
        print price, n


b = B('price', 'n')
#b.fun()
print B.__mro__
