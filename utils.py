import configargparse
import logging
import signal
import socket
import asyncio
import contextlib
import aiofiles


from datetime import datetime

ATTEMPT_DELAY_SECS = 3


def keyboard_interrupt_handler(signal, frame):
    print('\n[Program was closed]')
    exit(0)


@contextlib.asynccontextmanager
async def open_connection(server, port, attempts=1):
    attempt = 0
    connected = False
    while True:
        reader, writer = await asyncio.open_connection(server, port)
        try:
            logging.debug('The connection opened')
            signal.signal(signal.SIGINT, keyboard_interrupt_handler)
            connected = True
            yield reader, writer
            break
        except (ConnectionRefusedError, ConnectionResetError):
            if connected:
                logging.debug("The connection was closed")
                break
            if attempt >= attempts:
                logging.debug(
                    f"There is no connection. Next try in {ATTEMPT_DELAY_SECS} seconds")
                await asyncio.sleep(ATTEMPT_DELAY_SECS)
                continue
            attempt += 1
        finally:
            writer.close()
            await writer.wait_closed()
            logging.debug("Connection closed")


def get_parser():
    parser = configargparse.get_argument_parser()

    parser.add_argument("-h", '--host', default='minechat.dvmn.org',
                        help="Host name", type=str)
    parser.add_argument("-a", '--attempts', default=3,
                        help="Attempts to reconnect", type=int)
    parser.add_argument("-t", '--token',
                        help="Chat token", type=str)
    parser.add_argument("-f", '--c', default='minechat.history',
                        help="Chat history file name", type=str)
    parser.add_argument("-p", '--port', default=5000,
                        help="Port number", type=int)
    parser.add_argument("-f", '--file_name', default='minechat.history',
                        help="Chat history file name", type=str)
    return parser


def get_message_with_datetime(message):
    formated_datetime = datetime.now().strftime('%d.%m.%Y %H:%M')
    return f'[{formated_datetime}] {message}'


def decode_message(message):
    return message.decode('utf-8').strip()


async def get_answer(reader, use_datetime=True):
    answer = decode_message(await reader.readline())
    if use_datetime:
        answer = get_message_with_datetime(answer)
    logging.debug(answer)
    return answer


async def write_line_to_file(chat_file_name, line):
    async with aiofiles.open(chat_file_name, "a") as chat_history:
        await chat_history.write(f'{line}\n')
        logging.debug('chat_line')
