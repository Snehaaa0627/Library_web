from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from LibraryStaffInterface import LibraryStaffInterface

# Initialize Flask
staff = Flask(__name__)
staff.secret_key = 'your_secret_key'  

library = LibraryStaffInterface("127.0.0.1", 5555)

# create test environment
library = LibraryStaffInterface("127.0.0.1", 5555)
library.register_user('admin', 'admin')


# Define Routes
@staff.route('/')
def home():
    return redirect(url_for('staff_login'))

#Login Route
@staff.route('/staff_login', methods=['GET', 'POST'])
def staff_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if library.authenticate_staff(username, password):
            session['username'] = username
            return redirect(url_for('staff_dashboard'))
        else:
            return render_template('staff_login.html', error="Invalid username or password")
    return render_template('staff_login.html',error=None)

# SIGNUP ROUTE 
@staff.route('/staff_signup', methods=['GET', 'POST'])
def staff_signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        library.register_staff(username,password)
        return render_template('staff_signup.html', success="Sign-up successful! You can now log in.")
    return render_template('staff_signup.html', success=None)

#staff dashboard
@staff.route('/staff_dashboard')
def staff_dashboard():
    username = session.get('username')
    if not username:
        return redirect(url_for('staff_login'))
    return render_template('staff_dashboard.html')

#Book Management
@staff.route('/manage_books')
def manage_books():
    raw_books = library.get_book_statistics()  
    books = [
        {"id": book[0], "name": book[1], "position": f"Room {book[2]}, Row {book[3]}, Col {book[4]}"}
        for book in raw_books
    ]
    return render_template('manage_books.html', books=books)


# Add a new book
@staff.route('/add_book', methods=['POST'])
def add_book():
    data = request.get_json()
    book_name = data.get("book_name")
    position = data.get("position")

    if library.add_book(book_name, position):
        return jsonify({"message": "Book added successfully!", "status": "success"})
    else:
        return jsonify({"message": "Error adding book.", "status": "error"})

# Remove a book
@staff.route('/remove_book/<book_id>', methods=['POST'])
def remove_book(book_id):
    if library.remove_book(book_id):
        return jsonify({"message": "Book removed successfully!", "status": "success"})
    else:
        return jsonify({"message": "Error removing book.", "status": "error"})
    
# Room Management
@staff.route('/manage_rooms')
def manage_rooms():
    raw_rooms = library.get_all_rooms()
    rooms = [
    {"name": room[0], "capacity": room[1], "seats_occupied": room[2]}
    for room in raw_rooms
]

    return render_template('room_management.html', rooms=rooms)

# ADD ROOM
@staff.route('/add_room', methods=['POST'])
def add_room():
    try:
        data = request.get_json()
        print("Received data:", data)  # Debugging

        room_name = str(data.get("room_name", "")).strip()
        capacity = data.get("room_capacity", 0)
        position = data.get("coordinates", "0 0 0")
        room_type = int(data.get("staff_only", "n").lower() == "y")

        try:
            capacity = int(capacity)
        except ValueError:
            return jsonify({"message": "Invalid room capacity", "status": "error"})

        position = list(map(float, position.split()))
        room_type = int(room_type == "y")

        print(f"DEBUG: Calling library.add_room({room_name}, {capacity}, {position}, 'admin', {room_type})")
        success = library.add_room(room_name, capacity, position, "admin", room_type)

        print(f"DEBUG: library.add_room() returned {success}")

        if success:
            return jsonify({"message": "Room added successfully!", "status": "success"})
        else:
            print("Library function returned False")
            return jsonify({"message": "Error adding room.", "status": "error"})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"message": f"Server error: {e}", "status": "error"})



# REMOVE ROOM
@staff.route('/remove_room/<room_name>', methods=['POST'])
def remove_room(room_name):
    if library.remove_room(room_name):  
        return jsonify({"message": "Room removed successfully!", "status": "success"})
    else:
        return jsonify({"message": "Error removing room.", "status": "error"})
    
@staff.route("/staff_permissions")
def staff_permissions():
    return render_template("staff_permissions.html")

#Staff Permission
@staff.route("/set_staff_perms", methods=["POST"])
def set_staff_perms():
    try:
        data = request.get_json()
        staff_name = data["staff_name"]
        permission_level = int(data["permission_level"])

        success = library.set_staff_perms(staff_name, permission_level)

        if success:
            return jsonify({"status": "success", "message": f"Permission updated for {staff_name}."})
        else:
            return jsonify({"status": "error", "message": "Failed to modify permissions."})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


#LOGOUT ROUTE
@staff.route('/staff_logout')
def staff_logout():
    return redirect(url_for('staff_login'))


if __name__ == '__main__':
    print("Starting Flask server...")
    staff.run(debug=True)

