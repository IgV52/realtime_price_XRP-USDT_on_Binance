from binance import Binance
import asyncio

async def main():
    price = Binance()
    await price.start()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Stop")


