import time

# -------------------------------------------------------------
# Server Class
# -------------------------------------------------------------
class Server:
    def __init__(self, server_id, cluster):
        self.id = server_id
        self.cluster = cluster
        self.leader = False
        self.alive = True

        self.lamport = 0
        self.balance = {"A": 1000}

    # ---------------- Lamport Clock ----------------
    def tick(self):
        self.lamport += 1

    def update_clock(self, external):
        self.lamport = max(self.lamport, external) + 1

    # ---------------- Bully Algorithm ---------------
    def start_election(self):
        if not self.alive:
            print(f"[Server {self.id}] Cannot start election, server is down")
            return

        print(f"[Server {self.id}] Starting Election...")
        higher_alive = False

        for s in self.cluster:
            if s.id > self.id and s.alive:
                higher_alive = True
                print(f"[Server {self.id}] Sending election msg to {s.id}")
                s.on_election_message(self.id)

        if not higher_alive:
            self.become_leader()

    def on_election_message(self, sender_id):
        if not self.alive:
            return
        print(f"[Server {self.id}] Received election message from {sender_id}")
        self.start_election()

    def become_leader(self):
        print(f"[Server {self.id}] I AM THE LEADER NOW!")
        for s in self.cluster:
            s.leader = (s.id == self.id)

    # ---------------- Transaction ------------------
    def deposit(self, account, amount):
        if not self.alive:
            print(f"[Server {self.id}] Cannot process transaction, server is down")
            return None

        if not self.leader:
            leader = self.get_leader()
            print(f"[Server {self.id}] Forwarding to Leader {leader.id}")
            return leader.deposit(account, amount)

        self.tick()  # leader event
        self.balance[account] += amount
        seq = self.lamport

        print(f"[Leader {self.id}] Applied deposit {amount} => New Balance = {self.balance[account]} (L={seq})")
        return seq

    def get_leader(self):
        for s in self.cluster:
            if s.leader and s.alive:
                return s
        print("‼ No leader available")
        return None

    # ---------------- Crash / Revive ---------------
    def crash(self):
        print(f"[Server {self.id}] Crashed")
        self.alive = False
        self.leader = False

    def revive(self):
        print(f"[Server {self.id}] Revived")
        self.alive = True


# -------------------------------------------------------------
# Initialize Cluster
# -------------------------------------------------------------
def create_cluster():
    s1 = Server(1, [])
    s2 = Server(2, [])
    s3 = Server(3, [])

    cluster = [s1, s2, s3]

    for s in cluster:
        s.cluster = cluster

    return cluster


# -------------------------------------------------------------
# Interactive Menu
# -------------------------------------------------------------
def menu(cluster):
    while True:
        print("\n----------------------")
        print("Distributed Banking Menu")
        print("----------------------")
        print("1. Start Leader Election")
        print("2. Crash a Server")
        print("3. Revive a Server")
        print("4. Perform Deposit Transaction")
        print("5. Show Leader & Balances")
        print("6. Exit")
        choice = input("Enter choice: ")

        if choice == "1":
            sid = int(input("Start election from server ID: "))
            cluster[sid - 1].start_election()

        elif choice == "2":
            sid = int(input("Crash server ID: "))
            cluster[sid - 1].crash()

        elif choice == "3":
            sid = int(input("Revive server ID: "))
            cluster[sid - 1].revive()

        elif choice == "4":
            from_id = int(input("Client sends request to server ID: "))
            amt = int(input("Deposit amount: "))
            cluster[from_id - 1].deposit("A", amt)

        elif choice == "5":
            leader = None
            for s in cluster:
                if s.leader and s.alive:
                    leader = s
            if leader:
                print(f"\nCurrent Leader: Server {leader.id}")
            else:
                print("\nNo active leader")

            print("\nBalances:")
            for s in cluster:
                status = "UP" if s.alive else "DOWN"
                print(f"Server {s.id} [{status}] : {s.balance}")

        elif choice == "6":
            print("Exiting...")
            break

        else:
            print("Invalid choice!")


# -------------------------------------------------------------
# Main
# -------------------------------------------------------------
if __name__ == "__main__":
    cluster = create_cluster()
    print("\n Distributed Banking Simulation Started")
    print("Run an election first to choose a leader.\n")
    menu(cluster)