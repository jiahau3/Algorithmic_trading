import sqlalchemy
import pandas as pd
import websockets
import json
import asyncio

symbol1 = 'btcbusd'
ticker1 = 'miniTicker'
stream = websockets.connect('wss://stream.binance.com:9443/stream?streams={}@{}'\
    .format(symbol1.lower(), ticker1))
dbfile = 'livedata.db'
engine = sqlalchemy.create_engine('sqlite:///{}'.format(dbfile))

async def main():
    async with stream as receiver:
        while True:
            data = await receiver.recv()
            data = json.loads(data)['data']
            df = getdataframe(data)
            # Show the streaming data
            print(df)
            # Store dataframe into database
            df.to_sql(symbol1, engine, if_exists='append', index=False)

def getdataframe(data):
    df = pd.DataFrame([data])
    df = df.loc[:, ['s', 'E', 'c']]
    df.columns = ['Symbol', 'Time', 'Price']
    df.Time = pd.to_datetime(df.Time, unit='ms')
    df.Price = df.Price.astype(float)
    return df

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
