import asyncio
import gui
from utils import get_parser
from time import time



async def generate_msgs(queue):
    while True:
        message = f'Ping {int(time())}'
        queue.put_nowait(message)
        await asyncio.sleep(1)


async def main():

    parser = get_parser()
    args = parser.parse_args()
    print(args)

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
    asyncio.run(main())
