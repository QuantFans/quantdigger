from rpc import EventRPCClient
from eventengine import ZMQEventEngine
import time
import sys



client_engine = ZMQEventEngine()
client_engine.start()
client = EventRPCClient(client_engine, 'test')
for i in xrange(0, 10):
    print client.sync_call("print_hello", { 'data': 'from_rpc_client' })
print "***************" 
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    client_engine.stop()
    sys.exit(0)
