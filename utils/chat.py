import logging
import signal
import asyncio
import contextlib
import json

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


def sanitize(message):
    return message.replace("\n", "").replace("\r", "")


async def write_message_to_chat(writer, message=''):
    message = "{}\n\n".format(sanitize(message))
    writer.write(message.encode())
    await writer.drain()


async def get_user_text(queue):
    return await queue.get()


async def register_user(reader, writer, queue, after_incorrect_login=False):
    if after_incorrect_login == False:
        await get_answer(reader)
        await write_message_to_chat(writer)
    await get_answer(reader)
    writer.write('\n'.encode())
    nick_name = await get_user_text(queue)
    print(nick_name)
    writer.write(f'{nick_name}'.encode())
    await writer.drain()
    credentials = json.loads(await reader.readline())
    logging.debug(credentials)
    return credentials


async def authorise(token, reader, writer):
    host_answer = await get_answer(reader)
    await write_message_to_chat(writer, token)
    response = json.loads(await reader.readline())
    logging.debug(response)
    return response


async def login(reader, writer, token, queue):

    if token is None:
        print(token)
        return await register_user(reader, writer, queue)

    credentials = await authorise(token, reader, writer)
    if credentials:
        return credentials

    print('The current token is incorrect, we are going to create new user.')
    return await register_user(reader, writer, after_incorrect_login=True)
