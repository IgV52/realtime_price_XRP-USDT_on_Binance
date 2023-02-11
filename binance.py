from aiohttp import ClientSession

import asyncio
import numpy as np
import pandas as pd

class Binance:

    def __init__(self, timeout: int = 0.95):
        self.session = ClientSession()
        self.data = np.zeros(shape=(60, 60), dtype=np.float64)
        self.averange = np.array([0]*60, dtype=np.float64)
        self.timeout = timeout
        self.min = 0
        self.sec = 0

    async def drop_price(self, series):
        series = pd.Series(series)
        drop = ((series.pct_change(periods=(len(series)-1))).to_list())[-1] * 100
        if drop <= -1:
            print(f"Снижение цены на {abs(drop)}")

    async def wb(self):
        async with self.session.ws_connect('wss://ws-api.binance.com:443/ws-api/v3', autoping=True) as ws:
            while True:
                try:
                    await ws.send_json({
                        "id": "e2a85d9f-07a5-4f94-8d5f-789dc3deb097",
                        "method": "ticker.price",
                        "params": {
                            "symbol": "XRPUSDT"
                        }})
                    response = (await ws.receive()).json()
                    yield response['result']['price']
                except RuntimeError:
                    self.session.close()

    async def start(self):
        async for price in self.wb():
            self.data[self.min, self.sec] = float(price)
            await asyncio.sleep(self.timeout)
            if 0 <= self.sec <= 59:
                self.sec += 1
            if self.sec == 60:
                series = self.averange[np.nonzero(self.averange)]
                if len(self.averange) == len(series) and self.min != 59:
                    self.averange = np.append(self.averange[1:],np.average(self.data[self.min,:]))
                else:
                    self.averange[self.min] = np.average(self.data[self.min,:])
                self.min += 1
                self.sec = 0
                await self.drop_price(series=series)
            if self.min == 60:
                self.min = 0       
