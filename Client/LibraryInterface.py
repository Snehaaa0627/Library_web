import socket

class LibraryInterface:
    def __init__(self, hostname, port):
        self.hostname = hostname
        self.port = port

    def send_request(self, command):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((self.hostname, self.port))  # Connect to the server

        # Send the command to the server
        client.send(command.encode('utf-8'))

        # Receive and print the server's response
        response = client.recv(1024).decode('utf-8').strip()

        client.close()

        return response
    
    def get_room_statistics(self):
        response = self.send_request("get_room_statistics")
        statistics = []
        for result in response.split(" "):
            statistics.append(result.split(":"))
        return statistics

    def register_user(self, username, password):
        return self.send_request(f"register_user {username} {password}") == "True"

    def authenticate_user(self, username, password):
        return self.send_request(f"authenticate_user {username} {password}") == "True"

    def set_user_room(self, username, room_name):
        return self.send_request(f"set_user_room {username} {room_name}") == "True"

    def reset_user_room(self, username):
        return self.send_request(f"reset_user_room {username}") == "True"

    def check_present(self, book_name):
        return self.send_request(f"check_present {book_name}") == "True"

    def get_available_bookid(self, book_name):
        return int(self.send_request(f"get_available_bookid {book_name}"))

    def request_book(self, username, book_id):
        response = self.send_request(f"request_book {username} {book_id}")
        if (response == "False"): return []
        return list(map(int, response.split(" ")))

    def return_book(self, username, book_id):
        response = self.send_request(f"return_book {username} {book_id}")
        if (response == "False"): return []
        return list(map(int, response.split(" ")))
    
    def get_borrowed_book_list(self, borrower_username):
        response = self.send_request(f"get_borrowed_book_list {borrower_username}")
        if (response == 'False'): return []
        statistics = []
        for result in response.split(" "):
            statistics.append(result.split(":"))
        return statistics

if __name__ == "__main__":
    library = LibraryInterface("127.0.0.1", 5555)

    # Demo usage
    # Room management
    print("Testing room management")
    print("Testing add_room(): ", end="")
    print(library.add_room("A", 50, 1.0, 1.0, 1.57, True))
    print("add_room(): ", end="")
    print(library.add_room("B", 50, 12.0, 1.0, -1.57, False))

    print(library.get_room_statistics())
    print()

    # User management
    print("Tesing user management")
    print("Testing register_user(): ", end="")
    print(library.register_user('admin', 'admin'))
    print("register_user(): ", end="")
    print(library.register_user('user', 'user'))

    # Testing auth function
    print("Testing authenticate_user(): ", end="")
    print(library.authenticate_user('user', 'user'))

    print("Testing set_user_room(): ", end="")
    print(library.set_user_room('admin', 'A'))

    print("set_user_room(): ", end="")
    print(library.set_user_room('user', 'A'))

    print("Testing reset_user_room(): ", end="")
    print(library.reset_user_room('user'))
    print()

    print("Tesing book management")
    print("add_book(): ", end="")
    library.add_book("abc", [1, 1, 2])
    print("add_book(): ", end="")
    library.add_book("aab", [1, 2, 2])
    print("add_book(): ", end="")
    library.add_book("aba", [2, 1, 2])
    print("add_book(): ", end="")
    library.add_book("aaa", [3, 2, 1])
    print()

    # Testing functions
    # Check whether database contains the book
    print("Testing check_present(): ", end="")
    if (library.check_present("aaa")): print("Present");
    else: print("Not present")

    # Check whether the selected book is available to lend and return bookId
    print("Testing get_available_bookid(): ", end="")
    res = library.get_available_bookid("abc")
    if (res): print(res)
    else: print("Not available")

    # Check whether the selected book is available to lend and
    # if present then makes it unavailable and returns book location
    print("Testing request_book(): ", end="")
    res = library.request_book('a', 1)
    if (res): print(res)
    else: print("Not available")

    # Just testing to make sure that it cannot be requested again...
    print("request_book(): ", end="")
    res = library.request_book('a', 1)
    if (res): print(res)
    else: print("Not available")

    # Returning the book
    print("Testing return_book(): ", end="")
    res = library.return_book('a', 1)
    if (res): print(res)
    else: print("Book not in database or already available")

    # Now we can request it as we already returned it
    print("request_book(): ", end="")
    res = library.request_book('a', 1)
    if (res): print(res)
    else: print("Not available")