import aiofiles
import asyncio
from pathlib import Path


async def write_line_to_file(chat_file_name: str,
                             line: str) -> None:
    async with aiofiles.open(chat_file_name, "a") as chat_history:
        await chat_history.write(f'{line}\n')


async def load_from_file(file_name: str,
                         message_queue: asyncio.queues.Queue) -> None:
    if Path(file_name).is_file():
        async with aiofiles.open(file_name) as file:
            async for line in file:
                message_queue.put_nowait(line.strip())
