
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
LIGHT_GREEN = '\033[1;32m'
MAGENTA = '\033[35m'
CYAN = '\033[36m'
WHITE = '\033[37m'
GRAY = '\033[0;30m'
NORMAL = '\033[0m'
LIGHT_RED = '\033[1;31m'
BROWN = '\033[1;33m'
LIGHT_PURPLE = '\033[0;35m'


class Style:
    @staticmethod
    def bold(s: str):
        return "\033[1m" + s + "\033[0m"

    @staticmethod
    def green(s: str):
        return GREEN + s + NORMAL

    @staticmethod
    def light_green(s: str):
        return LIGHT_GREEN + s + NORMAL

    @staticmethod
    def light_purple(s: str):
        return LIGHT_PURPLE + s + NORMAL

    @staticmethod
    def brown(s: str):
        return BROWN + s + NORMAL

    @staticmethod
    def red(s: str):
        return RED + s + NORMAL

    @staticmethod
    def light_red(s: str):
        return LIGHT_RED + s + NORMAL

    @staticmethod
    def gray(s: str):
        return GRAY + s + NORMAL

    @staticmethod
    def yellow(s: str):
        return YELLOW + s + NORMAL

    @staticmethod
    def blue(s: str):
        return BLUE + s + NORMAL

    @staticmethod
    def magenta(s: str):
        return MAGENTA + s + NORMAL

# TODO: make dynamic
