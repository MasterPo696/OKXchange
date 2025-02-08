import aiohttp
import asyncio
import json
import logging
from pymemcache.client import base
from config import settings

# Инициализация pymemcache клиента
memcache_client = base.Client((settings.MEMCACHE_HOST, settings.MEMCACHE_PORT))

# Функция для получения торговых пар
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

# Функция для подписки на канал order book
async def subscribe_order_book(pairs):
    breaktime = 1
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.ws_connect(settings.WS_URL) as ws:
                    params = [{"channel": "books", "instId": pair} for pair in pairs]
                    await ws.send_json({'op': 'subscribe', "args": params})
                    logging.info(f"Subscribed to order book")

                    async for msg in ws:
                        breaktime = 1
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            data = json.loads(msg.data)
                            
                            await process_order_book(data)  # Обработка данных стакана
                            # await asyncio.sleep(0.1)
                        elif msg.type == aiohttp.WSMsgType.ERROR:
                            logging.error(f"Error with subscribing to pairs: {msg.data}")
                            return
        except Exception as e:
            breaktime += 2
            logging.error(f"Error with subscribing to pairs: {e}, again in {breaktime} sec...")
            await asyncio.sleep(breaktime)

# Функция для обработки данных стакана и сохранения их в Memcache
async def process_order_book(data):
    if "arg" in data and "data" in data:
        inst_id = data["arg"]["instId"]
        order_book = data["data"][0]
        
        # Получаем данные стакана из Memcache
        existing_book_raw = memcache_client.get(inst_id)
        if existing_book_raw:
            existing_book = json.loads(existing_book_raw.decode('utf-8'))
            existing_book["bids"] = merge_order_book(existing_book.get("bids", []), order_book.get("bids", []))
            existing_book["asks"] = merge_order_book(existing_book.get("asks", []), order_book.get("asks", []))
        else:
            existing_book = order_book

        # Сохраняем обновлённый стакан в Memcache
        memcache_client.set(inst_id, json.dumps(existing_book), expire=10) # убрать expire
        logging.info(f"Updated order book for {inst_id}")

        # Для проверки данных в Memcache
        check_existing_book = memcache_client.get(inst_id)
        if check_existing_book:
            check_existing_book = json.loads(check_existing_book.decode('utf-8'))
            logging.info(f"Successfully retrieved data from Memcache for {inst_id}: {check_existing_book}")
        else:
            logging.warning(f"No data found in Memcache for {inst_id}")

# Функция для объединения стакана
def merge_order_book(existing, updates):
    book = {price: size for price, size in existing}
    for price, size in updates:
        if float(size) > 0:
            book[price] = size
        elif price in book:
            del book[price]
    return sorted(book.items(), key=lambda x: float(x[0]), reverse=True)



# Основная асинхронная функция
async def main():
    pairs = await get_spot_pairs()
    if pairs:
        await subscribe_order_book(pairs)
    else:
        logging.error("No trading pairs available to subscribe.")

# Запуск программы
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())

