import asyncio
import tkinter as tk
import json
from typing import Tuple
from pathlib import PosixPath, Path
from utils.chat import open_connection, get_answer
from utils.parser import get_parser
from utils.files import write_line_to_file


async def get_account_hash(
        reader: asyncio.streams.StreamReader,
        writer: asyncio.streams.StreamReader,
        nick_name: str) -> dict:
    await get_answer(reader)
    writer.write('\n'.encode())
    await get_answer(reader)
    writer.write(f'{nick_name}\n'.encode())
    await writer.drain()
    credentials: dict = json.loads(
        await reader.readline())
    if 'account_hash' in credentials:
        print(credentials['account_hash'])
        return credentials['account_hash']


async def do_registartions(
        nick_name: str,
        host: str, port: str) -> None:

    async with open_connection(
            server=host, port=port,
            attempts=3) as rw:
        reader, writer = rw
        account_hash: str = await get_account_hash(
            reader, writer, nick_name)
        env_path: PosixPath = Path('.') / '.env'
        await write_line_to_file(env_path,
                                 f'TOKEN={account_hash}',
                                 mode='w')


def get_credentials(nick_name: str, label: tk.Label,
                    host: str, port: str):
    answer = tk.messagebox.askyesno(
        title="Warning",
        message=f"Is '{nick_name}' nick name correct?")
    if answer:
        asyncio.run(do_registartions(
            nick_name=nick_name,
            host=host, port=port))
        label['text'] = f'Now you can connect to chat as {nick_name}'


def get_window_center_dimensions(root) -> tuple:
    width_window: int = root.winfo_screenwidth()
    height_window: int = root.winfo_screenheight()
    center_width: int = width_window//2
    center_height: int = height_window//2
    return (center_width - 200, center_height-200)


def main():

    args = get_parser().parse_args()
    host: str = args.host
    port: str = args.output_port

    root = tk.Tk()
    root.title("Chat registration")
    root_width, root_height = get_window_center_dimensions(root)
    root.geometry(f'450x150+{root_width}+{root_height}')
    info_label = tk.Label(
        text="Enter you nick name",
        font="Arial 14 bold", pady=5)
    info_label.pack()
    nick_name_entry = tk.Entry(width=40)
    nick_name_entry.pack(pady=10)

    register_button = tk.Button(
        text='Register',
        width=15, height=3)
    register_button['command'] = lambda: get_credentials(
        nick_name=nick_name_entry.get(),
        label=info_label,
        host=host, port=port)
    register_button.pack()
    root.mainloop()


if __name__ == '__main__':
    main()
