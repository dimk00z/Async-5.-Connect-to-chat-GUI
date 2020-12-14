import logging
import asyncio
import contextlib
import json
from tkinter import messagebox


from datetime import datetime

ATTEMPT_DELAY_SECS = 3


class InvalidToken(Exception):
    def __init__(self, token) -> None:
        self.token = token
        messagebox_title = "Неверный токен"
        messagebox_message = f"Check the token '{self.token}'. Server hasn't accepted it. "
        messagebox.showinfo(messagebox_title, messagebox_message)

    def __str__(self) -> str:
        return f'Invalid token "{self.token}"!'


@contextlib.asynccontextmanager
async def open_connection(server, port, connection_states,
                          status_updates_queue, attempts=1):

    attempt = 0
    connected = False
    while True:
        reader, writer = await asyncio.open_connection(server, port)
        try:
            logging.debug(f'The connection opened {server, port}')
            connected = True
            status_updates_queue.put_nowait(
                connection_states.ESTABLISHED)
            yield reader, writer
            break
        except (ConnectionRefusedError, ConnectionResetError):
            if connected:
                logging.debug(f"The connection was closed {server, port}")
                break
            if attempt >= attempts:
                status_updates_queue.put_nowait(
                    connection_states.INITIATED)
                logging.debug(
                    f"There is no connection. Next try in {ATTEMPT_DELAY_SECS} seconds")
                await asyncio.sleep(ATTEMPT_DELAY_SECS)
                continue
            attempt += 1
        finally:
            writer.close()
            await writer.wait_closed()
            logging.debug(f"Connection closed {server, port}")
            status_updates_queue.put_nowait(
                connection_states.CLOSED)


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
    raise InvalidToken(token)
