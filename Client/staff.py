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


@staff.route('/add_room', methods=['POST'])
def add_room():
    try:
        data = request.json  
        room_name = data.get("room_name")
        capacity = int(data.get("capacity"))
        
        room_type = str(data.get("room_type", "").strip())  # Convert input to string
        if room_type not in ["1", "0"]:
            return jsonify({"status": "error", "message": "Invalid input! Enter '1' for staff-only, '0' for public"}), 400
        
        is_staff_only = int(room_type)  # Convert "1" -> 1, "0" -> 0

        # Validate position
        position_raw = data.get("position", "0 0 0")
        position_parts = position_raw.split()
        if len(position_parts) != 3:
            return jsonify({"status": "error", "message": "Position must contain exactly three numbers"}), 400
        
        try:
            position = tuple(map(float, position_parts))  # Convert to float
        except ValueError:
            return jsonify({"status": "error", "message": "Position must contain valid numbers"}), 400

        # Add room
        if library.add_room(room_name, capacity, position[0], position[1], position[2], is_staff_only):
            return jsonify({"status": "success", "message": "Room added successfully!"})
        else:
            return jsonify({"status": "error", "message": "Failed to add room"}), 500

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# REMOVE ROOM
@staff.route('/remove_room/<room_name>', methods=['POST'])
def remove_room(room_name):
    if library.remove_room(room_name):  # Now removing by name
        return jsonify({"message": "Room removed successfully!", "status": "success"})
    else:
        return jsonify({"message": "Error removing room.", "status": "error"})
    
@staff.route("/staff_permissions")
def staff_permissions():
    return render_template("staff_permissions.html")

@staff.route("/set_staff_perms", methods=["POST"])
def set_staff_perms():
    try:
        data = request.get_json()
        staff_name = data["staff_name"]
        permission_level = int(data["permission_level"])

        # Call the actual function to set permissions
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
