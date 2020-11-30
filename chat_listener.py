import asyncio
import aiofiles
import configargparse
import logging
from utils import get_message_with_datetime, get_parser, \
    decode_message, open_connection, get_answer


async def write_chat_line_to_file(chat_file_name, chat_line):
    async with aiofiles.open(chat_file_name, "a") as chat_history:
        await chat_history.write(chat_line)


async def listen_to_chat(host, port,
                         chat_file_name, attempts):
    async with open_connection(host, port, attempts) as rw:
        reader = rw[0]
        while True:
            chat_line = await get_answer(reader)
            await write_chat_line_to_file(chat_file_name, f'{chat_line}\n')


def get_listener_args(parser):
    parser.add_argument("-f", '--file_name', default='minechat.history',
                        help="Chat history file name", type=str)
    parser.add_argument("-p", '--port', default=5000,
                        help="Port number", type=int)
    return parser.parse_args()


def main():
    logging.basicConfig(level=logging.DEBUG)
    parser = get_parser()
    args = get_listener_args(parser)
    host = args.host
    attempts = args.attempts
    chat_file_name = args.file_name
    port = args.port
    asyncio.run(listen_to_chat(host, port, chat_file_name, attempts))


if __name__ == "__main__":
    main()
