# encoding: UTF-8
##
# @file eventengine.py
# @brief 
# @author wondereamer
# @version 0.1
# @date 2016-05-29
from datetime import datetime
from Queue import Queue, Empty
from threading import Thread, Condition, Lock
from time import sleep

from quantdigger.util import elogger as logger
from quantdigger.errors import InvalidRPCClientArguments

EVENT_TIMER = 'timer'

class Event:
    def __init__(self, route=None, args={ }):
        self.route = route
        self.args = args

    def __str__(self):
        return "route: %s\nargs: %s" % (self.route, self.args)


class _Timer(object):
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

    def start_timer(self):
        self._timer_active = True
        self._timer.start()

    def pause_timer(self):
        self._timer_active = False
        self._timer_pause_condition.acquire()

    def resume_timer(self):
        self._timer_active = True
        self._timer_pause_condition.notify()
        self._timer_pause_condition.release()

    def _run_timer(self):
        event = Event(route=EVENT_TIMER)
        while True:
            with self._timer_pause_condition:
                if not self._timer_active:
                    self._timer_pause_condition.wait()
                self._event_engine.emit(event)    
            # 等待
            sleep(self._timer_sleep)
    

class _QueueEventEngine(object):
    """
    计时器使用python线程的事件驱动引擎        
    """
    def __init__(self):
        """初始化事件引擎"""
        # 事件队列
        self._queue = Queue()
        self._active = False
        self._routes = {}
        self._thread = Thread(target=self._run)
        self._thread.daemon = True

    def start(self):
        """引擎启动"""
        #print self._routes
        self._active = True
        self._thread.start()
    
    def stop(self):
        """停止引擎"""
        self._active = False
        self._timer_active = False
        # 等待事件处理线程退出
        #self._thread.join()
            
    def register(self, route, handler):
        """注册事件处理函数监听,
          不重复注册同样事件的同样回调。
        """
        if route not in self._routes:
            self._routes[route] = [handler]
            return
        handlers = self._routes[route]
        if handler not in handlers:
            handlers.append(handler) 

    def unregister(self, route, handler):
        """注销事件处理函数监听"""
        try:
            handlerList = self._routes[route]
            # 如果该函数存在于列表中，则移除
            if handler in handlerList:
                handlerList.remove(handler)
            # 如果函数列表为空，则从引擎中移除该事件类型
            if not handlerList:
                del self._routes[route]
        except KeyError:
            pass     
        
    def emit(self, event):
        """向事件队列中存入事件"""
        self._queue.emit(event)
        
    def _run(self):
        """引擎运行"""
        while self._active == True:
            try:
                # 获取事件的阻塞时间设为1秒
                event = self._queue.get(block=True, timeout=1)
                self._process(event)
            except Empty:
                pass
            
    def _process(self, event):
        """处理事件"""
        if event.route in self._routes:
            for handler in self._routes[event.route]:
                try:
                    handler(event)    
                except Exception as e:
                    print e


class QueueEventEngine(_QueueEventEngine, _Timer):
    """ 事件引擎，必须注册完所有消息以后再启动。 """
    def __init__(self):
        _QueueEventEngine.__init__(self)
        _Timer.__init__(self, self)

    def start(self):
        """""" 
        _QueueEventEngine.start(self)
        _Timer.start_timer(self)
        return


class RPCClient(object):
    def __init__(self, event_engine, service, event_client=None, event_server=None):
        self.EVENT_CLIENT = event_client if event_client else "%s_CLIENT" % service.upper()
        self.EVENT_SERVER = event_server if event_server else "%s_SERVER" % service.upper()
        self.rid = 0
        self._handlers = { }
        self._handlers_lock = Lock()
        self._event_engine = event_engine
        self._event_engine.register(self.EVENT_SERVER, self._process_apiback)
        self._pause_condition = Condition()
        self._sync_ret = None
        self._timeout = 0
        self._timer_sleep = 1
        self._sync_call_time_lock = Lock()
        self._sync_call_time = datetime.now()
        timer = Thread(target = self._run_timer)
        timer.daemon = True
        timer.start()

    def _run_timer(self):
        while True:
            if not self._timeout == 0:
                with self._sync_call_time_lock:
                    mtime = self._sync_call_time
                delta = (datetime.now()-mtime).seconds
                if delta >= self._timeout:
                    #print "timeout", self._timeout, delta
                    # 不可重入，保证self.rid就是超时的那个
                    with self._handlers_lock:
                        del self._handlers[self.rid]
                    logger.debug("[RPCClient._runtimer] 处理超时, delete rid; %s" % self.rid)
                    self._timeout = 0
                    self._notify_server_data()
            sleep(self._timer_sleep)

    def _process_apiback(self, event):
        assert(event.route == self.EVENT_SERVER)
        self._timeout = 0
        rid = event.args['rid']
        try:
            with self._handlers_lock:
                handler = self._handlers[rid]
        except KeyError:
            logger.info('[RPCClient._process_apiback] 放弃超时任务的返回结果')
        else:
            try:
                if handler:
                    handler(event.args['ret'])
                else:
                    self._sync_ret = event.args['ret']
                    self._notify_server_data()
            except Exception as e:
                print e
            logger.debug("[RPCClient._process_apiback] 删除已经完成的任务 rid; %s" % rid)
            with self._handlers_lock:
                del self._handlers[rid]

    def call(self, apiname, args, handler):
        if not isinstance(args, dict):
            raise InvalidRPCClientArguments(argtype=type(args))
        assert(not handler ==  None)
        self.rid += 1
        args['apiname'] = apiname
        args['rid'] = self.rid
        self._event_engine.emit(Event(self.EVENT_CLIENT, args))
        with self._handlers_lock:
            self._handlers[self.rid] = handler

    def sync_call(self, apiname, args, timeout=10):
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
        self._event_engine.emit(Event(self.EVENT_CLIENT, args))
        with self._handlers_lock:
            self._handlers[self.rid] = None
        self._waiting_server_data()
        ret = self._sync_ret
        self._sync_ret = None
        return ret

    def _waiting_server_data(self):
        with self._pause_condition:
            self._pause_condition.wait()

    def _notify_server_data(self):
        with self._pause_condition:
            self._pause_condition.notify()


class RPCServer(object):
    def __init__(self, event_engine, service, event_client=None, event_server=None):
        self.EVENT_CLIENT = event_client if event_client else "%s_CLIENT" % service.upper()
        self.EVENT_SERVER = event_server if event_server else "%s_SERVER" % service.upper()
        self._event_engine = event_engine
        self._event_engine.register(self.EVENT_CLIENT, self._process_request)
        self._routes = { }
        self._routes_lock = Lock()

    def _process_request(self, event):
        #print "rpcsever: ", event.route, event.args
        args = event.args
        rid = args['rid']
        apiname = args['apiname']
        del args['rid']
        del args['apiname']
        try:
            with self._routes_lock:
                handler = self._routes[apiname]
            ret = handler(args)
        except Exception as e:
            print e, "****" 
        else:
            args = { 'ret': ret,
                    'rid': rid
            }
            self._event_engine.emit(Event(self.EVENT_SERVER, args))

    def register(self, route, handler):
        if route in self._routes:
            return False 
        with self._routes_lock:
            self._routes[route] = handler
        return True

    def unregister(self, route):
        with self._routes_lock:
            if route in self._routes:
                del self._routes[route]
