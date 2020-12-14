import asyncio
import contextlib
import json
import enum
from utils.loggers import app_logger, watchdog_logger
from tkinter import messagebox


from datetime import datetime

ATTEMPT_DELAY_SECS = 3


class InvalidToken(Exception):
    def __init__(self, token: str) -> None:
        self.token: str = token
        messagebox_title: str = "Неверный токен"
        messagebox_message: str = f"Check the token '{self.token}'. Server hasn't accepted it. "
        messagebox.showinfo(messagebox_title, messagebox_message)

    def __str__(self) -> str:
        return f'Invalid token "{self.token}"'


@contextlib.asynccontextmanager
async def open_connection(server: str, port: str,
                          connection_states: enum.EnumMeta,
                          status_updates_queue: asyncio.queues.Queue,
                          attempts: int = 1) -> None:

    attempt: int = 0
    connected: bool = False
    while True:
        reader, writer = await asyncio.open_connection(server, port)
        try:
            app_logger.debug(f'The connection opened {server, port}')
            connected: bool = True
            status_updates_queue.put_nowait(
                connection_states.ESTABLISHED)
            yield reader, writer
            break
        except (ConnectionRefusedError, ConnectionResetError):
            if connected:
                app_logger.debug(f"The connection was closed {server, port}")
                break
            if attempt >= attempts:
                status_updates_queue.put_nowait(
                    connection_states.INITIATED)
                app_logger.debug(
                    f"There is no connection. Next try in {ATTEMPT_DELAY_SECS} seconds")
                await asyncio.sleep(ATTEMPT_DELAY_SECS)
                continue
            attempt += 1
        finally:
            writer.close()
            await writer.wait_closed()
            app_logger.debug(f"Connection closed {server, port}")
            status_updates_queue.put_nowait(
                connection_states.CLOSED)


def get_message_with_datetime(message: str) -> str:
    formated_datetime: str = datetime.now().strftime('%d.%m.%Y %H:%M')
    return f'[{formated_datetime}] {message}'


def decode_message(message: str) -> str:
    return message.decode('utf-8').strip()


async def get_answer(reader: asyncio.streams.StreamReader,
                     use_datetime: bool = True) -> str:
    answer: str = decode_message(await reader.readline())
    if use_datetime:
        answer: str = get_message_with_datetime(answer)
    app_logger.debug(answer)
    return answer


def sanitize(message: str) -> str:
    return message.replace("\n", "").replace("\r", "")


async def write_message_to_chat(writer: asyncio.streams.StreamReader,
                                message: str = '') -> None:
    message: str = "{}\n\n".format(sanitize(message))
    writer.write(message.encode())
    await writer.drain()


async def get_user_text(queue: asyncio.queues.Queue) -> str:
    return await queue.get()


async def register_user(reader: asyncio.streams.StreamReader,
                        writer: asyncio.streams.StreamReader,
                        queue: asyncio.queues.Queue,
                        after_incorrect_login: bool = False) -> dict:
    if after_incorrect_login == False:
        await get_answer(reader)
        await write_message_to_chat(writer)
    await get_answer(reader)
    writer.write('\n'.encode())
    nick_name: str = await get_user_text(queue)
    writer.write(f'{nick_name}'.encode())
    await writer.drain()
    credentials: dict = json.loads(await reader.readline())
    app_logger.debug(credentials)
    return credentials


async def authorise(token: str,
                    reader: asyncio.streams.StreamReader,
                    writer: asyncio.streams.StreamReader) -> dict:
    await get_answer(reader)
    await write_message_to_chat(writer, token)
    response: dict = json.loads(await reader.readline())
    app_logger.debug(response)
    return response


async def login(reader: asyncio.streams.StreamReader,
                writer: asyncio.streams.StreamReader,
                token: str, queue: asyncio.queues.Queue):

    # if token is None:
    #     print(token)
    #     return await register_user(reader, writer, queue)
    # TODO: доделать регистрацию!
    credentials: dict = await authorise(token, reader, writer)
    if credentials:
        return credentials
    raise InvalidToken(token)
