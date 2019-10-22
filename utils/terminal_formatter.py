
STYLES = {
        'BLACK': '\033[30m',
        'RED': '\033[31m',
        'GREEN': '\033[32m',
        'YELLOW': '\033[33m',
        'BLUE': '\033[34m',
        'MAGENTA': '\033[35m',
        'CYAN': '\033[36m',
        'WHITE': '\033[37m',
        'NORMAL': '\033[0m',
}

BLACK = '\033[30m'
RED = '\033[31m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
BLUE = '\033[34m'
MAGENTA = '\033[35m'
CYAN = '\033[36m'
WHITE = '\033[37m'
NORMAL = '\033[0m'


class Style:
    def bold(s):
        return "\033[1m" + s + "\033[0m"

    def green(s):
        return GREEN + s + NORMAL

    def red(s):
        return RED + s + NORMAL

    def yellow(s):
        return YELLOW + s + NORMAL

    def blue(s):
        return BLUE + s + NORMAL

    def magenta(s):
        return MAGENTA + s + NORMAL

# TODO: make dynamic
