import configargparse


def get_parser(is_registration: bool = False) -> configargparse.ArgumentParser:
    parser = configargparse.get_argument_parser()

    parser.add_argument("-h", '--host', default='minechat.dvmn.org',
                        help="Host name", type=str)
    parser.add_argument("-op", '--output_port', default=5050,
                        help="Port number", type=int)
    if is_registration:
        return parser
    parser.add_argument("-a", '--attempts', default=3,
                        help="Attempts to reconnect", type=int)
    parser.add_argument("-f", '--c', default='minechat.history',
                        help="Chat history file name", type=str)
    parser.add_argument("-ip", '--input_port', default=5000,
                        help="Port number", type=int)
    parser.add_argument("-f", '--file_name', default='minechat.history',
                        help="Chat history file name", type=str)
    return parser
