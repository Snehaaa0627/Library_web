import sqlite3

# The class that authenticates users
class UserManagement:
    def __init__(self, conn, reset=False):
        self.conn = conn
        self.cursor = self.conn.cursor()

        if reset:
            query = "DROP TABLE IF EXISTS users"
            self.cursor.execute(query)
            self.conn.commit()

        query = """CREATE TABLE IF NOT EXISTS users(
                        username VARCHAR PRIMARY KEY,
                        password VARCHAR,
                        roomName VARCHAR
                )"""
        self.cursor.execute(query)
        self.conn.commit()

    def register_user(self, username, password):
        query = 'SELECT username from users WHERE username = ?'
        self.cursor.execute(query, (username,))
        res = self.cursor.fetchone()
        self.conn.commit()

        if res: return False

        query = "INSERT INTO users (username, password) VALUES (?, ?)"
        self.cursor.execute(query, (username, password))
        self.conn.commit()

        return True

    def authenticate_user(self, username, password):
        query = 'SELECT username FROM users WHERE username = ? AND password = ?'
        self.cursor.execute(query, (username, password))
        result = self.cursor.fetchone()
        self.conn.commit()
        
        if result: return True
        return False
    
    def get_user_room(self, username):
        query = 'SELECT roomName from users WHERE username = ? AND roomName IS NOT NULL'
        self.cursor.execute(query, (username,))
        res = self.cursor.fetchone()
        self.conn.commit()

        if not res: return False
        return res[0]

    def set_user_room(self, username, room_name):
        query = 'SELECT roomName, capacity, occupied from rooms WHERE roomName = ? AND capacity>occupied'
        self.cursor.execute(query, (room_name,))
        res = self.cursor.fetchone()
        self.conn.commit()

        if not res: return False

        query = 'SELECT username from users WHERE username = ?'
        self.cursor.execute(query, (username,))
        res = self.cursor.fetchone()
        self.conn.commit()

        if not res: return False

        # If there is already an existing room selected
        query = 'SELECT username from users WHERE username = ? AND roomName IS NULL'
        self.cursor.execute(query, (username,))
        res = bool(self.cursor.fetchone())
        self.conn.commit()

        if not res: self.reset_user_room(username)

        query = 'UPDATE users SET roomName = ? WHERE username = ?'
        self.cursor.execute(query, (room_name, username))
        self.conn.commit()

        query = 'UPDATE rooms SET occupied = occupied+1 WHERE roomName = ?'
        self.cursor.execute(query, (room_name,))
        self.conn.commit()

        return True

    def reset_user_room(self, username):
        query = 'SELECT roomName FROM users WHERE username = ? AND roomName IS NOT NULL'
        self.cursor.execute(query, (username,))
        room_name = self.cursor.fetchone()
        self.conn.commit()

        if not room_name: return False

        room_name = room_name[0]

        query = 'UPDATE users SET roomName = NULL WHERE username = ?'
        self.cursor.execute(query, (username,))
        self.conn.commit()

        query = 'UPDATE rooms SET occupied = occupied-1 WHERE roomName = ? AND occupied>0'
        self.cursor.execute(query, (room_name,))
        self.conn.commit()

        return True

if __name__ == "__main__":
    conn = sqlite3.connect('library.db')

    # Create test environment
    auth = UserManagement(conn)
    auth.register_user('admin', 'admin')
    auth.register_user('aaa', 'aaa')
    auth.register_user('aba', 'aba')
    auth.register_user('eea', 'eea')
    auth.register_user('user', 'user')

    # Testing auth function
    print(auth.authenticate_user('user', 'user'))
    print(auth.set_user_room('admin', 'A'))
    print(auth.set_user_room('user', 'A'))
    print(auth.reset_user_room('user'))