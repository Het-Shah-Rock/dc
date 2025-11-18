"""
Multithreaded TCP Server
Each client is handled in a separate thread.
Processes simple text requests (uppercase, reverse, length).
"""

import socket
import threading

HOST = "127.0.0.1"
PORT = 5001

def handle_client(conn, addr):
    print(f"[+] New client connected: {addr}")

    while True:
        data = conn.recv(1024).decode()
        if not data:
            break

        print(f"[Client {addr}] Sent: {data}")

        # process simple commands
        cmd = data.strip().lower()

        if cmd.startswith("upper "):
            msg = data[6:].upper()
        elif cmd.startswith("reverse "):
            msg = data[8:][::-1]
        elif cmd.startswith("length "):
            msg = str(len(data[7:]))
        elif cmd == "exit":
            msg = "Goodbye!"
            conn.send(msg.encode())
            break
        else:
            msg = "Unknown command. Use: upper <text>, reverse <text>, length <text>"

        conn.send(msg.encode())

    print(f"[-] Client disconnected: {addr}")
    conn.close()


# ---------------- MAIN SERVER ----------------
def main():
    print(f"Server running on {HOST}:{PORT}")
    s = socket.socket()
    s.bind((HOST, PORT))
    s.listen(5)

    while True:
        conn, addr = s.accept()
        t = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
        t.start()

if __name__ == "__main__":
    main()