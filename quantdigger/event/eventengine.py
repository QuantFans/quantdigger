# encoding: UTF-8
##
# @file eventenvine.py
# @brief 
# @author wondereamer
# @version 0.1
# @date 2016-05-17
import zmq  
from time import sleep
from threading import Thread, Condition, Lock
from Queue import Queue, Empty


EVENT_TIMER = 'timer'


class Event:
    def __init__(self, route=None, args={ }):
        self.route = route
        self.args = args

    def __str__(self):
        return "route: %s\nargs: %s" % (self.route, self.args)


class _Timer(object):
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


class EventEngine(object):
    """docstring for Eve"""
    def __init__(self):
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
          不重复注册同一事件的同样回调。
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
        print 'emit' 
        
    def _run(self):
        """引擎运行"""
        while self._active == True:
            print "hello" 
            
    def _process(self, event):
        """处理事件"""
        if event.route in self._routes:
            for handler in self._routes[event.route]:
                try:
                    handler(event)    
                except Exception as e:
                    print e
        pass

    
class _QueueEventEngine(EventEngine):
    """
    基于线程队列的事件引擎。
    ## @note 必须注册完所有消息以后再启动。
    """
    def __init__(self):
        # 事件队列
        super(_QueueEventEngine, self).__init__()
        self._queue = Queue()

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
            

class QueueEventEngine(_QueueEventEngine, _Timer):
    """ 基于线程队列, 且带有定时器的事件引擎。 """
    def __init__(self):
        _QueueEventEngine.__init__(self)
        _Timer.__init__(self, self)

    def start(self):
        """""" 
        _QueueEventEngine.start(self)
        _Timer.start_timer(self)
        return


class ZMQEventEngine(EventEngine):
    """ 基于zeromq的事件引擎 """
    def __init__(self):
        super(ZMQEventEngine, self).__init__()
        self._server_context = zmq.Context()  
        self._server_socket = self._server_context.socket(zmq.REP)  
        self._server_socket.bind("tcp://*:5555")  

    def emit(self, event):
        """docstring for emit(self, eve)""" 
        return

    def _run(self):
        """""" 
        while self._active == True:
            try:
                # 获取事件的阻塞时间设为1秒
                event = self._queue.get(block=True, timeout=1)
                self._process(event)
            except Empty:
                pass
   
        while True:  
            #  Wait for next request from client  
            message = self._server_socket.recv()  
            print "Received request: ", message  
           
            #  Do some 'work'  
            time.sleep (1)        #   Do some 'work'  
           
            #  Send reply back to client  
            socket.send(message)



if __name__ == '__main__':
    import time
    zmq_engine = ZMQEventEngine()
    zmq_engine.start()
    time.sleep(1000)
