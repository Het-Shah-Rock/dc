"""
Simple Load Balancer Simulation
Backend servers simulated as threads.
Supports:
1. Round Robin
2. Least Connections

Run:
    python load_balancer.py
"""

import threading
import time
import random

# ---------------- Backend Server ----------------

class BackendServer:
    def __init__(self, sid):
        self.sid = sid
        self.active_connections = 0
        self.lock = threading.Lock()

    def handle_request(self, req_id):
        """Simulate serving a request."""
        with self.lock:
            self.active_connections += 1

        print(f"[Server {self.sid}] Handling request {req_id} | Active connections: {self.active_connections}")

        # simulate work
        time.sleep(random.uniform(0.5, 1.2))

        with self.lock:
            self.active_connections -= 1


# ---------------- Load Balancer ----------------

class LoadBalancer:
    def __init__(self, servers, strategy="round_robin"):
        self.servers = servers
        self.strategy = strategy
        self.rr_index = 0

    def select_server(self):
        """Choose a server based on selected strategy."""

        if self.strategy == "round_robin":
            server = self.servers[self.rr_index]
            self.rr_index = (self.rr_index + 1) % len(self.servers)
            return server

        elif self.strategy == "least_connections":
            return min(self.servers, key=lambda s: s.active_connections)

    def dispatch_request(self, req_id):
        srv = self.select_server()
        t = threading.Thread(target=srv.handle_request, args=(req_id,), daemon=True)
        t.start()
        return srv.sid


# ---------------- Simulation ----------------

def main():
    print("Load Balancer Simulation")
    print("1. Round Robin")
    print("2. Least Connections")

    choice = input("Choose algorithm: ")

    strategy = "round_robin" if choice == "1" else "least_connections"

    # create backend servers
    servers = [BackendServer(i) for i in range(1, 4)]   # 3 backend servers
    lb = LoadBalancer(servers, strategy)

    # simulate 10 incoming requests
    print(f"\nUsing strategy: {strategy}\n")
    print("Dispatching requests...\n")

    assignments = []

    for req in range(1, 11):
        sid = lb.dispatch_request(req)
        assignments.append((req, sid))
        time.sleep(0.2)  # small delay between incoming requests

    # wait for all threads to complete
    time.sleep(3)

    print("\n--- Load Distribution ---")
    for req, sid in assignments:
        print(f"Request {req} -> Server {sid}")

    print("\nActive connections after completion:")
    for s in servers:
        print(f"Server {s.sid}: {s.active_connections} active")


if __name__ == "__main__":
    main()