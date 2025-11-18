"""
Minimal Bully Algorithm Simulation
- Nodes have IDs (higher = stronger)
- Some nodes may fail (down)
- Start an election from any alive node
- Prints step-by-step election flow
"""

# Node states (True = alive, False = down)
nodes = {
    1: True,
    2: True,
    3: True,
    4: True,
    5: True
}

coordinator = 5   # initially highest node


def show_status():
    print("\nNode Status:")
    for n, alive in nodes.items():
        print(f" Node {n} : {'ALIVE' if alive else 'DOWN'}")
    print(f"Current Coordinator: {coordinator}\n")


def start_election(starter):
    global coordinator
    print(f"\n=== Election started by Node {starter} ===")

    # Check if starter itself is alive
    if not nodes[starter]:
        print(f"Node {starter} is DOWN. Cannot start election.")
        return

    higher_nodes = [n for n in nodes if n > starter]

    got_response = False

    # Send ELECTION messages
    for h in higher_nodes:
        print(f"Node {starter} --> Node {h} : ELECTION?")
        if nodes[h]:
            print(f"Node {h} replies: OK")
            got_response = True

    if not got_response:
        # no higher node alive → starter becomes coordinator
        coordinator = starter
        print(f"\nNode {starter} becomes the COORDINATOR")
        announce(starter)
    else:
        print(f"\nNode {starter} waits… higher node(s) will take over election.")
        # Highest alive node becomes coordinator
        for n in sorted(nodes.keys(), reverse=True):
            if nodes[n]:
                coordinator = n
                print(f"Node {n} is highest alive → becomes COORDINATOR")
                announce(n)
                break


def announce(leader):
    print("\nCOORDINATOR ANNOUNCEMENT:")
    for n in nodes:
        if nodes[n] and n != leader:
            print(f"Node {leader} --> Node {n}: I am the new coordinator.")


def kill_node(n):
    nodes[n] = False
    print(f"\n*** Node {n} is now DOWN ***")


def recover_node(n):
    nodes[n] = True
    print(f"\n*** Node {n} has RECOVERED ***")
    # bully rule: recovered higher node starts election
    start_election(n)


# ----------------- SIMPLE MENU -----------------

while True:
    print("\n1. Show status")
    print("2. Kill a node")
    print("3. Recover a node")
    print("4. Start election")
    print("5. Exit")

    choice = input("Enter choice: ")

    if choice == "1":
        show_status()

    elif choice == "2":
        n = int(input("Node to kill: "))
        kill_node(n)

    elif choice == "3":
        n = int(input("Node to recover: "))
        recover_node(n)

    elif choice == "4":
        n = int(input("Start election from node: "))
        start_election(n)

    elif choice == "5":
        print("Exiting...")
        break

    else:
        print("Invalid choice.")
