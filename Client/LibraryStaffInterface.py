from LibraryInterface import LibraryInterface

class LibraryStaffInterface(LibraryInterface):
    def __init__(self, hostname, port): super().__init__(hostname, port)

    def register_staff(self, username, password):
        return self.send_request(f"register_staff {username} {password}") == "True"
    
    def authenticate_staff(self, username, password):
        return self.send_request(f"authenticate_staff {username} {password}") == "True"

    def add_room(self, room_name, capacity, position, issuer_username='admin', hide_room=0):
        return self.send_request(f"add_room {issuer_username} {room_name} {capacity} {position[0]} {position[1]} {position[2]} {hide_room}") == "True"
    
    def get_all_rooms(self, issuer_username='admin'):
        response = self.send_request(f"get_all_rooms {issuer_username}")
        statistics = []
        for result in response.split(" "):
            statistics.append(result.split(":"))
        return statistics

    def remove_room(self, room_name, issuer_username='admin'):
        return self.send_request(f"remove_room {issuer_username} {room_name}") == "True"

    def add_book(self, book_name, location, issuer_username='admin'):
        return self.send_request(f"add_book {issuer_username} {book_name} {location[0]} {location[1]} {location[2]}") == "True"
    
    def get_book_statistics(self, issuer_username='admin'):
        response = self.send_request(f"get_book_statistics {issuer_username}")
        statistics = []
        for result in response.split(" "):
            statistics.append(result.split(":"))
        return statistics
    
    def remove_book(self, book_id, issuer_username='admin'):
        return self.send_request(f"remove_book {issuer_username} {book_id}") == "True"
    
    def set_staff_perms(self, username, permission_level, issuer_username='admin'):
        return self.send_request(f"set_staff_perms {issuer_username} {username} {permission_level}") == "True"

if __name__ == "__main__" :
    library = LibraryStaffInterface("127.0.0.1", 5555)

    # Demo usage
    # Room management
    print("Testing room management")
    print("Testing add_room(): ", end="")
    print(library.add_room("A", 50, 1.0, 1.0, 1.57, hide_room=1))
    print("add_room(): ", end="")
    print(library.add_room("B", 50, 12.0, 1.0, -1.57, hide_room=0))

    print(library.get_room_statistics())
    print()

    # User management
    print("Tesing user management")
    print("Testing register_user(): ", end="")
    print(library.register_user('user', 'user'))

    print("Tesing staff management")
    print("Testing register_staff(): ", end="")
    print(library.register_staff('staff', 'staff'))

    # Testing auth function
    print("Testing authenticate_user(): ", end="")
    print(library.authenticate_user('user', 'user'))

    print("Testing authenticate_staff(): ", end="")
    print(library.authenticate_user('staff', 'staff'))

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
