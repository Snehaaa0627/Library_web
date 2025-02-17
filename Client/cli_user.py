from LibraryInterface import LibraryInterface

class LibraryCli:
    def __init__(self):
        self.library = LibraryInterface("127.0.0.1", 5555)
        self.username = None

        # Adding some defaults for testing
        self.library.register_user('a', 'a')
        self.library.register_user('b', 'b')
        self.library.register_user('c', 'c')
        self.library.register_user('d', 'd')
        self.library.register_user('e', 'e')
        self.library.register_user('f', 'f')

    def login_menu(self):
        print("\n====== Library Management System ======")
        print("1. Login")
        print("2. Register")
        print("=======================================")

    def main_menu(self):
        print("\n====== Library Management System ======")
        print("1. Check book in database")
        print("2. Request a Book")
        print("3. Return a Book")
        print("4. View all borrowed books")
        print("5. Change current reading room")
        print("6. Logout")
        print("=======================================")

    def login(self):
        username = input("Enter username: ")
        password = input("Enter password: ")
        if self.library.authenticate_user(username, password):
            print("Login successful!")
            isRoomSet = False
            while (not isRoomSet):
                print(f"Room statistics: {self.library.get_room_statistics()}")
                room_name = input("Enter room name: ")
                isRoomSet = self.library.set_user_room(username, room_name)
                
            self.username = username

        else:
            print("Invalid credentials, please try again.")

    def register(self):
        username = input("Enter username: ")
        password = input("Enter password: ")
        if self.library.register_user(username, password):
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

    def set_reading_room(self):
        username = input("Enter username: ")
        room_name = input("Enter room name: ")
        if self.library.set_user_room(username, room_name):
            print("Room set successfully!")
        else:
            print("Room setting failed. Either room doesn't exist or is full.")

    def leave_reading_room(self):
        username = input("Enter username: ")
        if self.library.reset_user_room(username):
            print("Left room successfully.")
        else:
            print("Failed to leave the room or user doesn't have any room set.")

    def check_book_present(self):
        book_name = input("Enter book name: ")
        if self.library.check_present(book_name):
            print(f"Book '{book_name}' is present.")
        else:
            print(f"Book '{book_name}' is not present.")

    def request_book(self):
        book_name = input("Enter book name: ")
        book_id = int(self.library.get_available_bookid(book_name))
        if not book_id:
            print(f"Book '{book_name}' is currently unavailable.")
            return
        
        res = self.library.request_book(self.username, book_id)
        if res:
            print(f"Book {book_name} requested successfully. ID: {book_id}, Location: {res}")
        else:
            print(f"Book '{book_name}' is currently unavailable.")

    def return_book(self):
        book_id = int(input("Enter book ID: "))
        res = self.library.return_book(self.username, book_id)
        if res:
            print(f"Book {book_id} returned successfully. Location: {res}")
        else:
            print("Book return failed or not available.")

    def view_borrowed_books(self):
        print(f"Borrowed books: {self.library.get_borrowed_book_list(self.username)}")

    def change_reading_room(self):
        room_name = input("Enter new room name: ")
        self.library.set_user_room(self.username, room_name)
        print("Changed current reading room.")

    def logout(self):
        self.library.reset_user_room(self.username)
        self.username = None
        print("Logged out successfully.")

    def handle_choices_main(self, choice):
        actions = {
            '1': self.check_book_present,
            '2': self.request_book,
            '3': self.return_book,
            '4': self.view_borrowed_books,
            '5': self.change_reading_room,
            '6': self.logout
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
