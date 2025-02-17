import socket
import sqlite3
import threading
from RoomManagement import RoomManagement
from UserManagement import UserManagement
from BookManagement import BookManagement
from StaffManagement import StaffManagement

conn = sqlite3.connect('library.db', check_same_thread=False)

users = UserManagement(conn, False)
staffs = StaffManagement(conn, False)
rooms = RoomManagement(conn, False, True)
books = BookManagement(conn, False, True)

def handle_client(client_socket):
    while True:
        # Receive a command from the client (max 1024 bytes)
        command = client_socket.recv(1024).decode('utf-8').strip()

        if not command:
            break
        
        # Split command to determine the action
        command, *args = command.split(" ")

        # From RoomManagement
        if command == "add_room":
            # Example: add_room issuer_username room_name capacity pos_x pos_y phi hide_room (e.g., "add_room admin A 50 1.0 2.1 0 0")
            issuer_username = args[0]
            # Authorize user before issuing command
            if (staffs.get_staff_perms(issuer_username) < 2):
                response = "False"

            else:
                room_name = args[1]
                capacity = int(args[2])
                pos_x = float(args[3])
                pos_y = float(args[4])
                phi = float(args[5])
                hide_room = int(args[6])
                response = str(rooms.add_room(room_name, capacity, pos_x, pos_y, phi, hide_room))

        # From StaffManagement
        elif command == "remove_room":
            # Example: remove_room issuer_username room_name (e.g., "remove_room staff A")
            issuer_username = args[0]
            # Authorize user before issuing command
            if (staffs.get_staff_perms(issuer_username) < 2):
                response = "False"
            
            else:
                room_name = args[1]
                response = str(rooms.remove_room(room_name))

        elif command == "get_room_statistics":
            ret, results = rooms.get_room_statistics()

            if ret:
                response = ""
                for result in results:
                    response += f"{result[0]}:{result[1]}:{result[2]} "

            else:
                response = "False"

        elif command == "get_all_rooms":
            issuer_username = args[0]
            # Authorize user before issuing command
            if (staffs.get_staff_perms(issuer_username) < 2):
                response = "False"

            else:
                ret, results = rooms.get_room_statistics(True)

                if ret:
                    response = ""
                    for result in results:
                        response += f"{result[0]}:{result[1]}:{result[2]} "

                else:
                    response = "False"

        # From StaffManagement
        elif command == "register_staff":
            # Example: register_staff username password (e.g., "register_staff staff staff")
            username = args[0]
            password = args[1]
            response = str(staffs.register_staff(username, password))

        elif command == "authenticate_staff":
            # Example: authenticate_staff username password (e.g., "authenticate_staff staff staff")
            username = args[0]
            password = args[1]
            response = str(staffs.authenticate_staff(username, password))

        elif command == "set_staff_perms":
            # Example: set_staff_perms issuer_username target_username permission_level (e.g., "set_staff_perms admin staff 1")
            issuer_username = args[0]
            # Authorize user before issuing command
            if (staffs.get_staff_perms(issuer_username) < 2):
                response = "False"

            else:
                username = args[1]
                permission_level = int(args[2])
                response = str(staffs.set_staff_perms(username, permission_level))
                
        # From LoginManagement
        elif command == "register_user":
            # Example: register_user username password (e.g., "register_user user user")
            username = args[0]
            password = args[1]
            response = str(users.register_user(username, password))

        elif command == "authenticate_user":
            # Example: authenticate_user username password (e.g., "authenticate_user user user")
            username = args[0]
            password = args[1]
            response = str(users.authenticate_user(username, password))

        elif command == "set_user_room":
            # Example: set_user_room username room_name (e.g., "set_user_room user A")
            username = args[0]
            room_name = args[1]
            response = str(users.set_user_room(username, room_name))

        elif command == "reset_user_room":
            # Example: reset_user_room username (e.g., "reset_user_room user")
            username = args[0]
            response = str(users.reset_user_room(username))

        # From BookManagement
        elif command == "add_book":
            # Example: add_book issuer_username book_name location (e.g., "add_book admin abc 1 1 1")
            issuer_username = args[0]
            # Authorize user before issuing command
            if (staffs.get_staff_perms(issuer_username) < 2):
                response = "False"

            else:
                book_name = args[1]
                location = tuple(map(float, args[2:5]))  # Convert to a tuple of integers
                books.add_book(book_name, location)
                response = "True"

        elif command == "check_present":
            # Example: check_present book_name (e.g., "check_present abc")
            book_name = args[0]
            response = str(books.check_present(book_name))

        elif command == "get_available_bookid":
            # Example: check_availability book_name (e.g., "check_availability abc")
            book_name = args[0]
            result = books.get_available_bookid(book_name)
            response = str(result)

        elif command == "request_book":
            # Example: request_book borrower_username book_id (e.g., "request_book user 1")
            borrower_username = args[0]
            book_id = int(args[1])
            success, location = books.request_book(book_id, borrower_username)
            if success:
                response = f"{location[0]} {location[1]} {location[2]}"

            else: response = "False"

        elif command == "return_book":
            # Example: return_book username book_id (e.g., "return_book user 1")
            username = args[0]
            book_id = int(args[1])
            success, location = books.return_book(book_id)
            if success:
                response = f"{location[0]} {location[1]} {location[2]}"

            else: response = "False"

        elif command == "get_borrowed_book_list":
            borrower_username = args[0]
            # Authorize user before issuing command

            ret, results = books.get_borrowed_book_list(borrower_username)

            if ret:
                response = ""
                for result in results:
                    response += f"{result[0]}:{result[1]} "

            else:
                response = "False"

        elif command == "get_book_statistics":
            issuer_username = args[0]
            # Authorize user before issuing command
            if (staffs.get_staff_perms(issuer_username) < 2):
                response = "False"

            else:
                ret, results = books.get_book_statistics()

                if ret:
                    response = ""
                    for result in results:
                        response += f"{result[0]}:{result[1]}:{result[2]}:{result[3]}:{result[4]} "

                else:
                    response = "False"

        elif command == "remove_book":
            # Example: remove_book issuer_username book_id (e.g., "remove_book staff 1")
            issuer_username = args[0]
            # Authorize user before issuing command
            if (staffs.get_staff_perms(issuer_username) < 2):
                response = "False"

            else:
                book_id = int(args[1])
                result = books.remove_book(book_id)
                response = str(result)

        else:
            response = "Unknown command"

        print(f"Received command: {command} : {response}")

        # Send the response back to the client
        client_socket.send(response.encode('utf-8'))

    client_socket.close()


def start_server(host, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    print(f"Server listening on {host}:{port}")

    while True:
        # Accept new client connection
        client_socket, addr = server.accept()
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()

def main():
    # Start the server on localhost and port 5555
    try:
        server = None
        start_server("127.0.0.1", 5555)

    except KeyboardInterrupt:
        print("\nStopping server")
        if server:
            server.close()
            conn.close()

    except Exception as e:
        print(f"Error: {e}")
        if server:
            server.close()
            conn.close()

if __name__ == "__main__":
    main()