# dump_pairs.py
import asyncio
import json
import logging
from api import get_spot_pairs

logging.basicConfig(level=logging.INFO)

async def dump_pairs():
    pairs = await get_spot_pairs()
    if pairs:
        # Сохраняем список пар в файл pairs_dump.json
        with open("pairs_dump.json", "w", encoding="utf-8") as f:
            json.dump(pairs, f, indent=4, ensure_ascii=False)
        logging.info(f"Dumped {len(pairs)} trading pairs to pairs_dump.json")
    else:
        logging.error("No trading pairs were retrieved.")

if __name__ == "__main__":
    asyncio.run(dump_pairs())
