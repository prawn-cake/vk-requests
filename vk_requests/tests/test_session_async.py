import asyncio
import pytest
import aiohttp


@pytest.mark.asyncio
async def test_something():
    session = aiohttp.ClientSession()
    async with session.get('https://api.github.com/events') as resp:
        print("resp1: " + str(await resp.json()))

    async with session.get('https://api.github.com/events') as resp:
        print("resp2: " + str(await resp.json()))
