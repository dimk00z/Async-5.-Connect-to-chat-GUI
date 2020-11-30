# Asyc. Lesson 5. Connecting to chat

This is a solution of the task to connect to a chat using async python libraries. 

There are two scripts:

`chat_listener.py` - allows to write all chat messages to file

`chat_writer.py` - uses for sending messages to the chat.

## How to install

Python version required: 3.7+

```bash
pip install -r requirements.txt
```

## How to launch

Both scripts have these parameters:

1. `-h`, `--host` - chat host, default is `minechat.dvmn.org`
2. `-p`, `--port` - port number
3. `-a`, `--attempts` - number of attemts for reconnections, default is `3`

Specific parameters:

* For  `chat_listener.py`:

`-f`, `--file_name` - file name for saving chat history, default is `minechat.history`

* For  `chat_writer.py`:

`-t`, `--token` - chat token if you have one

Using example:

```bash
python chat_listener.py -h minechat.dvmn.org -p 5000 -a 3

```
```bash
python chat_writer.py -h minechat.dvmn.org -p 5000 -a 3 -f minechat.history

```

# Project's aims

This code was written for learning Python course [Devman](https://dvmn.org).