from time import sleep
import asyncio

gens = []


async def asker(que):
    print(f'Напиши словами {que[1]}')



async def answer(queue):
    while queue:
        que = queue[0]
        # gen = asker(que)
        # next(gen)

        gen = asyncio.create_task(asker(que))
        await asyncio.gather(gen)
        ans = input()

        if ans == que[0]:
            print('Правильно!')
            del queue[0]
        else:
            print('Неправильно!')

    print('Ты все решил, молодец')


async def starter():
    queue = [['one', 1], ['two', 2], ['three', 3]]
    print('Начинаем викторину!')
    await answer(queue)


if __name__ == '__main__':
    asyncio.run(starter())




