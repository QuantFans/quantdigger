# encoding: UTF-8
##
# @file eventenvine.py
# @brief 
# @author wondereamer
# @version 0.1
# @date 2016-05-25
import unittest
from quantdigger.event import (
    QueueEventEngine,
    ZMQEventEngine,
    EventRPCClient,
    Event,
    Timer,
    EventRPCServer
)

def test_zmq_eventengine():
    """测试函数"""
    import sys
    from datetime import datetime
    import time
    
    def simpletest(event):
        print(str(datetime.now()), event.route)
    
    print('test_zmq_eventengine.....' )
    ee = ZMQEventEngine()
    ee.register(Event.TIMER, simpletest)
    timer = Timer(ee)
    ee.start()
    timer.start()
    event = Event(route=Event.TIMER)
    ee.emit(event)
    ## @TODO test_unregister

    #time.sleep(2)
    #ee.stop_timer()
    #time.sleep(2)
    #ee.resume_timer()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        timer.stop()
        ee.stop()
        sys.exit(0)


def test_eventengine():
    """测试函数"""
    import sys
    from datetime import datetime
    import time
    
    def simpletest(event):
        print(str(datetime.now()), event.route)
    
    ee = QueueEventEngine()
    timer = Timer(ee)
    ee.register(Event.TIMER, simpletest)
    ee.start()
    timer.start()

    time.sleep(2)
    timer.stop()
    time.sleep(2)
    timer.resume()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        ee.stop()
        timer.stop()
        sys.exit(0)


def test_rpc():
    import time
    import sys
    """""" 
    def server_print_hello(args):
        time.sleep(4) # 4秒处理时间
        print("server_print_hello")
        print("args: ", args)
        return 'data_sever_print_hello' 

    def client_print_hello(args):
        print("client_print_hello")
        print("args: ", args)

    # ------------------
    def test_call():
        ee = QueueEventEngine()
        client = EventRPCClient(ee, 'test')
        server = EventRPCServer(ee, 'test')
        server.register("server_print_hello", server_print_hello)
        ee.start()
        client.call("server_print_hello", { 'msg': 'parral_client'}, client_print_hello)
        return ee

    def test_sync_call(timeout):
        ee = QueueEventEngine()
        client = EventRPCClient(ee, 'test')
        server = EventRPCServer(ee, 'test')
        server.register("server_print_hello", server_print_hello)
        ee.start()
        print(client.sync_call("server_print_hello", { 'msg': 'sync_client'}, timeout), "**" )
        ee.stop()
        return

    test_sync_call(1)
    print("*****************" )
    test_sync_call(10)
    print("*****************" )
    ee = test_call()
    print("********************" )


    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        ee.stop()
        sys.exit(0)
    return
    
    
# 直接运行脚本可以进行测试
if __name__ == '__main__':
    test_zmq_eventengine()
    #test_eventengine()
    #test_rpc()


#class TestEventEngine(unittest.TestCase):
    #def test_get_qichats(self):
        #ret = get_qichats()
        #print(ret)
        #self.assertTrue(ret)



#if __name__ == '__main__':
    #unittest.main()
