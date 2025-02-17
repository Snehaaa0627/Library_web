from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from LibraryInterface import LibraryInterface

# Initialize Flask
app = Flask(__name__)
app.secret_key = 'your_secret_key'  

library = LibraryInterface("127.0.0.1", 5555)

# create test environment
library = LibraryInterface("127.0.0.1", 5555)
library.register_user('admin', 'admin')
library.register_user('user', 'user')

# Define Routes
@app.route('/')
def home():
    return redirect(url_for('login'))


# LOGIN ROUTE
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

            # Re-fetch updated room statistics
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

if __name__ == '__main__':
    print("Starting Flask server...")
    app.run(debug=True)
