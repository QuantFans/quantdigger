mport datetime
import time

from ib.ext.Contract import Contract
from ib.ext.Order import Order
from ib.opt import ibConnection, message

from event import FillEvent, OrderEvent
from execution import ExecutionHandler

class IBExecutionHandler(ExecutionHandler):
    """
    Handles order execution via the Interactive Brokers
    API, for use against accounts when trading live
    directly.
    """

    def __init__(self, events, 
                 order_routing="SMART", 
                 currency="USD"):
        """
        Initialises the IBExecutionHandler instance.
        """
        self.events = events
        self.order_routing = order_routing
        self.currency = currency
        self.fill_dict = {}

        self.tws_conn = self.create_tws_connection()
        self.order_id = self.create_initial_order_id()
        self.register_handlers()


    def _error_handler(self, msg):
            """
            Handles the capturing of error messages
            """
            # Currently no error handling.
            print "Server Error: %s" % msg

        def _reply_handler(self, msg):
            """
            Handles of server replies
            """
            # Handle open order orderId processing
            if msg.typeName == "openOrder" and \
                msg.orderId == self.order_id and \
                not self.fill_dict.has_key(msg.orderId):
                self.create_fill_dict_entry(msg)
            # Handle Fills
            if msg.typeName == "orderStatus" and \
                msg.status == "Filled" and \
                self.fill_dict[msg.orderId]["filled"] == False:
                self.create_fill(msg)      
            print "Server Response: %s, %s\n" % (msg.typeName, msg)


    def create_tws_connection(self):
            """
            Connect to the Trader Workstation (TWS) running on the
            usual port of 7496, with a clientId of 10.
            The clientId is chosen by us and we will need 
            separate IDs for both the execution connection and
            market data connection, if the latter is used elsewhere.
            """
            tws_conn = ibConnection()
            tws_conn.connect()
            return tws_conn

    def create_initial_order_id(self):
            """
            Creates the initial order ID used for Interactive
            Brokers to keep track of submitted orders.
            """
            # There is scope for more logic here, but we
            # will use "1" as the default for now.
            return 1


    def register_handlers(self):
            """
            Register the error and server reply 
            message handling functions.
            """
            # Assign the error handling function defined above
            # to the TWS connection
            self.tws_conn.register(self._error_handler, 'Error')

            # Assign all of the server reply messages to the
            # reply_handler function defined above
            self.tws_conn.registerAll(self._reply_handler)


    def create_contract(self, symbol, sec_type, exch, prim_exch, curr):
            """
            Create a Contract object defining what will
            be purchased, at which exchange and in which currency.

            symbol - The ticker symbol for the contract
            sec_type - The security type for the contract ('STK' is 'stock')
            exch - The exchange to carry out the contract on
            prim_exch - The primary exchange to carry out the contract on
            curr - The currency in which to purchase the contract
            """
            contract = Contract()
            contract.m_symbol = symbol
            contract.m_secType = sec_type
            contract.m_exchange = exch
            contract.m_primaryExch = prim_exch
            contract.m_currency = curr
            return contract


     def create_order(self, order_type, quantity, action):
            """
            Create an Order object (Market/Limit) to go long/short.

            order_type - 'MKT', 'LMT' for Market or Limit orders
            quantity - Integral number of assets to order
            action - 'BUY' or 'SELL'
            """
            order = Order()
            order.m_orderType = order_type
            order.m_totalQuantity = quantity
            order.m_action = action
            return order


     def create_fill_dict_entry(self, msg):
            """
            Creates an entry in the Fill Dictionary that lists 
            orderIds and provides security information. This is
            needed for the event-driven behaviour of the IB
            server message behaviour.
            """
            self.fill_dict[msg.orderId] = {
                "symbol": msg.contract.m_symbol,
                "exchange": msg.contract.m_exchange,
                "direction": msg.order.m_action,
                "filled": False
            }


    def create_fill(self, msg):
            """
            Handles the creation of the FillEvent that will be
            placed onto the events queue subsequent to an order
            being filled.
            """
            fd = self.fill_dict[msg.orderId]

            # Prepare the fill data
            symbol = fd["symbol"]
            exchange = fd["exchange"]
            filled = msg.filled
            direction = fd["direction"]
            fill_cost = msg.avgFillPrice

            # Create a fill event object
            fill = FillEvent(
                datetime.datetime.utcnow(), symbol, 
                exchange, filled, direction, fill_cost
            )

            # Make sure that multiple messages don't create
            # additional fills.
            self.fill_dict[msg.orderId]["filled"] = True

            # Place the fill event onto the event queue
            self.events.put(fill_event)


    def execute_order(self, event):
            """
            Creates the necessary InteractiveBrokers order object
            and submits it to IB via their API.

            The results are then queried in order to generate a
            corresponding Fill object, which is placed back on
            the event queue.

            Parameters:
            event - Contains an Event object with order information.
            """
            if event.type == 'ORDER':
                # Prepare the parameters for the asset order
                asset = event.symbol
                asset_type = "STK"
                order_type = event.order_type
                quantity = event.quantity
                direction = event.direction

                # Create the Interactive Brokers contract via the 
                # passed Order event
                ib_contract = self.create_contract(
                    asset, asset_type, self.order_routing,
                    self.order_routing, self.currency
                )

                # Create the Interactive Brokers order via the 
                # passed Order event
                ib_order = self.create_order(
                    order_type, quantity, direction
                )

                # Use the connection to the send the order to IB
                self.tws_conn.placeOrder(
                    self.order_id, ib_contract, ib_order
                )

                # NOTE: This following line is crucial.
                # It ensures the order goes through!
                time.sleep(1)

                # Increment the order ID for this session
                self.order_id += 1
