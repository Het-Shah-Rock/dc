import threading
import time
import uuid


KEY_TTL = 5 * 60           # key dies if no keep-alive for 5 minutes
AUTO_RELEASE = 60          # blocked keys auto-release after 60 seconds
SWEEP_INTERVAL = 5         # background check every 5 seconds

lock = threading.Lock()

# key_id -> metadata
keys = {}


def create_key():
    """Create a new API key."""
    k = str(uuid.uuid4())
    now = time.time()
    with lock:
        keys[k] = {
            "created": now,
            "last_keepalive": now,
            "blocked": False,
            "assigned_time": None,
        }
    print(f"[CREATE] New key generated: {k}")
    return k


def get_key():
    """Retrieve a non-blocked, non-expired key."""
    now = time.time()
    with lock:
        for k, meta in keys.items():
            if meta["blocked"]:
                continue
            if now - meta["last_keepalive"] > KEY_TTL:
                continue
            meta["blocked"] = True
            meta["assigned_time"] = now
            print(f"[ASSIGN] Key assigned: {k}")
            return k
    print("[ASSIGN] No available keys.")
    return None


def unblock_key(k):
    """Unblock (return) a previously assigned key."""
    with lock:
        if k not in keys:
            print("[UNBLOCK] Invalid key.")
            return
        keys[k]["blocked"] = False
        keys[k]["assigned_time"] = None
        print(f"[UNBLOCK] Key unblocked: {k}")


def keep_alive(k):
    """Refresh TTL of the key."""
    now = time.time()
    with lock:
        if k not in keys:
            print("[KEEPALIVE] Key does not exist.")
            return
        keys[k]["last_keepalive"] = now
        print(f"[KEEPALIVE] Refreshed key: {k}")


def sweeper():
    """Background thread: deletes expired keys and auto-releases long-blocked keys."""
    while True:
        time.sleep(SWEEP_INTERVAL)
        now = time.time()
        with lock:
            delete_list = []
            for k, meta in list(keys.items()):

                # delete expired
                if now - meta["last_keepalive"] > KEY_TTL:
                    delete_list.append(k)
                    continue

                # auto-release blocked keys after 60s
                if meta["blocked"] and meta["assigned_time"] is not None:
                    if now - meta["assigned_time"] > AUTO_RELEASE:
                        print(f"[SWEEPER] Auto-released key: {k}")
                        meta["blocked"] = False
                        meta["assigned_time"] = None

            for k in delete_list:
                print(f"[SWEEPER] Deleted expired key: {k}")
                del keys[k]


def print_status():
    """Print all keys and their statuses."""
    with lock:
        print("\n--- KEY STATUS ---")
        if not keys:
            print("No keys exist.")
        now = time.time()
        for k, meta in keys.items():
            ttl = KEY_TTL - int(now - meta["last_keepalive"])
            blk = "BLOCKED" if meta["blocked"] else "AVAILABLE"
            print(f"{k[:8]}...  | {blk} | TTL left: {ttl} sec")
        print("------------------\n")


# start sweeper thread
t = threading.Thread(target=sweeper, daemon=True)
t.start()

# ----------- MENU LOOP -------------
print("API KEY MANAGER SIMULATION (multithreaded)")
while True:
    print("\nChoose an action:")
    print("1 - Create new key")
    print("2 - Get available key")
    print("3 - Unblock key")
    print("4 - Keep alive key")
    print("5 - Show status")
    print("6 - Exit")

    choice = input("Enter choice: ")

    if choice == "1":
        create_key()

    elif choice == "2":
        get_key()

    elif choice == "3":
        k = input("Enter key: ")
        unblock_key(k)

    elif choice == "4":
        k = input("Enter key: ")
        keep_alive(k)

    elif choice == "5":
        print_status()

    elif choice == "6":
        print("Exiting...")
        break

    else:
        print("Invalid choice.")