"""
Minimal Ring Election Algorithm Simulation
- N processes arranged in a ring
- Highest ID wins
- Election message circulates clockwise
- Coordinator announces after election
"""

# Node states: True = alive, False = down
nodes = {
    1: True,
    2: True,
    3: True,
    4: True,
    5: True
}

coordinator = 5   # initially highest

def show_status():
    print("\nNode Status:")
    for n, alive in nodes.items():
        print(f" Node {n}: {'ALIVE' if alive else 'DOWN'}")
    print(f"Current Coordinator: {coordinator}\n")

def next_node(current):
    """Return next node in the ring (circular)."""
    ids = sorted(nodes.keys())
    idx = ids.index(current)
    return ids[(idx + 1) % len(ids)]

def start_election(starter):
    global coordinator
    if not nodes[starter]:
        print(f"Node {starter} is DOWN. Cannot start election.")
        return

    print(f"\n=== Ring Election started by Node {starter} ===")

    msg = [starter]   # election message containing IDs
    current = next_node(starter)

    # circulate until returns to starter
    while current != starter:
        print(f"Message at Node {current}: ", msg)

        if nodes[current]:            # alive? include in candidate list
            msg.append(current)
            print(f"Node {current} is ALIVE → Added to election list")
        else:
            print(f"Node {current} is DOWN → Skipped")

        current = next_node(current)

    print("\nElection message returned to starter.")
    print("Final candidate list:", msg)

    # pick highest alive node from msg
    coordinator = max(msg)
    print(f"\nNEW COORDINATOR ELECTED: Node {coordinator}")
    announce(coordinator)

def announce(leader):
    print("\nCoordinator Announcement:")
    current = next_node(leader)
    while current != leader:
        if nodes[current]:
            print(f"Node {leader} → Node {current}: I am coordinator.")
        current = next_node(current)

def kill_node(n):
    nodes[n] = False
    print(f"\n*** Node {n} is now DOWN ***")

def recover_node(n):
    nodes[n] = True
    print(f"\n*** Node {n} RECOVERED (alive again) ***")
    # ring algorithm does NOT auto-elect on recovery

# ---------------------- MENU ----------------------

while True:
    print("\n1. Show status")
    print("2. Kill a node")
    print("3. Recover a node")
    print("4. Start election")
    print("5. Exit")

    op = input("Enter choice: ")

    if op == "1":
        show_status()

    elif op == "2":
        n = int(input("Node to kill: "))
        kill_node(n)

    elif op == "3":
        n = int(input("Node to recover: "))
        recover_node(n)

    elif op == "4":
        n = int(input("Start election from node: "))
        start_election(n)

    elif op == "5":
        print("Exiting...")
        break

    else:
        print("Invalid input.")