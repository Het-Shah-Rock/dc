"""
Simple TCP Client
Sends text requests to the multithreaded server.
"""

import socket

HOST = "127.0.0.1"
PORT = 5001

s = socket.socket()
s.connect((HOST, PORT))

print("Connected to server.")
print("Try commands: upper <text>, reverse <text>, length <text>, exit")

while True:
    msg = input("You: ")
    s.send(msg.encode())

    if msg.lower() == "exit":
        break

    reply = s.recv(1024).decode()
    print("Server:", reply)

s.close()
print("Disconnected.")
