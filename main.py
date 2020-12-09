import asyncio
import gui
from time import time
from utils import get_parser, open_connection, \
    get_answer, write_line_to_file, load_from_file


async def read_msgs(host, port,
                    queue, histoty_queue,
                    file_name, attempts=3):
    await load_from_file(file_name, message_queue=queue)
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


async def send_msgs(host, port, queue):
    while True:
        msg = await queue.get()
        print(msg)
    # async def generate_msgs(queue):
    #     while True:
    #         message = f'Ping {int(time())}'
    #         queue.put_nowait(message)
    #         await asyncio.sleep(1)


async def main():

    parser = get_parser()
    args = parser.parse_args()
    host = args.host
    attempts = args.attempts
    port = args.port
    history_file_name = args.file_name
    print(args)

    messages_queue = asyncio.Queue()
    sending_queue = asyncio.Queue()
    status_updates_queue = asyncio.Queue()
    histoty_queue = asyncio.Queue()

    await asyncio.gather(
        read_msgs(host=host, port=port,
                  queue=messages_queue,
                  histoty_queue=histoty_queue,
                  file_name=history_file_name,
                  attempts=attempts),
        gui.draw(messages_queue=messages_queue,
                 sending_queue=sending_queue,
                 status_updates_queue=status_updates_queue),
        save_messages(histoty_queue=histoty_queue,
                      file_name=history_file_name),
        send_msgs(host, port, sending_queue))


if __name__ == '__main__':
    asyncio.run(main())
