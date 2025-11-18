"""
vector_clock_simulation.py

Simulates Vector Clocks for logical clock synchronization.
Processes generate internal, send, and receive events.
Demonstrates ordering rules in a simple distributed system.

Run:
    python vector_clock_simulation.py
"""

import time
import threading
import random
from dataclasses import dataclass


# -------------------------
# Vector Clock Utilities
# -------------------------

def vc_increment(vc, pid):
    vc[pid] += 1


def vc_update_on_receive(local_vc, incoming_vc, pid):
    # take elementwise max
    for i in range(len(local_vc)):
        local_vc[i] = max(local_vc[i], incoming_vc[i])
    # then increment own entry
    local_vc[pid] += 1


def vc_copy(vc):
    return [x for x in vc]


# -------------------------
# Message Container
# -------------------------

@dataclass
class Message:
    sender: int
    vc: list
    content: str


# -------------------------
# Process Class
# -------------------------

class Process(threading.Thread):
    def __init__(self, pid, total, inbox):
        super().__init__(daemon=True)
        self.pid = pid          # process ID
        self.total = total      # total number of processes
        self.vc = [0] * total   # initial vector clock
        self.inbox = inbox      # shared inbox (dict pid -> queue)
        self.running = True

    def internal_event(self):
        vc_increment(self.vc, self.pid)
        print(f"P{self.pid}: INTERNAL | VC={self.vc}")

    def send_event(self, to_pid, message):
        vc_increment(self.vc, self.pid)
        msg = Message(self.pid, vc_copy(self.vc), message)
        self.inbox[to_pid].append(msg)       # non-blocking queue
        print(f"P{self.pid}: SEND->P{to_pid} '{message}' | VC={self.vc}")

    def receive_event(self):
        if self.inbox[self.pid]:
            msg = self.inbox[self.pid].pop(0)
            vc_update_on_receive(self.vc, msg.vc, self.pid)
            print(f"P{self.pid}: RECV<-P{msg.sender} '{msg.content}' | (msg VC={msg.vc}) -> Updated VC={self.vc}")

    def run(self):
        # simulate 8 random events
        for _ in range(8):
            time.sleep(random.uniform(0.2, 0.7))
            event_type = random.choice(["internal", "send", "receive"])

            if event_type == "internal":
                self.internal_event()

            elif event_type == "send":
                # choose random other process
                to_pid = random.choice([i for i in range(self.total) if i != self.pid])
                self.send_event(to_pid, f"hello_from_{self.pid}")

            elif event_type == "receive":
                self.receive_event()

        print(f"P{self.pid}: finished simulation.")


# -------------------------
# Main Simulation
# -------------------------

def main():
    print("=== Vector Clock Simulation ===")
    num_processes = 3

    # inbox is a dict: pid -> list (acting as queue)
    inbox = {i: [] for i in range(num_processes)}

    processes = [Process(i, num_processes, inbox) for i in range(num_processes)]

    print("\nStarting processes...\n")
    for p in processes:
        p.start()

    for p in processes:
        p.join()

    print("\n=== Simulation complete ===")


if __name__ == "__main__":
    main()