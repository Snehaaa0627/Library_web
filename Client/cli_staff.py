from LibraryStaffInterface import LibraryStaffInterface

class LibraryCli:
    def __init__(self):
        self.library = LibraryStaffInterface("127.0.0.1", 5555)
        self.username = None

        # Adding some defaults for testing
        self.library.register_user('a', 'a')
        self.library.register_user('b', 'b')
        self.library.register_user('c', 'c')
        self.library.register_user('d', 'd')
        self.library.register_user('e', 'e')
        self.library.register_user('f', 'f')

        self.library.add_book("abc", [1, 1, 1])
        self.library.add_book("aba", [2, 3, 1])
        self.library.add_book("aaa", [3, 1, 2])
        self.library.add_book("abb", [2, 2, 1])

        self.library.add_room('A', 4, [-14.0, 0.0, 1.57], hide_room=0)
        self.library.add_room('B', 4, [22.0, 0.0, 1.57], hide_room=0)
        self.library.add_room('1', 4, [-14.0, 1.0, -1.57], hide_room=1)
        self.library.add_room('2', 4, [6.5, 1.0, -1.57], hide_room=1)
        self.library.add_room('3', 4, [22.0, 1.0, -1.57], hide_room=1)

    def login_menu(self):
        print("\n====== Library Management System ======")
        print("1. Login")
        print("2. Register")
        print("=======================================")

    def main_menu(self):
        print("\n====== Library Management System ======")
        print("1. Add book")
        print("2. List all books")
        print("3. Remove book")
        print("4. Add room")
        print("5. Print room statistics")
        print("6. Remove room")
        print("7. Set user permission level")
        print("8. Logout")
        print("=======================================")

    def login(self):
        username = input("Enter username: ")
        password = input("Enter password: ")
        if self.library.authenticate_staff(username, password):
            print("Login successful!")
            self.username = username

        else:
            print("Invalid credentials, please try again.")

    def register(self):
        username = input("Enter username: ")
        password = input("Enter password: ")
        if self.library.register_staff(username, password):
            print("Registration successful!")
        else:
            print("Username already exists. Please try again.")

    def handle_choices_login(self, choice):
        actions = {
            '1': self.login,
            '2': self.register
        }

        action = actions.get(choice)
        if action: action()
        else: print("Invalid choice")

    def add_room(self):
        room_name = input("Enter room name: ")
        capacity = int(input("Enter room capacity: "))
        position = list(map(float, input("Enter coordinates (x y phi): ").split()))
        room_type = int(input("Is staff only room (Y/n): ").lower() == "y")

        if self.library.add_room(room_name, capacity, position, self.username, room_type):
            print("Room added successfully!")
        else:
            print("Error adding room")

    def get_all_rooms(self):
        print(f"Room statistics: {self.library.get_all_rooms()}")

    def remove_room(self):
        room_name = input("Enter room name: ")

        if self.library.remove_room(room_name, self.username):
            print("Room removed successfully!")
        else:
            print("Error removing room.")

    def add_book(self):
        book_name = input("Enter book name: ")
        position = list(map(float, input("Enter coordinates (room row col): ").split()))

        if self.library.add_book(book_name, position, self.username):
            print("Book added successfully!")
        else:
            print("Error adding book.")

    def get_book_statistics(self):
        print(f"Books statistics: {self.library.get_book_statistics(self.username)}")

    def remove_book(self):
        book_id = input("Enter book ID: ")

        if self.library.remove_book(book_id, self.username):
            print("Book removed successfully!")
        else:
            print("Error removing book.")

    def set_staff_perms(self):
        user_name = input("Enter staff name: ")
        permission_level = int(input("Enter permission level: "))
        if self.library.set_staff_perms(user_name, permission_level, self.username):
            print(f"Staff permission modified.")
        else:
            print(f"Error modifying permission.")

    def logout(self):
        self.username = None
        print("Logged out successfully.")

    def handle_choices_main(self, choice):
        actions = {
            '1': self.add_book,
            '2': self.get_book_statistics,
            '3': self.remove_book,
            '4': self.add_room,
            '5': self.get_all_rooms,
            '6': self.remove_room,
            '7': self.set_staff_perms,
            '8': self.logout
        }

        action = actions.get(choice)
        if action: action()
        else: print("Invalid choice")

    def run(self):
        while True:
            if not self.username:
                self.login_menu()
                choice = input("Enter your choice: ").strip()
                self.handle_choices_login(choice)
                
            else:
                self.main_menu()
                choice = input("Enter your choice: ").strip()
                self.handle_choices_main(choice)

if __name__ == "__main__":
    app = LibraryCli()
    app.run()
