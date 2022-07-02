import pandas as pd
from binance.client import Client
import sqlalchemy

def getSymbolpairs(quote_symbol):
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

def createDataframe(symbols):
    symbol_price = {}
    for symbol in symbols:
        df = getPricedata(symbol, '1d', '2019-01-01')
        if df is not None:
            symbol_price[symbol] = df
    symbol_price = pd.concat(symbol_price).reset_index()
    symbol_price = symbol_price.rename(columns={'level_0': 'Symbol'})
    return symbol_price

def to_database(symbol_price, tablename, dbfile: str):
    engine = sqlalchemy.create_engine('sqlite:///' + dbfile)
    symbol_price.to_sql(tablename, engine, index=False)
    print(f'Data imported to {dbfile}')
    return -1

def create_cryptoList():
    
    pass

if __name__ == '__main__':
    tokens = getSymbolpairs('BUSD')
    tokens_price = createDataframe(tokens)
    to_database(tokens_price, 'crypto_price', 'BUSDquote.db')
