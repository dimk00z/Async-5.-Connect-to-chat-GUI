from tkinter import *
from tkinter import messagebox as mb
from typing import Tuple


def register_user(nick_name: str, label: tkinter.Label):
    answer = mb.askyesno(
        title="Warning",
        message=f"Is '{nick_name}' nick name correct?")
    if answer:
        label['text'] = f'Now you can connect to chat as {nick_name}'


def get_window_center_dimensions(root) -> tuple:
    width_window: int = root.winfo_screenwidth()
    height_window: int = root.winfo_screenheight()
    center_width: int = width_window//2
    center_height: int = height_window//2
    return (center_width - 200, center_height-200)


def main():

    root = Tk()
    root.title("Chat registration")
    root_width, root_height = get_window_center_dimensions(root)
    root.geometry(f'450x150+{root_width}+{root_height}')
    info_label = Label(text="Enter you nick name",
                       font="Arial 14 bold", pady=5)
    info_label.pack()
    print(type(info_label))
    entry = Entry(width=40)
    entry.pack(pady=10)

    register_button = Button(text='Register',
                             width=15, height=3)
    register_button['command'] = lambda: register_user(
        nick_name=entry.get(), label=info_label)
    register_button.pack()
    root.mainloop()


if __name__ == '__main__':
    main()
