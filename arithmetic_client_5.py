"""
arithmetic_client.py
Client that invokes remote arithmetic functions via XML-RPC.
Run: python arithmetic_client.py
"""

import xmlrpc.client

proxy = xmlrpc.client.ServerProxy("http://localhost:9000/")

print("Connected to remote Arithmetic Service")

while True:
    print("\nChoose Operation:")
    print("1. Add")
    print("2. Subtract")
    print("3. Multiply")
    print("4. Exit")

    choice = input("Enter choice: ")

    if choice == "4":
        break

    a = float(input("Enter value A: "))
    b = float(input("Enter value B: "))

    if choice == "1":
        res = proxy.add(a, b)
        print("Result =", res)

    elif choice == "2":
        res = proxy.sub(a, b)
        print("Result =", res)

    elif choice == "3":
        res = proxy.mul(a, b)
        print("Result =", res)

    else:
        print("Invalid choice.")