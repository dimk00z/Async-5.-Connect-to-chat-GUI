import asyncio
import gui
from time import time

# Программе понадобятся несколько параллельных задач —
# одна рисует окно интерфейса,
# другая слушает сервер,
# третья отравляет сообщения.


async def generate_msgs(queue):
    while True:
        message = f'Ping {int(time())}'
        queue.put_nowait(message)
        await asyncio.sleep(1)


async def main():
    # loop = asyncio.get_event_loop()

    messages_queue = asyncio.Queue()
    sending_queue = asyncio.Queue()
    status_updates_queue = asyncio.Queue()

    # messages_queue.put_nowait('Привет обитателям чата!')
    # messages_queue.put_nowait('Как дела?')
    # status_updates_queue.put_nowait(gui.ReadConnectionStateChanged.CLOSED)
    # event = gui.NicknameReceived('Василий Пупкин')
    # status_updates_queue.put_nowait(event)

    await asyncio.gather(
        generate_msgs(messages_queue),
        gui.draw(messages_queue=messages_queue,
                 sending_queue=sending_queue,
                 status_updates_queue=status_updates_queue))


if __name__ == '__main__':
    # main()
    asyncio.run(main())
