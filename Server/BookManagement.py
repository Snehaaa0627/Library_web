import sqlite3

# The class that handles book database
class BookManagement:
    def __init__(self, conn, reset=False, refresh=True):
        self.conn = conn
        self.cursor = self.conn.cursor()

        if reset:
            query = "DROP TABLE IF EXISTS books"
            self.cursor.execute(query)
            self.conn.commit()
        
        query = """CREATE TABLE IF NOT EXISTS books (
                        bookId INTEGER PRIMARY KEY AUTOINCREMENT,
                        bookName VARCHAR,
                        bookLocationRoom INTEGER,
                        bookLocationRow INTEGER,
                        bookLocationCol INTEGER,
                        availability BIT,
                        borrowerUsername VARCHAR
                )"""
        
        self.cursor.execute(query)
        self.conn.commit()

        if refresh:
            query = "UPDATE books SET availability = 1, borrowerUsername = NULL"
            self.cursor.execute(query)
            self.conn.commit()


    def add_book(self, book_name, book_location):
        query = "INSERT INTO books (bookName, bookLocationRoom, bookLocationRow, bookLocationCol, availability) VALUES (?, ?, ?, ?, 1)"
        self.cursor.execute(query, (book_name, book_location[0], book_location[1], book_location[2]))
        self.conn.commit()

    def check_present(self, book_name):
        query = 'SELECT bookId FROM books WHERE bookName = ?'
        self.cursor.execute(query, (book_name,))
        result = self.cursor.fetchone()
        self.conn.commit()
        
        if result: return True
        return False

    def get_available_bookid(self, book_name):
        query = 'SELECT bookId FROM books WHERE bookName = ? AND availability = 1'
        self.cursor.execute(query, (book_name,))
        result = self.cursor.fetchone()

        self.conn.commit()
        
        if result: return result[0]
        return 0

    def request_book(self, book_id, borrower_username):
        query = 'SELECT bookLocationRoom, bookLocationRow, bookLocationCol FROM books WHERE bookId = ? AND availability = 1'
        self.cursor.execute(query, (book_id,))
        result = self.cursor.fetchone()
        self.conn.commit()
        
        if result:
            location = list(result)
            query = 'UPDATE books SET availability = 0, borrowerUsername = ? WHERE bookId = ? AND availability = 1'
            self.cursor.execute(query, (borrower_username, book_id,))
            result = self.cursor.fetchone()
            self.conn.commit()

            return True, location

        return False, []

    def return_book(self, book_id):
        query = 'SELECT bookLocationRoom, bookLocationRow, bookLocationCol FROM books WHERE bookId = ? AND availability = 0'
        self.cursor.execute(query, (book_id,))
        result = self.cursor.fetchone()
        self.conn.commit()
        
        if result:
            location = list(result)
            query = 'UPDATE books SET availability = 1, borrowerUsername = NULL WHERE bookId = ?'
            self.cursor.execute(query, (book_id,))
            result = self.cursor.fetchone()
            self.conn.commit()
            
            return True, location

        return False, []
    
    def get_borrowed_book_list(self, borrower_username):
        query = 'SELECT bookId, bookName FROM books WHERE borrowerUsername = ?'
        self.cursor.execute(query, (borrower_username,))
        res = self.cursor.fetchall()
        self.conn.commit()
        
        if not res: return False, []

        return True, res
    
    def get_book_statistics(self):
        query = 'SELECT bookId, bookName, bookLocationRoom, bookLocationRow, bookLocationCol FROM books'
        self.cursor.execute(query)
        res = self.cursor.fetchall()
        self.conn.commit()
        
        if not res: return False, []

        return True, res

    def remove_book(self, book_id):
        query = 'SELECT bookId from books WHERE bookId = ?'
        self.cursor.execute(query, (book_id,))
        res = self.cursor.fetchone()
        self.conn.commit()

        if not res: return False

        query = "DELETE FROM books WHERE bookId = ?"
        self.cursor.execute(query, (book_id,))
        self.conn.commit()

        return True


if __name__ == "__main__":
    conn = sqlite3.connect('library.db')
    
    # Demo usage
    # Create test environment
    books = BookManagement(conn)
    books.add_book("abc", [1, 1, 2])
    books.add_book("aab", [1, 2, 2])
    books.add_book("aba", [2, 1, 2])
    books.add_book("aaa", [3, 2, 1])

    # Testing functions
    # Check whether database contains the book
    print("Testing check_present(): ", end="")
    if (books.check_present("aaa")): print("Present");
    else: print("Not present")

    # Check whether the selected book is available to lend and return bookId
    print("Testing get_available_bookid(): ", end="")
    res = books.get_available_bookid("abc")
    if (res): print(res)
    else: print("Not available")

    # Check whether the selected book is available to lend and
    # if present then makes it unavailable and returns book location
    print("Testing request_book(): ", end="")
    ret, res = books.request_book(1)
    if (ret): print(res)
    else: print("Not available")

    # Just testing to make sure that it cannot be requested again...
    print("request_book(): ", end="")
    ret, res = books.request_book(1)
    if (ret): print(res)
    else: print("Not available")

    # Returning the book
    print("Testing return_book(): ", end="")
    ret, res = books.return_book(1)
    if (ret): print(res)
    else: print("Book not in database or already available")

    # Now we can request it as we already returned it
    print("request_book(): ", end="")
    ret, res = books.request_book(1)
    if (ret): print(res)
    else: print("Not available")

    print(books.get_book_statistics())

    # Remove a book
    print("remove_book(): ", end="")
    res = books.remove_book(1)
    if (res): print("Book removed")
    else: print("Error removing book")

    print(books.get_book_statistics())