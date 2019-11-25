
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
    def bold(s):
        return "\033[1m" + s + "\033[0m"

    def green(s):
        return GREEN + s + NORMAL

    def light_green(s):
        return LIGHT_GREEN + s + NORMAL

    def light_purple(s):
        return LIGHT_PURPLE + s + NORMAL

    def brown(s):
        return BROWN + s + NORMAL

    def red(s):
        return RED + s + NORMAL

    def light_red(s):
        return LIGHT_RED + s + NORMAL

    def gray(s):
        return GRAY + s + NORMAL

    def yellow(s):
        return YELLOW + s + NORMAL

    def blue(s):
        return BLUE + s + NORMAL

    def magenta(s):
        return MAGENTA + s + NORMAL

# TODO: make dynamic
