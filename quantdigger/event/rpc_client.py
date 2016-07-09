from rpc import EventRPCClient
from eventengine import ZMQEventEngine
import time
import sys



client_engine = ZMQEventEngine('text')
client_engine.start()
client = EventRPCClient('test', client_engine, 'test')
for i in xrange(0, 5):
    print "sync_call: print_hello "
    print "return: ", client.sync_call("print_hello",
                            { 'data': 'from_rpc_client' })
    time.sleep(1)
print "***************" 
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    client_engine.stop()
    sys.exit(0)
