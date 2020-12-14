import asyncio
from anyio import create_task_group, run
import gui
from async_timeout import timeout
from utils.parser import get_parser
from utils.files import write_line_to_file, load_from_file
from utils.chat import open_connection, get_answer, \
    login, write_message_to_chat, get_message_with_datetime, InvalidToken
from utils.loggers import app_logger, watchdog_logger


async def read_msgs(host, port,
                    file_name, connection_states,
                    queues, attempts=3):
    await load_from_file(file_name,
                         message_queue=queues['messages_queue'])
    async with open_connection(host, port,
                               connection_states,
                               queues['status_updates_queue'], attempts) as rw:
        reader = rw[0]
        while True:
            message = await get_answer(reader)
            queues['messages_queue'].put_nowait(message)
            queues['history_queue'].put_nowait(message)
            queues["watchdog_queue"].put_nowait(
                "Connection is alive. New message")


async def save_messages(history_queue, file_name):
    while True:
        message = await history_queue.get()
        await write_line_to_file(chat_file_name=file_name,
                                 line=message)


async def send_msgs(host, port, token,
                    connection_states,  attempts, queues):
    async with open_connection(host, port, connection_states,
                               queues['status_updates_queue'], attempts) as rw:
        reader, writer = rw

        credentials = await login(reader, writer,
                                  token, queues['sending_queue'])
        event = gui.NicknameReceived(credentials['nickname'])
        queues['status_updates_queue'].put_nowait(event)
        while True:
            message = await queues['sending_queue'].get()
            host_answer = await get_answer(reader)
            await write_message_to_chat(writer, message)
            queues["watchdog_queue"].put_nowait(
                "Connection is alive. Message sent")
            app_logger.debug(get_message_with_datetime(message))


async def watch_for_connection(watchdog_queue):
    while True:
        try:
            async with timeout(5):
                message = await watchdog_queue.get()
                watchdog_logger.info(message)
        except asyncio.TimeoutError:
            watchdog_logger.info('5s timeout is elapsed')
            raise ConnectionError


async def handle_connection(queues, history_file_name, host, ports, token, attempts):
    while True:
        try:
            async with create_task_group() as tg:

                await tg.spawn(read_msgs, host, ports['input_port'],
                               history_file_name, gui.ReadConnectionStateChanged,
                               queues, attempts)
                await tg.spawn(save_messages, queues['history_queue'],
                               history_file_name)
                await tg.spawn(send_msgs, host,
                               ports['output_port'], token,
                               gui.SendingConnectionStateChanged,
                               attempts, queues)
                await tg.spawn(watch_for_connection,
                               queues['watchdog_queue'])
        except ConnectionError as ex:
            app_logger.debug('Reconnecting to server')


async def main():

    parser = get_parser()
    args = parser.parse_args()
    host = args.host
    attempts = args.attempts
    ports = {
        'input_port': args.input_port,
        'output_port': args.output_port
    }

    history_file_name = args.file_name
    token = args.token
    token = 'd5a5384e-3a2c-11eb-8c47-0242ac110002'

    queues = {
        'messages_queue': asyncio.Queue(),
        'sending_queue': asyncio.Queue(),
        'status_updates_queue': asyncio.Queue(),
        'history_queue': asyncio.Queue(),
        'watchdog_queue': asyncio.Queue(),
    }
    async with create_task_group() as tg:
        await tg.spawn(gui.draw, queues['messages_queue'],
                       queues['sending_queue'],
                       queues['status_updates_queue'])
        await tg.spawn(handle_connection, queues, history_file_name,
                       host, ports, token, attempts)


if __name__ == '__main__':
    try:
        run(main)
    except (KeyboardInterrupt, gui.TkAppClosed, InvalidToken) as ex:
        if type(ex) is InvalidToken:
            print('----------------------------')
            print(ex)
        print('----------------------------')
        print('Have a nice day even in 2020')
        print('----------------------------')
