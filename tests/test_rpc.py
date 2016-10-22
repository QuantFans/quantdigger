from quantdigger.event.eventengine import ZMQEventEngine
from rpc import EventRPCClient

engine = ZMQEventEngine('TestWindowGate')
engine.start()
client = EventRPCClient('client', engine, 'test')
client.sync_call('print_hello', { 'data': 'nihao' })
