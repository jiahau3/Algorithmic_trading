import sqlalchemy
import pandas as pd
from binance.client import Client
import matplotlib.pyplot as plt

import os

test = True
if test:
    api_key = os.environ.get("B_API_TEST_KEY")
    api_secret = os.environ.get("B_API_TEST_SECRET")
else:
    api_key = os.environ.get("B_API_KEY")
    api_secret = os.environ.get("B_API_SECRET")    
dbfile = 'livedata.db'
symbol = 'btcbusd'
client = Client(api_key, api_secret, testnet=test)
engine = sqlalchemy.create_engine(f'sqlite:///{dbfile}')

buy_timestamp, sell_timestamp = [], []

initial_balance = client.get_asset_balance('busd')
# Get the minimum required quantity for the symbol tokens
def check_decimals(symbol):
    info = client.get_symbol_info(symbol)
    val = info['filters'][2]['stepSize']
    decimal = 0
    is_dec = False
    for c in val:
        if is_dec is True:
            decimal += 1
        if c == '1':
            break
        if c == '.':
            is_dec = True
    return decimal


# Create Buy order if the cumulative return is greater than entry value.
# Exit the position if cumulative return is greater than x%, or less than -y%
def trendfollowing(entry, lookback, quote_qty, gain, loss, open_position=False):
    while True:
        df = pd.read_sql(symbol, engine)
        df_lookback = df.iloc[-lookback:]
        cumret = (df_lookback.Price.pct_change() + 1).cumprod() - 1
        if not open_position:
            if cumret[cumret.last_valid_index()] > entry:
                order = client.create_order(symbol=symbol.upper(), side='BUY', type='MARKET', quantity=round(quote_qty / df_lookback.Price[cumret.last_valid_index()], check_decimals(symbol)))
                print(order)
                open_position = True
                buy_timestamp.append(df_lookback.Time[cumret.last_valid_index()])
                break
    if open_position:
        while True:
            df = pd.read_sql(symbol, engine)
            df_sincebuy = df.loc[df.Time > pd.to_datetime(order['transactTime'], unit='ms')]
            if len(df_sincebuy) > 1:
                cumret_sincebuy = (df_sincebuy.Price.pct_change() + 1).cumprod() - 1
                if cumret_sincebuy[cumret_sincebuy.last_valid_index()] > gain or cumret_sincebuy[cumret_sincebuy.last_valid_index()] < loss:
                    order = client.create_order(symbol=symbol.upper(), side='SELL', type='MARKET', quantity=round(quote_qty / df_sincebuy.Price[cumret_sincebuy.last_valid_index()], check_decimals(symbol)))
                    print(order)
                    open_position = False
                    sell_timestamp.append(df_sincebuy.Time[cumret_sincebuy.last_valid_index()])
                    break

def trade_records(buy_timestamp, sell_timestamp):
    buy_timestamp = pd.DataFrame(buy_timestamp)
    sell_timestamp = pd.DataFrame(sell_timestamp)
    buy_timestamp.to_csv('buytime.csv')
    sell_timestamp.to_csv('selltime.csv')
    

def show_transcation(df, buy_timestamp, sell_timestamp):
    df = df.set_index('Time')
    plt.figure(figsize=(15,6))
    plt.plot(df.Price)
    plt.scatter(buy_timestamp, df.loc[buy_timestamp].Price, marker='^', color='g', s=200)
    plt.scatter(sell_timestamp, df.loc[sell_timestamp].Price, marker='v', color='r', s=200)
    plt.show()
    
if __name__=='__main__':
    # Testing for 3 trades
    for i in range(3):
        trendfollowing(0.001, 60, quote_qty=20, gain=0.001, loss=-0.001)
    trade_records(buy_timestamp, sell_timestamp)
    # show_transcation(pd.read_sql(symbol, engine), buy_timestamp, sell_timestamp)
