import subprocess


def get_commands(command):
    # TODO: enhance this, intelligent split
    if isinstance(command, list):
        splitted = command
    else:
        splitted = command.split('|')
    return [x.strip().split(' ') for x in splitted]


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
