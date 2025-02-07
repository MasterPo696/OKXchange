import aiohttp
import asyncio
import json
import logging
from config import settings

async def get_spot_pairs():
    params = {"instType": "SPOT"} 
    async with aiohttp.ClientSession() as session:
        async with session.get(settings.OKX_API_URL, params=params) as response:
            data = await response.json()
            if data.get("code") == "0":
                pairs = [item["instId"] for item in data.get("data", [])]
                logging.info(f"Retrieved {len(pairs)} trading pairs.")
                return pairs
            else:
                logging.error(f"Error fetching trading pairs: {data}")
                return []