import sys
import asyncio
import pytest
import aiohttp
from vk_requests import settings, API
from vk_requests.async.session import AsyncVKSession


@pytest.mark.skipIf(sys.version_info < (3, 0))
class TestAsyncVKSession(object):
    @staticmethod
    def get_real_vk_session(**kwargs):
        return AsyncVKSession(app_id=settings.APP_ID,
                              user_login=settings.USER_LOGIN,
                              user_password=settings.USER_PASSWORD,
                              phone_number=settings.PHONE_NUMBER, **kwargs)

    @pytest.mark.asyncio
    async def test_something(self):
        session = aiohttp.ClientSession()
        async with session.get('https://api.github.com/events') as resp:
            print("resp1: " + str(await resp.json()))

        async with session.get('https://api.github.com/events') as resp:
            print("resp2: " + str(await resp.json()))

        session.close()

    def test_run_future(self):
        loop = asyncio.get_event_loop()
        session = aiohttp.ClientSession()
        f = asyncio.ensure_future(session.get('https://api.github.com/events'))
        loop.run_until_complete(f)
        print(f.result())

    @pytest.mark.asyncio
    async def test_async_api(self):
        session = self.get_real_vk_session()
        api = API(session=session)
        result = await api.wall.get(owner_id=1)
        print(result)
