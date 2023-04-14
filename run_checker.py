import subprocess


def bytes_to_str(s: bytes) -> str:
    """
    Converts bytes into string
    :param s: bytes variable
    :return: string from bytes
    """
    if s is None:
        return ''
    s = s.decode()
    s = s.replace('\\n', '\n')
    s = s.replace('\r', '')
    s = s.replace('\\r', '')
    s = s.replace('\\t', '')
    s = s.replace('\t', ' ')
    return s


def get_points(checker: str, answer: str) -> dict:
    """
    Returns points for user's answer corresponding to the task.
    :param checker: path to checking script
    :param answer: user's answer
    :return: points for user's answer
    """
    cmd = ["python3", f"{checker}"]
    process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    answer = answer.split('\n')
    for i in answer:
        process.stdin.write(i.encode())

    output, error = process.communicate()
    result = {
        'points': float(bytes_to_str(output)),
        'errors': bytes_to_str(error)
    }
    process.stdin.close()
    process.stdout.close()
    return result
