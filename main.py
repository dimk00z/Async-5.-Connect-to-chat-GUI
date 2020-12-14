import asyncio
import gui
import logging
from tkinter import messagebox
from time import time
from utils.parser import get_parser
from utils.files import write_line_to_file, load_from_file
from utils.chat import open_connection, get_answer, login, write_message_to_chat, get_message_with_datetime
from utils.loggers import app_logger, watchdog_logger


async def read_msgs(host, port,
                    queue, histoty_queue,
                    file_name, connection_states, status_updates_queue, watchdog_queue, attempts=3):
    await load_from_file(file_name, message_queue=queue)
    async with open_connection(host, port, connection_states,
                               status_updates_queue, attempts) as rw:
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


async def send_msgs(host, port, token, connection_states, status_updates_queue, attempts, queue, watchdog_queue):
    async with open_connection(host, port, connection_states,
                               status_updates_queue, attempts) as rw:
        reader, writer = rw

        credentials = await login(reader, writer, token, queue)
        # print(credentials)
        event = gui.NicknameReceived(credentials['nickname'])
        status_updates_queue.put_nowait(event)
        while True:
            message = await queue.get()
            host_answer = await get_answer(reader)
            await write_message_to_chat(writer, message)
            app_logger.debug(get_message_with_datetime(message))


async def watch_for_connection(watchdog_queue):
    # TODO: listen / wait messages in watchdog_queue
    pass


async def main():

    parser = get_parser()
    args = parser.parse_args()
    host = args.host
    attempts = args.attempts
    input_port = args.input_port
    output_port = args.output_port
    history_file_name = args.file_name
    token = args.token
    token = 'd5a5384e-3a2c-11eb-8c47-0242ac110002'

    messages_queue = asyncio.Queue()
    sending_queue = asyncio.Queue()
    status_updates_queue = asyncio.Queue()
    histoty_queue = asyncio.Queue()
    watchdog_queue = asyncio.Queue()

    await asyncio.gather(
        read_msgs(host=host, port=input_port,
                  queue=messages_queue,
                  histoty_queue=histoty_queue,
                  file_name=history_file_name,
                  connection_states=gui.ReadConnectionStateChanged,
                  status_updates_queue=status_updates_queue,
                  watchdog_queue=watchdog_queue,
                  attempts=attempts),
        gui.draw(messages_queue=messages_queue,
                 sending_queue=sending_queue,
                 status_updates_queue=status_updates_queue),
        save_messages(histoty_queue=histoty_queue,
                      file_name=history_file_name),
        send_msgs(host=host, port=output_port,
                  token=token,
                  connection_states=gui.SendingConnectionStateChanged,
                  status_updates_queue=status_updates_queue,
                  attempts=attempts, watchdog_queue=watchdog_queue,
                  queue=sending_queue),
        watch_for_connection(watchdog_queue=watchdog_queue))


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, gui.TkAppClosed):
        print('----------------------------')
        print('Have a nice day even in 2020')
        print('----------------------------')
