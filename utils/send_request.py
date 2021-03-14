import logging
import asyncio
import aioschedule
import httpx


async def sending_aio_request():
    requests = httpx.get('https://cosmosalonbot.herokuapp.com/')
    logging.info(f'Send Request {requests.status_code}')


async def send_request():
    aioschedule.every(5).minutes.do(sending_aio_request)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)
