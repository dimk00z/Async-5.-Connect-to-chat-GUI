import configargparse


def get_parser():
    parser = configargparse.get_argument_parser()

    parser.add_argument("-h", '--host', default='minechat.dvmn.org',
                        help="Host name", type=str)
    parser.add_argument("-a", '--attempts', default=3,
                        help="Attempts to reconnect", type=int)
    parser.add_argument("-t", '--token',
                        help="Chat token", type=str)
    parser.add_argument("-f", '--file_name', default='minechat.history',
                        help="Chat history file name", type=str)
    parser.add_argument("-p", '--port', default=5000,
                        help="Port number", type=int)
    return parser
