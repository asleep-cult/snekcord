import sys

sys.addaudithook(lambda *args: print(args))
sys.settrace(lambda *args: print(args))


async def abc():
    yield from range(10)


async def xyz():
    async yield from abc()


async def bbb():
    async for g in xyz():
        print('Hello', g)


coro = bbb()

while True:
    try:
        coro.send(None)
    except StopIteration:
        break


while True:
    continue
