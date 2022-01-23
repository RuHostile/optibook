import datetime as dt
import time
import random
import logging

from optibook.synchronous_client import Exchange

exchange = Exchange()
exchange.connect()

logging.getLogger('client').setLevel('ERROR')


def trade_would_breach_position_limit(instrument_id, volume, side, position_limit=0):
    positions = exchange.get_positions()
    position_instrument = positions[instrument_id]

    if side == 'bid':
        return position_instrument + volume > position_limit
    elif side == 'ask':
        return position_instrument - volume < -position_limit
    else:
        raise Exception(f'''Invalid side provided: {side}, expecting 'bid' or 'ask'.''')


def print_positions_and_pnl():
    positions = exchange.get_positions()
    pnl = exchange.get_pnl()

    print('Positions:')
    for instrument_id in positions:
        print(f'  {instrument_id:10s}: {positions[instrument_id]:4.0f}')

    print(f'\nPnL: {pnl:.2f}')


STOCK_A_ID = 'PHILIPS_A'
STOCK_B_ID = 'PHILIPS_B'

while True:
    print(f'')
    print(f'-----------------------------------------------------------------')
    print(f'TRADE LOOP ITERATION ENTERED AT {str(dt.datetime.now()):18s} UTC.')
    print(f'-----------------------------------------------------------------')

    print_positions_and_pnl()
    print(f'')

    # Flip a coin to select which stock to trade


    a_stock = exchange.get_last_price_book(STOCK_A_ID)
    b_stock = exchange.get_last_price_book(STOCK_B_ID)
    
    if not (a_stock and a_stock.bids and a_stock.asks and b_stock and b_stock.bids and b_stock.asks):
        print(f'Order book for {STOCK_A_ID} or {STOCK_B_ID} does not have bids or offers. Skipping iteration.')
        continue
    
    a_best_bid = a_stock.bids[0].price
    a_best_ask = a_stock.asks[0].price 
    b_best_bid = b_stock.bids[0].price
    b_best_ask = b_stock.asks[0].price
    print(a_best_bid, a_best_ask)
    print(b_best_bid, b_best_ask)

    diff1 = ((a_best_bid - b_best_ask)/((a_best_bid + b_best_ask)/2))*100

    diff2 = ((b_best_bid - a_best_ask)/((b_best_bid + a_best_ask)/2))*100
    
    print(exchange.poll_new_trades(STOCK_A_ID))
    print(exchange.poll_new_trades(STOCK_B_ID))


    if a_best_bid > (b_best_ask*diff1):
  
        time.sleep(0.04)
        exchange.insert_order(
            instrument_id=STOCK_B_ID,
            price=b_best_ask,
            volume=1,
            side="ask",
            order_type='ioc'
            )
        #time.sleep(0.04)
        exchange.insert_order(
            instrument_id=STOCK_A_ID,
            price=a_best_bid,
            volume=1,
            side="bid",
            order_type='ioc'
            )

    elif (a_best_ask*diff2) < b_best_bid:
        
        time.sleep(0.04)
        exchange.insert_order(
            instrument_id=STOCK_A_ID,
            price=a_best_ask,
            volume=200,
            side="ask",
            order_type='ioc'
            )
        #time.sleep(0.04)
        exchange.insert_order(
            instrument_id=STOCK_B_ID,
            price=b_best_bid,
            volume=200,
            side="bid",
            order_type='ioc'
            )
            
    else:
        time.sleep(5)
