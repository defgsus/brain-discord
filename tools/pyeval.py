import subprocess
import sys


def evaluate_python(code):
    python = sys.executable
    code = """
import random
print(%s)
""" % code
    try:
        ret = subprocess.check_output(
            [python, "-c", code], stderr=subprocess.PIPE,
        )
    except subprocess.CalledProcessError:
        return "What?"
    return ret.decode("utf-8").strip()


if __name__ == "__main__":

    print(evaluate_python('"*" * 10'))
    print(evaluate_python("'ä' * 10"))
    print(evaluate_python("blub"))

