"""
distributed_logging.py

Simulates multiple servers producing logs with unsynchronized local clocks.
Uses Lamport logical clocks to produce a consistent global ordering.

Run: python distributed_logging.py
"""

import threading
import time
import random
from dataclasses import dataclass, field
from typing import List, Dict, Any

# ---------------- Config ----------------
NUM_SERVERS = 3
EVENTS_PER_SERVER = 8
MAX_EVENT_DELAY = 0.6   # max seconds between events (randomized)
SEED = 42               # reproducible demo

random.seed(SEED)


# ---------------- Data structures ----------------
@dataclass
class LogEntry:
    server_id: int
    local_ts: float           # raw timestamp at server (unsynchronized)
    lamport_ts: int           # lamport timestamp at send (incremented before send)
    message: str
    manager_receive_ts: float = field(default=0.0)  # set by LogManager on receipt


# ---------------- LogManager ----------------
class LogManager:
    def __init__(self):
        self.lock = threading.Lock()
        self.received_logs: List[LogEntry] = []
        self.lamport = 0  # manager's lamport clock

    def log_event(self, entry: LogEntry):
        """
        Called by servers to submit events.
        Follows Lamport rule: on receive, manager.lamport = max(manager.lamport, entry.lamport_ts) + 1
        Manager records the entry (manager_receive_ts and stores lamport if needed).
        """
        with self.lock:
            # Lamport receive event processing
            old_mgr = self.lamport
            self.lamport = max(self.lamport, entry.lamport_ts) + 1
            entry.manager_receive_ts = time.time()
            # store
            self.received_logs.append(entry)
            print(f"[Manager] Received from S{entry.server_id} | "
                  f"local={entry.local_ts:.4f} | send_lamport={entry.lamport_ts} "
                  f"| mgr_lamport={self.lamport} | msg='{entry.message}'")
            # return manager lamport to sender if needed (simulating RPC reply)
            return self.lamport

    def merged_logs(self):
        """
        Merge logs according to Lamport timestamps with server_id tie-breaker.
        Returns a sorted list.
        """
        with self.lock:
            # sort by lamport_ts asc, tie-breaker server_id asc, then local_ts for stability
            sorted_list = sorted(self.received_logs, key=lambda e: (e.lamport_ts, e.server_id, e.local_ts))
            return list(sorted_list)


# ---------------- Server (simulated) ----------------
class Server(threading.Thread):
    def __init__(self, server_id: int, manager: LogManager, events_to_gen: int, max_delay: float):
        super().__init__(daemon=True)
        self.server_id = server_id
        self.manager = manager
        self.events_to_gen = events_to_gen
        self.max_delay = max_delay
        self.lamport = 0  # local lamport clock
        # simulate unsynchronized physical clock by adding a small random offset
        # (not necessary for Lamport but useful to show raw timestamps differ)
        self.physical_clock_offset = random.uniform(-0.5, 0.5)

    def local_time(self):
        """Simulated local physical time (system time + offset)."""
        return time.time() + self.physical_clock_offset

    def send_event(self, message: str):
        """Create log event: increment lamport and send to manager (RPC simulation)."""
        # Lamport send event: increment local lamport before sending
        self.lamport += 1
        le = LogEntry(
            server_id=self.server_id,
            local_ts=self.local_time(),
            lamport_ts=self.lamport,
            message=message
        )
        # Simulate RPC call to manager (block until manager returns)
        mgr_lamport = self.manager.log_event(le)
        # On receive of reply from manager (a message event), update local lamport: max(local, mgr)+1
        self.lamport = max(self.lamport, mgr_lamport) + 1
        # Now lamport reflects the receive event as well

    def run(self):
        for i in range(self.events_to_gen):
            # generate a simple event message
            msg = f"evt-{i+1} from S{self.server_id}"
            # random delay to simulate asynchronous generation
            time.sleep(random.random() * self.max_delay)
            self.send_event(msg)
        print(f"[Server {self.server_id}] Done generating {self.events_to_gen} events.")


# ---------------- Demo runner ----------------
def demo():
    print("Distributed Logging Simulation with Lamport Logical Clocks")
    print(f"Servers: {NUM_SERVERS}, events/server: {EVENTS_PER_SERVER}\n")

    manager = LogManager()

    # create servers
    servers = [Server(sid + 1, manager, EVENTS_PER_SERVER, MAX_EVENT_DELAY) for sid in range(NUM_SERVERS)]

    # start all servers
    for s in servers:
        print(f"Starting Server {s.server_id} (clock offset {s.physical_clock_offset:+.3f}s)")
        s.start()

    # wait for all servers to finish
    for s in servers:
        s.join()

    print("\nAll servers finished producing events. Preparing merged global log...\n")
    merged = manager.merged_logs()

    # Print merged global timeline
    print("===== Centralized Merged Log (ordered by Lamport TS, tie-break by Server ID) =====")
    print(f"{'idx':>3} | {'S':>2} | {'send_lamport':>11} | {'mgr_recv_time':>12} | {'local_ts (server)':>18} | message")
    print("-" * 100)
    for idx, e in enumerate(merged, 1):
        print(f"{idx:3d} | S{e.server_id:>1d} | {e.lamport_ts:11d} | {e.manager_receive_ts:12.4f} | {e.local_ts:18.4f} | {e.message}")
    print("=" * 100)

    # Additional verification: ensure no server's own events are out-of-order in lamport timestamps
    print("\nVerifying per-server lamport monotonicity (should be strictly increasing):")
    per_server: Dict[int, List[int]] = {}
    for e in merged:
        per_server.setdefault(e.server_id, []).append(e.lamport_ts)
    ok = True
    for sid, seq in per_server.items():
        inc = all(x < y for x, y in zip(seq, seq[1:]))
        print(f" Server {sid}: events={len(seq)} lamport_increasing={inc} sequence={seq}")
        if not inc:
            ok = False
    if ok:
        print("\nVerification PASSED: per-server lamport timestamps strictly increase.")
    else:
        print("\nVerification FAILED: some server's lamport timestamps are not strictly increasing.")


if __name__ == "__main__":
    demo()