import subprocess
import sys
import multiprocessing
import queue

__all__ = ("evaluate_python",)

MAX_SECONDS = 4


def evaluate_python_queue(code, queue):
    python = sys.executable
    code = """
import random
from math import *
print(%s)
""" % code
    try:
        ret = subprocess.check_output(
            [python, "-c", code], stderr=subprocess.PIPE,
        )
    except subprocess.CalledProcessError:
        queue.put("What?")
        return
    queue.put(ret.decode("utf-8").strip())


def evaluate_python(code):
    q = multiprocessing.Queue()
    thread = multiprocessing.Process(target=lambda: evaluate_python_queue(code, q))
    thread.start()

    try:
        ret = q.get(timeout=MAX_SECONDS)
    except queue.Empty:
        thread.terminate()
        return "Sorry, das dauerte mir zu lang.."

    thread.join()
    return ret


if __name__ == "__main__":

    print(evaluate_python('"*" * 10'))
    print(evaluate_python("'ä' * 10"))
    print(evaluate_python("blub"))
    #print(evaluate_python("time.sleep(10)"))

