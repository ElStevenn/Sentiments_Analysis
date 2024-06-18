import aiohttp
import asyncio
import os
import time
import hmac
import hashlib
import base64
from typing import Literal, Optional
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.bitget.com"

class BitgetExchange():

    def __init__(self) -> None:
        self.api_key = os.getenv("API_KEY")
        self.api_secret = os.getenv("API_SECRET")
        self.passphrase = os.getenv("API_PASSPHRASE")

        if not self.api_key or not self.api_secret or not self.passphrase:
            raise ValueError("API_KEY, API_SECRET, and API_PASSPHRASE must be set in the environment variables.")

    def generate_headers(self, method: str, path: str, params: dict, body: str = "") -> dict:
        timestamp = str(int(time.time() * 1000))
        query_string = '&'.join([f"{key}={value}" for key, value in sorted(params.items())])
        if query_string:
            full_path = f"{path}?{query_string}"
        else:
            full_path = path

        message = f"{timestamp}{method.upper()}{full_path}{body}"
        hmac_key = hmac.new(self.api_secret.encode(), message.encode(), hashlib.sha256).digest()
        sign = base64.b64encode(hmac_key).decode()
        
        headers = {
            "Content-Type": "application/json",
            "ACCESS-KEY": self.api_key,
            "ACCESS-SIGN": sign,
            "ACCESS-PASSPHRASE": self.passphrase,
            "ACCESS-TIMESTAMP": timestamp,
            "locale": "en-US"
        }
        return headers

    async def open_order(self):
        pass

    async def close_order(self):
        pass

    async def get_current_orders(self):
        pass

    async def get_positions(self):
        path = "/api/mix/v2/position/allPosition"
        url = BASE_URL + path
        params = {
            "productType": "USDT-FUTURES",
            "marginCoin": "usdt"
        }

        headers = self.generate_headers("GET", path, params)

        async with aiohttp.ClientSession() as session:
            result = await session.get(url=url, headers=headers, params=params)
            raw_response = await result.text()  # Get raw response text
            print("Raw Response:", raw_response)  # Print raw response for debugging
            try:
                response = await result.json(content_type=None)
            except Exception as e:
                print("Failed to parse JSON:", e)
                response = None
            await session.close()
        return response

# Example usage
bitget = BitgetExchange()

async def main():
    result = await bitget.get_positions()
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
