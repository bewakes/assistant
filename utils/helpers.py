import subprocess


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
        output = p.stdout.read().decode()
        return output
