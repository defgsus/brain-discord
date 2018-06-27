import subprocess
import sys
import multiprocessing
import queue

__all__ = ("evaluate_python",)

MAX_SECONDS = 4


def evaluate_python_queue(code, queue):
    python = sys.executable
    code = """
from random import *
from math import *
from decimal import Decimal as D
def open(*args, **kwargs): 
    raise NotImplementedError("file access is not allowed")
def __import__(*args, **kwargs):
    raise NotImplementedError("module imports not allowed") 
def exec(*args, **kwargs):
    raise NotImplementedError("exec not allowed") 
def eval(*args, **kwargs):
    raise NotImplementedError("eval not allowed")
__loader__ = None
__builtins__.open = open
__builtins__.__import__ = __import__
__builtins__.exec = exec
__builtins__.eval = eval 
_func123_ = lambda: %s
print(_func123_())
""" % code
    try:
        ret = subprocess.check_output(
            [python, "-c", code], stderr=subprocess.STDOUT,
        )
    except subprocess.CalledProcessError as e:
        queue.put("`%s`" % e.output.decode("utf-8").strip().split("\n")[-1])
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
    print(evaluate_python("open('/var/log/syslog').read(1000)"))
    print(evaluate_python('__import__("os").system("ls")'))
    print(evaluate_python('__builtins__.__import__("os").system("ls")'))
    print(evaluate_python("__loader__"))
    #print(evaluate_python("time.sleep(10)"))

