import pandas as pd
from binance.client import Client
import sqlalchemy

def getSymbolpairs(quote_symbol='BUSD'):
    client = Client()
    info = client.get_exchange_info()
    # Select the token pairs end with BUSD
    symbols = [x['symbol'] for x in info['symbols'] if x['symbol'].endswith(quote_symbol)]
    return symbols

def getPricedata(symbol: str, kline_interval: str, date: str):
    client = Client()
    df = pd.DataFrame(client.get_historical_klines(symbol, kline_interval, date))
    if len(df) > 0:
        df = df.iloc[:,[0,1,2,3,4,5,9]]
        df.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Taker_buy_volume']
        df.Time = pd.to_datetime(df.Time, unit='ms')
        df = df.set_index('Time')
        df = df.astype(float)
        return df

def createDict(symbols):
    symbol_price_dict = {symbol: getPricedata(symbol, '1d', '2021-01-01') for symbol in symbols if getPricedata(symbol, '1d', '2021-01-01') is not None }
    return symbol_price_dict

def to_database(symbol_price_dict, dbfile: str):
    engine = sqlalchemy.create_engine('sqlite:///' + dbfile)
    for symbol, df in symbol_price_dict.items():
        df.to_sql(symbol, engine)
    print(f'Data imported to {dbfile}')
    return -1

if __name__ == '__main__':
    tokens = getSymbolpairs('BUSD')
    tokens_price_dict = createDict(tokens)
    to_database(tokens_price_dict, 'BUSDquote.db')
