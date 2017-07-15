# encoding: UTF-8
##
# @file eventenvine.py
# @brief
# @author wondereamer
# @version 0.5
# @date 2016-05-17

import six
from six.moves import queue, _thread

import abc
import time
import zmq

from time import sleep
from threading import Thread, Condition, Lock

from quantdigger.util import mlogger as log
from quantdigger.event import Event


class Timer(object):
    """ 定时器，会定时往事件队列中发送定时事件。 """
    def __init__(self, event_engine, seconds=1):
        # 计时器，用于触发计时器事件
        self._timer = Thread(target = self._run_timer)
        self._timer.daemon = True
        self._timer_active = False
        self._timer_sleep = seconds
        self._timer_pause_condition = Condition(Lock())
        self._event_engine = event_engine

    def set_timer(self, seconds):
        self._timer_sleep = seconds

    def start(self):
        log.info('start timer')
        self._timer_active = True
        self._timer.start()

    def stop(self):
        self._timer_active = False
        self._timer_pause_condition.acquire()

    def resume(self):
        self._timer_active = True
        self._timer_pause_condition.notify()
        self._timer_pause_condition.release()

    def _run_timer(self):
        event = Event(route=Event.TIMER)
        while True:
            with self._timer_pause_condition:
                if not self._timer_active:
                    self._timer_pause_condition.wait()
                self._event_engine.emit(event)
            # 等待
            sleep(self._timer_sleep)


class EventEngine:

    __metaclass__ =  abc.ABCMeta

    def __init__(self):
        self._active = False
        self._routes = {}

    def start(self):
        """引擎启动"""
        #six.print_(self._routes)
        self._active = True

    def stop(self):
        """停止引擎"""
        self._active = False

    def register(self, route, handler):
        """注册事件处理函数监听,
          不重复注册同一事件的同样回调。

        Args:
            route (str): 事件名
            handler (function): 回调函数

        Returns:
            Bool. 是否注册成功。
        """
        if route not in self._routes:
            self._routes[route] = [handler]
            return True
        handlers = self._routes[route]
        if handler not in handlers:
            handlers.append(handler)
            return True
        return False

    def unregister(self, route, handler):
        """ 注销事件处理函数监听 """
        try:
            handlerList = self._routes[route]
            # 如果该函数存在于列表中，则移除
            if handler in handlerList:
                handlerList.remove(handler)
            # 如果函数列表为空，则从引擎中移除该事件类型
            if not handlerList:
                del self._routes[route]
        except KeyError:
            return

    @abc.abstractmethod
    def emit(self, event):
        """向事件队列中存入事件"""
        raise NotImplementedError

    @abc.abstractmethod
    def _run(self):
        """引擎运行"""
        raise NotImplementedError

    def _process(self, event):
        """ 基于多线程的处理事件 """
        if event.route not in self._routes:
            log.warning("事件%s 没有被处理" % event.route)
            return
        for handler in self._routes[event.route]:
            try:
                log.debug("处理事件%s" % event.route)
                _thread.start_new_thread(handler, (event,))
                #handler(event)
            except Exception as e:
                log.error(e)


class QueueEventEngine(EventEngine):
    """
    基于线程队列, 且带有定时器的事件引擎。
    ## @note 必须注册完所有消息以后再启动。
    """
    def __init__(self, name):
        # 事件队列
        EventEngine.__init__(self)
        self._queue = queue.Queue()
        self._thrd = Thread(target=self._run)
        self._thrd.daemon = True
        self._name = name

    def emit(self, event):
        #"""向事件队列中存入事件"""
        #six.print_(self._queue.qsize())
        self._queue.put(event)

    def start(self):
        """引擎启动"""
        EventEngine.start(self)
        self._thrd.start()

    def stop(self):
        """停止引擎"""
        EventEngine.stop(self)
        # 等待事件处理线程退出
        #self._thrd.join()

    def _run(self):
        """引擎运行"""
        while self._active == True:
            try:
                # 获取事件的阻塞时间设为1秒, 这样关闭的时候
                # self._active才会发挥作用。
                event = self._queue.get(block=True, timeout=1)
                self._process(event)
            except queue.Empty:
                pass


class ZMQEventEngine(EventEngine):
    """ 基于zeromq的事件引擎, 同一个地址的实例只会有一个服务器(同时也是客户端)，可有
    多个客户端实例。
    """
    def __init__(self, name, event_protocol="tcp://127.0.0.1:5555",
		    register_protocol="tcp://127.0.0.1:5557"):
        EventEngine.__init__(self)
        self._name = name
        self._context = zmq.Context()
        try:
            self._broadcast_event_socket = self._context.socket(zmq.PUB)
            self._broadcast_event_socket.bind(event_protocol)
            self._server_recv_event_socket = self._context.socket(zmq.PULL)
            self._server_recv_event_socket.bind(register_protocol)
            self._is_server = True
            log.info('Run ZMQEventEngine Server: %s' % self._name)
        except zmq.error.ZMQError:
            log.info('Run ZMQEventEngine client: %s' % self._name)
            self._is_server = False

        self._emit_event_socket = self._context.socket(zmq.PUSH)
        self._emit_event_socket.connect(register_protocol)
        self._client_recv_event_socket = self._context.socket(zmq.SUB)
        self._client_recv_event_socket.connect(event_protocol)

        self._thrd = Thread(target=self._run)
        self._thrd.daemon = True
        self._queue_engine = QueueEventEngine(self._name)
        time.sleep(1)

    def emit(self, event):
        """ client or event"""
        msg = Event.event_to_message(event)
        self._emit_event_socket.send_string(msg)
        return

    def start(self):
        """引擎启动"""
        EventEngine.start(self)
        self._queue_engine.start()
        self._thrd.start()

    def stop(self):
        """停止引擎"""
        EventEngine.stop(self)
        self._queue_engine.stop()
        self._context.destroy()
        #self._thrd.join()

    def register(self, route, handler):
        """ 接受指定的事件。 """
        if self._queue_engine.register(route, handler):
            self._client_recv_event_socket.setsockopt(zmq.SUBSCRIBE,
                    Event.message_header(route))

    def unregister(self, route, handler):
        self._queue_engine.unregister(route, handler)
        if route not in self._routes:
            self._client_recv_event_socket.setsockopt(zmq.UNSUBSCRIBE,
                    Event.message_header(route))

    def _run(self):
        """"""
        poller = zmq.Poller()
        poller.register(self._client_recv_event_socket, zmq.POLLIN)
        if self._is_server:
            poller.register(self._server_recv_event_socket, zmq.POLLIN)
        while self._active:
            socks = dict(poller.poll(1))
            if self._client_recv_event_socket in socks and \
                    socks[self._client_recv_event_socket] == zmq.POLLIN:
                self._run_client()

            if self._is_server and  self._server_recv_event_socket in socks and \
                socks[self._server_recv_event_socket] == zmq.POLLIN:
                self._run_server()
        return

    def _run_client(self):
        message = self._client_recv_event_socket.recv()
        event = Event.message_to_event(message)
        log.debug("[engine: %s] receive message: %s" % (self._name, event))
        self._queue_engine.emit(event)

    def _run_server(self):
        strevent = self._server_recv_event_socket.recv()
        self._broadcast_event_socket.send(strevent)
        log.debug("[engine: %s] broadcast message: %s" % (self._name, strevent))


if __name__ == '__main__':
    import time, datetime, sys

    def simpletest(event):
        six.print_(str(datetime.datetime.now()), event)

    ee = ZMQEventEngine('test')
    ee.register(Event.TIMER, simpletest)
    timer = Timer(ee)
    ee.start()
    timer.start()
    event = Event(route=Event.TIMER)

    timer.stop()
    time.sleep(2)
    timer.resume()
    time.sleep(2)
    timer.stop()
    client = ZMQEventEngine('test')
    event = Event(route=Event.TIMER, args = { 'data': 'from client' })
    client.start()
    client.emit(event)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        ee.stop()
        client.stop()
        sys.exit(0)
