"""
Simple simulation of a distributed key-value store
showing Strong Consistency vs Eventual Consistency.

- 3 replicas: R1, R2, R3
- Client writes to R1 first
- Propagation to others is delayed
"""

import time
import threading

# ----------------- REPLICAS -----------------
replicas = {
    "R1": {},
    "R2": {},
    "R3": {}
}

# delay for updates to propagate to other replicas
PROPAGATION_DELAY = 3   # seconds


def show_all():
    print("\n--- Replica States ---")
    for r in replicas:
        print(f"{r}: {replicas[r]}")
    print("----------------------\n")


# ---------------- STRONG CONSISTENCY ----------------
def strong_write(key, value):
    """
    Strong consistency : write to ALL replicas immediately.
    """
    print(f"\n[STRONG WRITE] Setting {key} = {value} on ALL replicas")
    for r in replicas:
        replicas[r][key] = value


# ---------------- EVENTUAL CONSISTENCY ----------------
def eventual_write(key, value):
    """
    Eventual consistency: write to ONE replica immediately,
    propagate after delay to others.
    """
    print(f"\n[EVENTUAL WRITE] Setting {key} = {value} on R1 ONLY")
    replicas["R1"][key] = value

    # After some delay, propagate update
    def propagate():
        print(f"[Propagation after {PROPAGATION_DELAY}s] Updating R2 and R3...")
        replicas["R2"][key] = value
        replicas["R3"][key] = value
        print("[Propagation] Completed.")

    threading.Timer(PROPAGATION_DELAY, propagate).start()


# -------------------- MENU --------------------
def main():
    while True:
        print("1. Strong Write")
        print("2. Eventual Write")
        print("3. Show All Replicas")
        print("4. Exit")

        choice = input("Enter choice: ")

        if choice == "1":
            key = input("Enter key: ")
            val = input("Enter value: ")
            strong_write(key, val)

        elif choice == "2":
            key = input("Enter key: ")
            val = input("Enter value: ")
            eventual_write(key, val)

        elif choice == "3":
            show_all()

        elif choice == "4":
            break

        else:
            print("Invalid choice.\n")


if __name__ == "__main__":
    main()