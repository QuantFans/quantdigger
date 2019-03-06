#!/usr/bin/env python
# encoding: utf-8


from timeit import timeit

from nameko.standalone.rpc import ClusterRpcProxy
with ClusterRpcProxy({"AMQP_URI": "pyamqp://guest:guest@localhost"}) as rpc:

    def func():
        result = rpc.backend_service.say_hello("world")

    t = timeit('func()', 'from __main__ import func', number=100)
    print(t)
