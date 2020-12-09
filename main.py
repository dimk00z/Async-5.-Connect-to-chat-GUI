import asyncio
import gui
from tkinter import messagebox
from time import time
from utils.parser import get_parser
from utils.files import write_line_to_file, load_from_file
from utils.chat import open_connection, get_answer, login


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


async def send_msgs(host, port, token, attempts, queue):
    async with open_connection(host, port, attempts) as rw:
        reader, writer = rw

        credentials = await login(reader, writer, token)

        # while True:
        #     await submit_message(reader, writer)
        while True:
            msg = await queue.get()
            print(msg)


async def main():

    parser = get_parser()
    args = parser.parse_args()
    host = args.host
    attempts = args.attempts
    input_port = args.input_port
    output_port = args.output_port
    history_file_name = args.file_name
    token = args.token
    print(args)

    messages_queue = asyncio.Queue()
    sending_queue = asyncio.Queue()
    status_updates_queue = asyncio.Queue()
    histoty_queue = asyncio.Queue()

    await asyncio.gather(
        read_msgs(host=host, port=input_port,
                  queue=messages_queue,
                  histoty_queue=histoty_queue,
                  file_name=history_file_name,
                  attempts=attempts),
        gui.draw(messages_queue=messages_queue,
                 sending_queue=sending_queue,
                 status_updates_queue=status_updates_queue),
        save_messages(histoty_queue=histoty_queue,
                      file_name=history_file_name),
        send_msgs(host=host, port=output_port,
                  token=token, attempts=attempts, queue=sending_queue))


if __name__ == '__main__':
    asyncio.run(main())
