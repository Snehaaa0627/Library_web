import sqlite3

# The class that authenticates staffs
class StaffManagement:
    def __init__(self, conn, reset=False):
        self.conn = conn
        self.cursor = self.conn.cursor()

        if reset:
            query = "DROP TABLE IF EXISTS staffs"
            self.cursor.execute(query)
            self.conn.commit()

        query = """CREATE TABLE IF NOT EXISTS staffs(
                        username VARCHAR PRIMARY KEY,
                        password VARCHAR,
                        permLevel INT DEFAULT 0
                )"""
        self.cursor.execute(query)
        self.conn.commit()

        query = 'SELECT username from staffs WHERE username = ?'
        self.cursor.execute(query, ('admin',))
        res = self.cursor.fetchone()
        self.conn.commit()

        if res: return

        # Create a root user for commands to work
        query = "INSERT INTO staffs (username, password, permLevel) VALUES (?, ?, ?)"
        self.cursor.execute(query, ('admin', 'admin', 2))
        self.conn.commit()

    def register_staff(self, username, password):
        query = 'SELECT username from staffs WHERE username = ?'
        self.cursor.execute(query, (username,))
        res = self.cursor.fetchone()
        self.conn.commit()

        if res: return False

        query = 'SELECT username from users WHERE username = ?'
        self.cursor.execute(query, (username,))
        res = self.cursor.fetchone()
        self.conn.commit()

        if res: return False

        query = "INSERT INTO staffs (username, password) VALUES (?, ?)"
        self.cursor.execute(query, (username, password))
        self.conn.commit()

        return True
    
    def set_staff_perms(self, username, permission_level):
        query = 'UPDATE staffs SET permLevel=? WHERE username = ?'
        self.cursor.execute(query, (permission_level, username))
        self.conn.commit()

        return True
    
    def get_staff_perms(self, username):
        query = 'SELECT permLevel FROM staffs WHERE username = ?'
        self.cursor.execute(query, (username,))
        result = self.cursor.fetchone()
        self.conn.commit()

        if result: return result[0]
        return 0

    def authenticate_staff(self, username, password):
        query = 'SELECT username FROM staffs WHERE username = ? AND password = ?'
        self.cursor.execute(query, (username, password))
        result = self.cursor.fetchone()
        self.conn.commit()
        
        if result: return True
        return False