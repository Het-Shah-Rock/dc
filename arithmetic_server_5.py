"""
arithmetic_server.py
A simple distributed arithmetic service using XML-RPC in Python.
Run: python arithmetic_server.py
"""

from xmlrpc.server import SimpleXMLRPCServer

# The remote service class
class ArithmeticService:
    def add(self, a, b):
        print(f"Received add({a}, {b})")
        return a + b

    def sub(self, a, b):
        print(f"Received sub({a}, {b})")
        return a - b

    def mul(self, a, b):
        print(f"Received mul({a}, {b})")
        return a * b

# Start the RPC server
server = SimpleXMLRPCServer(("localhost", 9000), allow_none=True)
server.register_instance(ArithmeticService())

print("Arithmetic RPC Server running on port 9000...")
print("Methods: add(a,b), sub(a,b), mul(a,b)")

# Keep server alive
server.serve_forever()