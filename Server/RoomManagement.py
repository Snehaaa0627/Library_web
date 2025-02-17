import sqlite3

# The class that handles rooms
class RoomManagement:
    def __init__(self, conn, reset=False, refresh=True):
        self.conn = conn
        self.cursor = self.conn.cursor()

        if reset:
            query = "DROP TABLE IF EXISTS rooms"
            self.cursor.execute(query)
            self.conn.commit()
        
        query = """CREATE TABLE IF NOT EXISTS rooms(
                        roomName VARCHAR PRIMARY KEY,
                        hideRoom BIT,
                        capacity INTEGER,
                        occupied INTEGER DEFAULT 0,
                        posX DOUBLE,
                        posY DOUBLE,
                        phi DOUBLE
                )"""
        self.cursor.execute(query)
        self.conn.commit()

        if refresh:
            query = "UPDATE rooms SET occupied=0"
            self.cursor.execute(query)
            self.conn.commit()
    
    def add_room(self, room_name, capacity, pos_x, pos_y, phi, hide_room=0):
        query = 'SELECT roomName from rooms WHERE roomName = ?'
        self.cursor.execute(query, (room_name,))
        res = self.cursor.fetchone()
        self.conn.commit()

        if res: return False

        query = "INSERT INTO rooms (roomName, hideRoom, capacity, posX, posY, phi) VALUES (?, ?, ?, ?, ?, ?)"
        self.cursor.execute(query, (room_name, hide_room, capacity, pos_x, pos_y, phi))
        self.conn.commit()

        return True
    
    def remove_room(self, room_name):
        query = 'SELECT roomName from rooms WHERE roomName = ?'
        self.cursor.execute(query, (room_name,))
        res = self.cursor.fetchone()
        self.conn.commit()

        if not res: return False

        query = "DELETE FROM rooms WHERE roomName = ?"
        self.cursor.execute(query, (room_name,))
        self.conn.commit()

        return True
    
    def get_room_position(self, room_name):
        query = 'SELECT posX, posY, phi from rooms WHERE roomName = ?'
        self.cursor.execute(query, (room_name,))
        res = self.cursor.fetchone()
        self.conn.commit()

        if not res: return False, []

        return True, list(map(float, res))
    
    def get_room_statistics(self, show_all_rooms=False):
        if show_all_rooms:
            query = 'SELECT roomName, capacity, occupied from rooms'
        else:
            query = 'SELECT roomName, capacity, occupied from rooms WHERE hideRoom = 0'

        self.cursor.execute(query)
        res = self.cursor.fetchall()
        self.conn.commit()
        
        if not res: return False, []

        return True, res

if __name__ == "__main__":
    conn = sqlite3.connect('library.db')

    # Create test environment
    rooms = RoomManagement(conn)
    rooms.add_room('A', 4, 0.3, 1.0, 1.57)
    rooms.add_room('B', 4, 10.2, 1.1, -1.57)

    rooms.add_room('1', 4, 1.2, 5.1, -1.57, True)
    rooms.add_room('2', 4, 10.2, 5.1, -1.57, True)

    ret, position = rooms.get_room_position('A')
    if (ret): print(position)
    else: print("Couldn't find the specified room")
    print(rooms.get_room_statistics())