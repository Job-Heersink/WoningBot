import json
import logging
import os
from typing import Optional

import httpx
from typing import Tuple

BASE_URL = "https://api.opencagedata.com/geocode/v1/json"

logger = logging.getLogger(__name__)

API_KEY = os.getenv("GEOCODING_API_KEY")


async def get_geocode(address: str = None, city: str = None, country: str = "Netherlands") -> Optional[Tuple[float, float]]:
    query_list = []
    for p in [address, city, country]:
        if p is not None:
            query_list.append(p)

    async with httpx.AsyncClient() as client:
        response = await client.get(BASE_URL, params={"q": ",".join(query_list), "key": API_KEY})

    if response.status_code != 200:
        raise Exception(f"Failed to fetch {BASE_URL}: {response.text}")

    response = response.json()
    rate = response.get("rate", {}).get("remaining", 0)
    if rate < 10:
        logger.warning(f"Geocoding API remaining allowed requests are low: {rate}")
    else:
        logger.debug(f"Geocoding API remaining allowed requests: {rate}")

    result = response.get("results", [])
    if len(result) == 0:
        return None

    return result[0]["geometry"]["lat"], result[0]["geometry"]["lng"]


if __name__ == '__main__':
    import asyncio

    asyncio.run(get_geocode("Kerkstraat 1", "Amsterdam"))
