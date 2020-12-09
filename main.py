import asyncio
import gui
from utils import get_parser, open_connection, get_answer, write_line_to_file
from time import time


async def write_chat_line_to_file(chat_file_name, chat_line):
    async with aiofiles.open(chat_file_name, "a") as chat_history:
        await chat_history.write(chat_line)


async def read_msgs(host, port, queue, histoty_queue, attempts=3):
    async with open_connection(host, port, attempts) as rw:
        reader = rw[0]
        while True:
            message = await get_answer(reader)
            queue.put_nowait(message)
            histoty_queue.put_nowait(message)
            await asyncio.sleep(1)


async def save_messages(histoty_queue, file_name):
    while True:
        message = await histoty_queue.get()
        await write_line_to_file(chat_file_name=file_name, line=message)
# async def generate_msgs(queue):
#     while True:
#         message = f'Ping {int(time())}'
#         queue.put_nowait(message)
#         await asyncio.sleep(1)


async def main():

    parser = get_parser()
    args = parser.parse_args()
    print(args)

    messages_queue = asyncio.Queue()
    sending_queue = asyncio.Queue()
    status_updates_queue = asyncio.Queue()
    histoty_queue = asyncio.Queue()

    # messages_queue.put_nowait('Привет обитателям чата!')
    # messages_queue.put_nowait('Как дела?')
    # status_updates_queue.put_nowait(gui.ReadConnectionStateChanged.CLOSED)
    # event = gui.NicknameReceived('Василий Пупкин')
    # status_updates_queue.put_nowait(event)
    host = args.host
    attempts = args.attempts
    port = args.port
    history_file_name = args.file_name
    await asyncio.gather(
        read_msgs(host=host, port=port,
                  queue=messages_queue,
                  histoty_queue=histoty_queue,
                  attempts=attempts),
        gui.draw(messages_queue=messages_queue,
                 sending_queue=sending_queue,
                 status_updates_queue=status_updates_queue),
        save_messages(histoty_queue=histoty_queue,
                      file_name=history_file_name))


if __name__ == '__main__':
    asyncio.run(main())
