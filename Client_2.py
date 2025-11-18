import xmlrpc.client

proxy = xmlrpc.client.ServerProxy("http://localhost:5000/")

print("Connected to Remote Execution Server")

while True:
    print("\n--- Remote Execution Menu ---")
    print("1. Arithmetic")
    print("2. Sorting")
    print("3. String Operation")
    print("4. Exit")

    choice = input("Enter choice: ")

    if choice == "1":
        expr = input("Enter arithmetic expression: ")
        result = proxy.execute("ARITH", {"expr": expr})
        print("Result:", result)

    elif choice == "2":
        nums = input("Enter comma-separated numbers: ")
        order = input("Descending? (yes/no): ").strip().lower() == "yes"
        result = proxy.execute("SORT", {"nums": nums, "desc": order})
        print("Result:", result)

    elif choice == "3":
        op = input("Operation (REVERSE/UPPER/LOWER/LENGTH/CONCAT): ")
        s1 = input("Enter string 1: ")
        s2 = ""
        if op.upper() == "CONCAT":
            s2 = input("Enter string 2: ")

        result = proxy.execute("STRING",
                               {"op": op, "s1": s1, "s2": s2})
        print("Result:", result)

    elif choice == "4":
        print("Exiting.")
        break

    else:
        print("Invalid choice.")
