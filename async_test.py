import asyncio
import ssl
import time
from aiohttp import ClientSession

url = 'https://github.com'

async def main(loop):
    session = ClientSession()
    start = time.time()
    task_times = []
    print('start at', start)

    for i in range(400):
        task_start = time.time()
        loop.create_task(req(i, session))
        task_end = time.time()
        task_times.append(task_end - task_start)

    end = time.time()
    print('end at', end)
    print('taken', sum(task_times), 'for every')
    print('taken', end - start, 'for all')
    session.close()

async def req(i, session):
    print('Init request', i)
    page = await session.get(url, ssl=ssl.SSLContext())
    page = await page.text()
    print(f'Request {i} done')

loop = asyncio.get_event_loop()
loop.create_task(main(loop))
loop.run_forever()


# import asyncio
# import random
#
# async def main(loop):
#     for i in range(3):
#         loop.create_task(handler(i))
#
# async def handler(i):
#     print("get", i)
#     await asyncio.sleep(random.random() * 2)
#     print("resolve", i)
#
# loop = asyncio.get_event_loop()
# loop.create_task(main(loop))
# loop.run_forever()
