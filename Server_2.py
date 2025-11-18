from xmlrpc.server import SimpleXMLRPCServer
from concurrent.futures import ThreadPoolExecutor
import threading


# ---------------- TASK EXECUTOR FUNCTIONS ----------------

def eval_arith(expr: str):
    """Safe arithmetic: + - * / and parentheses only."""
    allowed = "0123456789+-*/(). "
    if not all(c in allowed for c in expr):
        return "ERROR: Invalid characters"
    try:
        return str(eval(expr))
    except Exception as e:
        return f"ERROR: {str(e)}"


def sort_numbers(nums: str, descending: bool):
    try:
        arr = [int(x) for x in nums.split(",") if x.strip()]
        arr.sort(reverse=descending)
        return str(arr)
    except:
        return "ERROR: Bad number list"


def string_ops(op, s1, s2=""):
    op = op.upper()
    if op == "REVERSE":
        return s1[::-1]
    if op == "UPPER":
        return s1.upper()
    if op == "LOWER":
        return s1.lower()
    if op == "LENGTH":
        return str(len(s1))
    if op == "CONCAT":
        return s1 + s2
    return "ERROR: Unknown string operation"


# ---------------- CLASS FOR MULTITHREADED EXECUTION ----------------

class RemoteExecutor:
    def __init__(self):
        self.pool = ThreadPoolExecutor(max_workers=5)

    def execute(self, task_type, params):
        """Main RPC function called by clients."""

        future = self.pool.submit(self.run_task, task_type, params)
        return future.result()

    def run_task(self, task_type, params):
        """Worker thread executes the actual task."""

        print(f"[THREAD {threading.get_ident()}] Executing {task_type} -> {params}")

        if task_type == "ARITH":
            return eval_arith(params["expr"])

        if task_type == "SORT":
            nums = params["nums"]
            desc = params["desc"]
            return sort_numbers(nums, desc)

        if task_type == "STRING":
            return string_ops(params["op"], params["s1"], params.get("s2", ""))

        return "ERROR: Unknown Task"


# ---------------- START RPC SERVER ----------------

server = SimpleXMLRPCServer(("localhost", 5000), allow_none=True)
server.register_instance(RemoteExecutor())

print(">>> Remote Code Execution Server is running on port 5000")
server.serve_forever()