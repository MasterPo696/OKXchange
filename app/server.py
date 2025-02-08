# server.py
import json
import logging
from aiohttp import web
from pymemcache.client import base
from config import settings

# Инициализируем клиента для memcached с пустым префиксом
memcache_client = base.Client(
    (settings.MEMCACHE_HOST, settings.MEMCACHE_PORT),
    key_prefix=b''
)

async def index(request):
    text = (
        "<h1>Сервер Order Book</h1>"
        "<p>Доступные эндпоинты:</p>"
        "<ul>"
        "<li><a href='/orderbooks/{instrument_id}'>/orderbooks/{instrument_id}</a> — JSON-вывод для указанного инструмента</li>"
        "<li><a href='/pretty/{instrument_id}'>/pretty/{instrument_id}</a> — Красивый HTML‑вывод для указанного инструмента</li>"
        "<li><a href='/clear'>/clear</a> — Очистка memcached</li>"
        "</ul>"
    )
    return web.Response(text=text, content_type='text/html')

async def get_orderbook(request):
    instrument_id = request.match_info.get('instrument_id')
    logging.info(f"Запрос JSON для orderbook: {instrument_id}")
    try:
        data = memcache_client.get(instrument_id)
        logging.info(f"Попытка получить данные из memcached по ключу {instrument_id}: {data}")
    except Exception as e:
        logging.error(f"Ошибка при получении ключа {instrument_id} из memcached: {e}")
        return web.json_response({'error': 'Internal Server Error'}, status=500)

    if data:
        try:
            orderbook = json.loads(data.decode('utf-8'))
            logging.info(f"Декодированные данные для {instrument_id}: {orderbook}")
        except Exception as e:
            logging.error(f"Ошибка декодирования данных для {instrument_id}: {e}")
            return web.json_response({'error': 'Data corrupted'}, status=500)
        return web.json_response(orderbook)
    else:
        logging.info(f"Нет данных по ключу {instrument_id}")
        return web.json_response({'error': 'Order book not found'}, status=404)


async def pretty_orderbook(request):
    instrument_id = request.match_info.get('instrument_id')
    logging.info(f"Запрос красивого вывода для {instrument_id}")
    try:
        data = memcache_client.get(instrument_id)
    except Exception as e:
        logging.error(f"Ошибка получения ключа {instrument_id}: {e}")
        return web.Response(text="Internal Server Error", status=500)

    if not data:
        return web.Response(text="Order book not found", status=404)

    try:
        orderbook = json.loads(data.decode('utf-8'))
    except Exception as e:
        logging.error(f"Ошибка декодирования данных для {instrument_id}: {e}")
        return web.Response(text="Data corrupted", status=500)

    # Формируем HTML страницу
    html = f"<html><head><title>Order Book for {instrument_id}</title></head><body>"
    html += f"<h1>Order Book for {instrument_id}</h1>"
    
    if 'bids' in orderbook:
        html += "<h2>Bids</h2>"
        html += "<table border='1' cellspacing='0' cellpadding='5'><tr><th>Price</th><th>Size</th></tr>"
        for price, size in orderbook['bids'][:10]:
            html += f"<tr><td>{price}</td><td>{size}</td></tr>"
        html += "</table>"
    
    if 'asks' in orderbook:
        html += "<h2>Asks</h2>"
        html += "<table border='1' cellspacing='0' cellpadding='5'><tr><th>Price</th><th>Size</th></tr>"
        for price, size in orderbook['asks'][:10]:
            html += f"<tr><td>{price}</td><td>{size}</td></tr>"
        html += "</table>"
    
    html += "</body></html>"
    return web.Response(text=html, content_type='text/html')


async def clear_cache(request):
    logging.info("Запрос на очистку кэша memcached")
    try:
        memcache_client.flush_all()
        logging.info("Кэш успешно очищен")
        return web.json_response({'status': 'Cache cleared'})
    except Exception as e:
        logging.error(f"Ошибка при очистке кэша: {e}")
        return web.json_response({'error': str(e)}, status=500)


def init_app():
    app = web.Application()
    app.router.add_get('/', index)
    app.router.add_get('/orderbooks/{instrument_id}', get_orderbook)
    app.router.add_get('/pretty/{instrument_id}', pretty_orderbook)
    app.router.add_get('/clear', clear_cache)
    return app
