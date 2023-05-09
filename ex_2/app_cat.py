import threading
import urllib.request
from datetime import datetime
import time
from pathlib import Path
import multiprocessing

import asyncio
import aiohttp
import aiofiles


URL = 'https://cataas.com/cat'
OUT_PATH = Path(__file__).parent / 'cats'
OUT_PATH.mkdir(exist_ok=True, parents=True)
OUT_PATH = OUT_PATH.absolute()

answer = {}
l = (10, 50, 100)

sem = multiprocessing.Semaphore(multiprocessing.cpu_count())

# def my_timer(foo):
#     print(f"start time {start_time}")
#     def wrap(*args, **kwargs):
#         start_time = datetime.now()
#         func(*args, **kwargs)
#         elapsed_time = datetime.now()-start_time
#         print(elapsed_time)
#     return wrap


class MyTimer:
    def __init__(self):
        self._start_time = None
        self.elapsed_time = None

    def start(self):
        """Запуск нового таймера"""
        self._start_time = time.perf_counter()

    def stop(self):
        """Отстановить таймер и сообщить о времени вычисления"""
        self.elapsed_time = time.perf_counter() - self._start_time
        self._start_time = None
        # print(f"Прошло времени {self.elapsed_time:0.4f} секунд")

    def output(self):
        return f"{self.elapsed_time:0.5f}"


def get_cat(id):
    resource = urllib.request.urlopen(url=URL, timeout=30)
    file_path = "{}/{}.png".format(OUT_PATH, id)
    out = open(file_path, 'wb')
    out.write(resource.read())
    out.close()


def get_cat_threads(nums_cats):
    threads = []

    for i in range(nums_cats):
        name = 'thread_' + str(i)
        thread = threading.Thread(name=name, target=get_cat, args=(i,))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()


def get_car_multiprocessing(nums_cats):
    procs = []

    with sem:
        for i in range(nums_cats):
            proc = multiprocessing.Process(target=get_cat, args=(i,))
            proc.start()
            procs.append(proc)

        for proc in procs:
            proc.join()


async def get_cat_asicio(client: aiohttp.ClientSession, idx: int) -> bytes:
    async with client.get(URL) as response:
        result = await response.read()
        await write_to_disk(result, idx)


async def write_to_disk(content: bytes, id: int):
    file_path = "{}/{}.png".format(OUT_PATH, id)
    async with aiofiles.open(file_path, mode='wb') as f:
        await f.write(content)


async def get_all_cats(num_cats):
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(15)) as client:
        tasks = [get_cat_asicio(client, i) for i in range(num_cats)]
        return await asyncio.gather(*tasks)


def main():
    t = MyTimer()
    for num_cat in l:
        t.start()
        get_cat_threads(num_cat)
        t.stop()
        answer[str(num_cat)] = t.output()
    print("время выполнения на потоках")
    print(answer)

    for num_cat in l:
        t.start()
        get_car_multiprocessing(num_cat)
        t.stop()
        answer[str(num_cat)] = t.output()
    print("время выполнения на процессах")
    print(answer)

    for num_cat in l:
        t.start()
        asyncio.run(get_all_cats(num_cat))
        t.stop()
        answer[str(num_cat)] = t.output()
    print("время выполнения c asyncio")
    print(answer)



if __name__ == '__main__':
    main()
