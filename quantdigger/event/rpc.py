# encoding: UTF-8

import six
import time
from datetime import datetime
from threading import Thread, Condition, Lock
from quantdigger.util import mlogger as log
from quantdigger.errors import InvalidRPCClientArguments
from quantdigger.event import Event


class EventRPCClient(object):
    def __init__(self, name, event_engine, service, event_client=None, event_server=None):
        self.EVENT_FROM_CLIENT = event_client if event_client else "EVENT_FROM_%s_CLIENT" % service.upper()
        self.EVENT_FROM_SERVER = event_server if event_server else "EVENT_FROM_%s_SERVER" % service.upper()
        self.rid = 0
        self._handlers = {}
        self._name = name
        self._handlers_lock = Lock()
        self._event_engine = event_engine
        self._event_engine.register(self.EVENT_FROM_SERVER, self._process_apiback)
        self._pause_condition = Condition()
        self._sync_ret = None
        self._timeout = 0
        self._timer_sleep = 1
        self._sync_call_time_lock = Lock()
        self._sync_call_time = datetime.now()
        timer = Thread(target=self._run_timer)
        timer.daemon = True
        timer.start()

    def _run_timer(self):
        # @TODO 用python自带的Event替代。
        while True:
            if not self._timeout == 0:
                with self._sync_call_time_lock:
                    mtime = self._sync_call_time
                delta = (datetime.now() - mtime).seconds
                if delta >= self._timeout:
                    # print("timeout", self._timeout, delta)
                    # 不可重入，保证self.rid就是超时的那个
                    with self._handlers_lock:
                        del self._handlers[self.rid]
                    log.debug("[RPCClient._runtimer] 处理超时, delete rid; %s" % self.rid)
                    self._timeout = 0
                    self._notify_server_data()
            time.sleep(self._timer_sleep)

    def _process_apiback(self, event):
        assert(event.route == self.EVENT_FROM_SERVER)
        self._timeout = 0
        rid = event.args['rid']
        try:
            with self._handlers_lock:
                handler = self._handlers[rid]
        except KeyError:
            log.info('[RPCClient._process_apiback] 放弃超时任务的返回结果')
        else:
            try:
                if handler:
                    # 异步
                    handler(event.args['ret'])
                else:
                    # 同步
                    self._sync_ret = event.args['ret']
                    self._notify_server_data()
            except Exception as e:
                log.error(e)
            log.debug("[RPCClient._process_apiback] 删除已经完成的任务 rid; %s" % rid)
            with self._handlers_lock:
                del self._handlers[rid]

    def call(self, apiname, args, handler):
        """ 给定参数args，异步调用RPCServer的apiname服务,
        返回结果做为回调函数handler的参数。

        Args:
            apiname (str): 服务API名称。
            args (dict): 给服务API的参数。
            handler (function): 回调函数。
        """
        if not isinstance(args, dict):
            raise InvalidRPCClientArguments(argtype=type(args))
        assert(handler is not None)
        log.debug('RPCClient [%s] sync_call: %s' % (self._name, apiname))
        self.rid += 1
        args['apiname'] = apiname
        args['rid'] = self.rid
        self._event_engine.emit(Event(self.EVENT_FROM_CLIENT, args))
        with self._handlers_lock:
            self._handlers[self.rid] = handler

    def sync_call(self, apiname, args={}, timeout=5):
        """ 给定参数args，同步调用RPCServer的apiname服务,
        返回该服务的处理结果。如果超时，返回None。

        Args:
            apiname (str): 服务API名称。
            args (dict): 给服务API的参数。
            handler (function): 回调函数。
        """
        log.debug('RPCClient [%s] sync_call: %s' % (self._name, apiname))
        if not isinstance(args, dict):
            self._timeout = 0
            self._sync_ret = None
            raise InvalidRPCClientArguments(argtype=type(args))
        self.rid += 1
        args['apiname'] = apiname
        args['rid'] = self.rid
        with self._sync_call_time_lock:
            self._sync_call_time = datetime.now()
        self._timeout = timeout
        with self._handlers_lock:
            self._handlers[self.rid] = None
        self._event_engine.emit(Event(self.EVENT_FROM_CLIENT, args))
        self._waiting_server_data()
        ret = self._sync_ret
        return ret

    def _waiting_server_data(self):
        with self._pause_condition:
            self._pause_condition.wait()

    def _notify_server_data(self):
        with self._pause_condition:
            self._pause_condition.notify()


class EventRPCServer(object):
    def __init__(self, event_engine, service, event_client=None, event_server=None):
        super(EventRPCServer, self).__init__()
        self._routes = {}
        self._routes_lock = Lock()
        # server监听的client事件
        self.EVENT_FROM_CLIENT = event_client if event_client else "EVENT_FROM_%s_CLIENT" % service.upper()
        # client监听的server事件
        self.EVENT_FROM_SERVER = event_server if event_server else "EVENT_FROM_%s_SERVER" % service.upper()
        self._event_engine = event_engine
        self._event_engine.register(self.EVENT_FROM_CLIENT, self._process_request)
        log.info("[Create RPCServer  %s]" % self.EVENT_FROM_CLIENT)
        self._name = service.upper()

    def register(self, route, handler):
        """ 注册服务函数。

        Args:
            route (str): 服务名
            handler (function): 回调函数

        Returns:
            Bool. 是否注册成功。
        """
        if route in self._routes:
            return False
        with self._routes_lock:
            self._routes[route] = handler
        return True

    def unregister(self, route):
        """ 注销服务函数 """
        with self._routes_lock:
            if route in self._routes:
                del self._routes[route]

    def _process_request(self, event):
        args = event.args
        rid = args['rid']
        apiname = args['apiname']
        del args['rid']
        del args['apiname']
        log.debug('RPCServer [%s] process: %s' % (self._name, apiname))
        try:
            with self._routes_lock:
                handler = self._routes[apiname]
            # @TODO async
            ret = handler(**args)
        except Exception as e:
            log.exception(e)
        else:
            args = {'ret': ret,
                    'rid': rid
            }
            log.debug('RPCServer [%s] emit %s' % (self._name,
                      str(self.EVENT_FROM_SERVER)))
            self._event_engine.emit(Event(self.EVENT_FROM_SERVER, args))


if __name__ == '__main__':

    from eventengine import ZMQEventEngine
    import sys

    def print_hello(data):
        """"""
        six.print_("***************")
        six.print_("print_hello")
        six.print_("args: ", data)
        six.print_("return: ", 123)
        return "123"
    server_engine = ZMQEventEngine('test')
    server_engine.start()
    server = EventRPCServer(server_engine, 'test')
    server.register("print_hello", print_hello)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        server_engine.stop()
        sys.exit(0)
