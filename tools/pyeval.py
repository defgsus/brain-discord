import subprocess
import sys
import multiprocessing
import queue

__all__ = ("evaluate_python",)

MAX_SECONDS = 4

HEADER_CODE = """
from random import *
from math import *
from decimal import Decimal
D = Decimal
"""

SECURITY_CODE = """
def open(*args, **kwargs): 
    raise NotImplementedError("file access is not allowed")
def __import__(*args, **kwargs):
    raise NotImplementedError("module imports not allowed") 
def exec(*args, **kwargs):
    raise NotImplementedError("exec not allowed") 
def eval(*args, **kwargs):
    raise NotImplementedError("eval not allowed")
def compile(*args, **kwargs):
    raise NotImplementedError("compile not allowed")

__loader__ = None
__builtins__.__loader__ = None
__builtins__.__spec__ = None
__builtins__.open = open
__builtins__.__import__ = __import__
__builtins__.exec = exec
__builtins__.eval = eval
__builtins__.compile = compile 
"""


def evaluate_python_queue(code, queue):
    python = sys.executable
    code = """
%s
%s
print((lambda: %s)())
""" % (HEADER_CODE, SECURITY_CODE, code)
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


def test_security_code():
    """
    Go through the tree of all available global objects
    and see if we can find access to the module loader..
    """
    code = """
todo = list(globals().values())
visited = []

while todo:
    item = todo[0]
    todo = todo[1:]
    try:
        print("#", repr(item))
    except NotImplementedError:
        # _Printer.__repr__ needs open()
        pass
    visited.append(item)

    try:
        sub_items = list(vars(item).values())
        for s in sub_items:
            if s not in visited:
                todo.append(s)
    except TypeError:
        pass
    """
    code = """
%s
%s
%s
""" % (HEADER_CODE, SECURITY_CODE, code)
    python = sys.executable
    try:
        ret = subprocess.check_output(
            [python, "-c", code], stderr=subprocess.STDOUT,
        )
    except subprocess.CalledProcessError as e:
        print(e.output.decode("utf-8").strip())
        exit(-1)

    output = ret.decode("utf-8").strip()
    if "loader" in output.lower():
        exit(-1)


if __name__ == "__main__":

    if 1:
        print(evaluate_python('"*" * 10'))
        print(evaluate_python("'ä' * 10"))
        print(evaluate_python("blub"))
        print(evaluate_python("open('/var/log/syslog').read(1000)"))
        print(evaluate_python('__import__("os").system("ls")'))
        print(evaluate_python('__builtins__.__import__("os").system("ls")'))
        print(evaluate_python("__loader__"))
        print(evaluate_python('__builtins__.__spec__.loader.load_module("os").system("ls")'))
        #print(evaluate_python("time.sleep(10)"))

    if 1:
        test_security_code()
