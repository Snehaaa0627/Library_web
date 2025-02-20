from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from LibraryInterface import LibraryInterface
from LibraryStaffInterface import LibraryStaffInterface

# Initialize Flask
app = Flask(__name__)
app.secret_key = 'your_secret_key'  

library = LibraryInterface("127.0.0.1", 5555)
library1 = LibraryStaffInterface("127.0.0.1", 5555)


# create test environment
library = LibraryInterface("127.0.0.1", 5555)
library1.register_user('admin', 'admin')
library.register_user('user', 'user')

#Entry Page
@app.route('/')
def home():
    return redirect(url_for('entry'))

@app.route('/entry')
def entry():
    return render_template('entry.html')


#Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if library.authenticate_user(username, password):
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="Invalid username or password")
    return render_template('login.html',error=None)

# SIGNUP ROUTE 
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        library.register_user(username,password)
        return render_template('signup.html', success="Sign-up successful! You can now log in.")
    return render_template('signup.html', success=None)


# DASHBOARD ROUTE
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))
    rooms = library.get_room_statistics()
    print("Room statistics:", rooms)  
    rooms_data = [
        {
            'name': room[0],
            'seats_available': int(room[1]) - int(room[2]),  
            'occupied': int(room[2])
        } 
        for room in rooms
    ]
    if request.method == 'POST':
        room_name = request.form.get('room_name')
        print(f"Attempting to allocate room: {room_name} for user: {username}")

        allocation_success = library.set_user_room(username, room_name)
        print(f"Received command: add_room : {allocation_success}")  

        if allocation_success:
            success_message = f'You have been successfully allocated to Room {room_name}.'

            rooms = library.get_room_statistics()
            rooms_data = [
                {
                    'name': room[0],
                    'seats_available': int(room[1]) - int(room[2]), 
                    'occupied': int(room[2])
                } 
                for room in rooms
            ]
            return render_template('dashboard.html', rooms=rooms_data, success=success_message)
        else:
            error_message = f'Room {room_name} is full or allocation failed. Please try again.'
            return render_template('dashboard.html', rooms=rooms_data, error=error_message)
    return render_template('dashboard.html', rooms=rooms_data)


#BOOK SECTION ROUTE
@app.route('/books')
def books():
    return render_template('books.html')


#CHECK BOOK ROUTE
@app.route('/check_book', methods=['GET'])
def check_book():
    book_name = request.args.get('name', '').strip()
    if not book_name:
        return jsonify({"error": "No book name provided"}), 400

    is_present = library.check_present(book_name)
    return jsonify({"present": is_present})

#GET BOOK ID ROUTE
@app.route('/get_book_id', methods=['GET'])
def get_book_id():
    book_name = request.args.get('name')
    book_id = library.get_available_bookid(book_name) 
    if book_id:
        return jsonify({"id": book_id})
    else:
        return jsonify({"id": None}), 404
    

# REQUEST BOOK ROUTE    
@app.route('/request_book', methods=['POST'])
def request_book():
    data = request.json
    book_name = data.get("bookName")
    book_id = data.get("bookId")
    username = session.get("username")  

    if not book_id:
        return jsonify({"success": False}), 400

    res = library.request_book(username, book_id)
    if res:
        return jsonify({"success": True, "location": res})
    else:
        return jsonify({"success": False}), 404



# RETURN BOOK ROUTE
@app.route('/return')
def return_book():
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))
    borrowed_books = library.get_borrowed_book_list(username)  
    print(f"Borrowed books for {username}: {borrowed_books}")  
    if not borrowed_books or borrowed_books is None:
        borrowed_books = [] 
    return render_template('return.html', borrowed_books=borrowed_books)


# RETURN_BOOK_ACTION ROUTE
@app.route('/return_book_action', methods=['POST'])
def return_book_action():
    username = session.get('username')
    print(f"Request received to return book. User: {username}") 
    if not username:
        return jsonify({"success": False, "error": "User not logged in"}), 401
    data = request.get_json()
    book_id = data.get("bookId")
    print(f"Book ID received: {book_id}")  
    if not book_id or not str(book_id).isdigit():  
        return jsonify({"success": False, "error": "Invalid book ID"}), 400
    return_success = library.return_book(username, int(book_id))  
    print(f"Return success: {return_success}")  
    if return_success:
        return jsonify({"success": True, "location": "Library return section"}), 200
    else:
        return jsonify({"success": False, "error": "Failed to return book"}), 500

# DEVELOPER ROUTE
@app.route('/developer')
def developer():
    return render_template('developer.html')

#LOGOUT ROUTE
@app.route('/logout')
def logout():
    username = session.get('username')
    if username:
        library.reset_user_room(username)
        print(f"Room allocation reset for {username}")
        session.pop('username', None)
    return redirect(url_for('login'))



# STAFF LOGIN ROUTE
@app.route('/staff_login', methods=['GET', 'POST'])
def staff_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if library1.authenticate_staff(username, password):
            session['username'] = username
            return redirect(url_for('staff_dashboard'))
        else:
            return render_template('staff_login.html', error="Invalid username or password")
    return render_template('staff_login.html',error=None)

# STAFF SIGNUP ROUTE 
@app.route('/staff_signup', methods=['GET', 'POST'])
def staff_signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        library1.register_staff(username,password)
        return render_template('staff_signup.html', success="Sign-up successful! You can now log in.")
    return render_template('staff_signup.html', success=None)

#staff dashboard
@app.route('/staff_dashboard')
def staff_dashboard():
    username = session.get('username')
    if not username:
        return redirect(url_for('staff_login'))
    return render_template('staff_dashboard.html')

# STAFF Book Management
@app.route('/manage_books')
def manage_books():
    raw_books = library1.get_book_statistics()  
    books = [
        {"id": book[0], "name": book[1], "position": f"Room {book[2]}, Row {book[3]}, Col {book[4]}"}
        for book in raw_books
    ]
    return render_template('manage_books.html', books=books)


# STAFF Add a new book
@app.route('/add_book', methods=['POST'])
def add_book():
    data = request.get_json()
    book_name = data.get("book_name")
    position = data.get("position")

    if library1.add_book(book_name, position):
        return jsonify({"message": "Book added successfully!", "status": "success"})
    else:
        return jsonify({"message": "Error adding book.", "status": "error"})

# STAFF Remove a book
@app.route('/remove_book/<book_id>', methods=['POST'])
def remove_book(book_id):
    if library1.remove_book(book_id):
        return jsonify({"message": "Book removed successfully!", "status": "success"})
    else:
        return jsonify({"message": "Error removing book.", "status": "error"})
    
# STAFF Room Management
@app.route('/manage_rooms')
def manage_rooms():
    raw_rooms = library1.get_all_rooms()
    rooms = [
    {"name": room[0], "capacity": room[1], "seats_occupied": room[2]}
    for room in raw_rooms
]

    return render_template('room_management.html', rooms=rooms)

# STAFF ADD ROOM
@app.route('/add_room', methods=['POST'])
def add_room():
    try:
        data = request.get_json()
        print("Received data:", data)  

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
        success = library1.add_room(room_name, capacity, position, "admin", room_type)

        print(f"DEBUG: library.add_room() returned {success}")

        if success:
            return jsonify({"message": "Room added successfully!", "status": "success"})
        else:
            print("Library function returned False")
            return jsonify({"message": "Error adding room.", "status": "error"})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"message": f"Server error: {e}", "status": "error"})


# STAFF REMOVE ROOM
@app.route('/remove_room/<room_name>', methods=['POST'])
def remove_room(room_name):
    if library1.remove_room(room_name):  
        return jsonify({"message": "Room removed successfully!", "status": "success"})
    else:
        return jsonify({"message": "Error removing room.", "status": "error"})
    
@app.route("/staff_permissions")
def staff_permissions():
    return render_template("staff_permissions.html")

#Staff Permission
@app.route("/set_staff_perms", methods=["POST"])
def set_staff_perms():
    try:
        data = request.get_json()
        staff_name = data["staff_name"]
        permission_level = int(data["permission_level"])

        success = library1.set_staff_perms(staff_name, permission_level)

        if success:
            return jsonify({"status": "success", "message": f"Permission updated for {staff_name}."})
        else:
            return jsonify({"status": "error", "message": "Failed to modify permissions."})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


#LOGOUT ROUTE
@app.route('/staff_logout')
def staff_logout():
    return redirect(url_for('staff_login'))


if __name__ == '__main__':
    print("Starting Flask server...")
    app.run(debug=True)
