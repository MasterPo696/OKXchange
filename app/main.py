import asyncio
import logging
from aiohttp import web
from api import get_spot_pairs, subscribe_order_book
from server import init_app

async def main():
    pairs = await get_spot_pairs()
    if pairs:
        # Запускаем подписку на WebSocket в отдельной задаче
        asyncio.create_task(subscribe_order_book(pairs))
    else:
        logging.error("No trading pairs available to subscribe.")
    
    # Инициализируем и запускаем HTTP‑сервер
    app = init_app()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8080)
    await site.start()
    logging.info("Web server started on port 8080")
    
    # Бесконечный цикл, чтобы приложение не завершилось
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Shutting down.")
