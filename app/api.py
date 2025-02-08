import aiohttp
import asyncio
import json
import logging
from pymemcache.client import base
from config import settings

# Инициализация memcache клиента с пустым префиксом
memcache_client = base.Client(
    (settings.MEMCACHE_HOST, settings.MEMCACHE_PORT),
    key_prefix=b''
)

# Получение ВСЕХ пар со Спота
async def get_spot_pairs():
    params = {"instType": "SPOT"}
    async with aiohttp.ClientSession() as session:
        async with session.get(settings.OKX_API_URL, params=params) as response:
            data = await response.json()
            if data.get("code") == "0":
                pairs = list(set(item["instId"] for item in data.get("data", [])))
                logging.info(f"Retrieved {len(pairs)} unique trading pairs.")
                return pairs
            else:
                logging.error(f"Error fetching trading pairs: {data}")
                return []

async def subscribe_order_book(pairs):
    breaktime = 1
    unique_pairs = list(set(pairs))
    logging.info(f"Subscribing to {len(unique_pairs)} unique pairs.")

    while True:
        try:
            # Реконект происходит благодаря  бесконечному циклу и asyncio.sleep()
            async with aiohttp.ClientSession() as session:
                async with session.ws_connect(settings.WS_URL) as ws:
                    # Разбиваем список пар на группы по 20
                    chunk_size = 20
                    for i in range(0, len(unique_pairs), chunk_size):
                        chunk = unique_pairs[i:i + chunk_size]
                        params = [{"channel": "books", "instId": pair} for pair in chunk]
                        await ws.send_json({'op': 'subscribe', "args": params})
                        logging.info(f"Subscribed to {len(params)} pairs.")
                        await asyncio.sleep(1)  # Задержка между запросами

                    async for msg in ws:
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            data = json.loads(msg.data)
                            breaktime = 1
                            await process_order_book(data)
                        elif msg.type == aiohttp.WSMsgType.ERROR:
                            logging.error(f"WebSocket error: {msg.data}")
                            break
        except Exception as e:
            breaktime += 2
            logging.error(f"Error subscribing to pairs: {e}, retrying in {breaktime} sec...")
            await asyncio.sleep(breaktime)

# Обработка стаканов
async def process_order_book(data):
    if "arg" in data and "data" in data:
        inst_id = data["arg"]["instId"]
        order_book = data["data"][0]
        
        existing_book_raw = memcache_client.get(inst_id)
        if existing_book_raw:
            existing_book = json.loads(existing_book_raw.decode('utf-8'))
            existing_book["bids"] = merge_order_book(existing_book.get("bids", []), order_book.get("bids", []))
            existing_book["asks"] = merge_order_book(existing_book.get("asks", []), order_book.get("asks", []))
        else:
            existing_book = order_book

        # Кеш стакается наверх, образуя стек
        memcache_client.set(inst_id, json.dumps(existing_book))
        logging.info(f"Data for {inst_id} successfully saved in Memcached")

        check_existing_book = memcache_client.get(inst_id)
        if check_existing_book:
            logging.info(f"Successfully retrieved data for {inst_id}")
        else:
            logging.warning(f"No data found in Memcache for {inst_id}")

        # Логируем количество уникальных инструментов в Memcached
        keys = memcache_client.stats("items")
        unique_keys = len(keys) if keys else 0
        logging.info(f"Total unique pairs stored in Memcached: {unique_keys}")

# Объединение обновленных данных стакана с существующими
def merge_order_book(existing, updates):
    try:
        book = {entry[0]: entry[1] for entry in existing if len(entry) >= 2}
        for entry in updates:
            if len(entry) < 2:
                continue
            price, size = entry[0], entry[1]
            if float(size) > 0:
                book[price] = size
            elif price in book:
                del book[price]

        sorted_book = sorted(book.items(), key=lambda x: float(x[0]), reverse=True)
        logging.info(f"Updated order book with {len(sorted_book)} unique price levels.")
        return sorted_book
    except Exception as e:
        logging.error(f"Error in merge_order_book: {e}")
        raise
