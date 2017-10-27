import sys
import asyncio
import pytest
import aiohttp


@pytest.mark.skipIf(sys.version_info < (3, 0))
class TestAsyncVKSession(object):
    @pytest.mark.asyncio
    async def test_something(self):
        session = aiohttp.ClientSession()
        async with session.get('https://api.github.com/events') as resp:
            print("resp1: " + str(await resp.json()))

        async with session.get('https://api.github.com/events') as resp:
            print("resp2: " + str(await resp.json()))

        session.close()
