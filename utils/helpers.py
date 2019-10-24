import os
import sys
import subprocess
import re
from datetime import datetime
from dateutil import tz

from .terminal_formatter import Style

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import log  # noqa

logger = log.get_logger('Expense utils')

ISO_DATE_FORMAT = '%Y-%m-%d'


def get_commands(command):
    # TODO: enhance this, intelligent split
    if isinstance(command, list):
        splitted = command
    else:
        splitted = command.split('|')
    return [x.strip().split(' ') for x in splitted]


def pipe_commands_bg(commands):
    if not commands:
        return ""
    elif len(commands) == 1:
        process = subprocess.Popen(commands[0])
    else:
        process = subprocess.Popen(
            commands[0], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
        )
        curr_process = process
        for command in commands[1:-1]:
            p = subprocess.Popen(
                command, stdin=curr_process.stdout, stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL
            )
            curr_process = p
        p = subprocess.Popen(
            commands[-1], stdin=curr_process.stdout
        )
    return ""


def pipe_commands(commands):
    if not commands:
        return
    elif len(commands) == 1:
        process = subprocess.Popen(commands[0])
        o, e = process.communicate()
    else:
        process = subprocess.Popen(
            commands[0], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
        )
        curr_process = process
        for command in commands[1:-1]:
            p = subprocess.Popen(
                command, stdin=curr_process.stdout, stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL
            )
            curr_process = p
        p = subprocess.Popen(
            commands[-1], stdin=curr_process.stdout, stdout=subprocess.PIPE
        )
        process.wait()
        o = p.stdout.readlines()
        op = [try_decode(x) for x in o]
        return '\n'.join(op)


def try_decode(b):
    encodings = ['ascii', 'utf-8', 'latin']
    for e in encodings:
        try:
            return b.decode(e)
        except Exception:
            pass
    raise Exception('could not decode')


def try_encode(b):
    encodings = ['ascii', 'utf-8', 'latin']
    for e in encodings:
        try:
            return b.encode(e)
        except Exception:
            pass
    raise Exception('could not encode')


def is_url(string):
    return re.match('[a-z]+://.+', string)


def parse_integer(string):
    try:
        return int(string.strip())
    except (ValueError, TypeError):
        return None


def return_on_exception(function):
    def wrapped(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except Exception as e:
            logger.error('ERROR:', exc_info=True)
            return Style.red(str(e.args and e.args[0]))
    return wrapped


def parse_iso_date(date_str):
    try:
        return datetime.strptime(date_str, ISO_DATE_FORMAT)
    except (ValueError, TypeError) as e:
        print(e)
        return None


def to_local_date(date):
    return date.astimezone(tz.gettz())


def parse_duration(dur):
    """
    Parse strings like last month, year, etc to (1, month), (2, month), etc
    """
    duration = None
    n = 1
    if 'last' in dur:
        dur = dur.replace('last', '').strip()
        if 'month' in dur:
            dur = dur.replace('months', '').replace('month', '').strip()
            duration = 'month'
        elif 'year' in dur:
            dur = dur.replace('years', '').replace('year', '').strip()
            duration = 'year'
        elif 'week' in dur:
            dur = dur.replace('weeks', '').replace('week', '').strip()
            duration = 'week'
        elif 'day' in dur:
            dur = dur.replace('days', '').replace('day', '').strip()
            duration = 'day'
        # Now parse any number left
        n = parse_integer(dur) or 1
    return duration, n
