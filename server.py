import socket
import threading, time, sqlite3, json, bcrypt

host = '0.0.0.0'
port = 1235

idle_threads = []
connections = []

# Database initialization setup
sql_conn = sqlite3.connect('data.db')
sql_conn.execute("PRAGMA journal_mode=WAL;")
cursor = sql_conn.cursor()

with open('create_db.sql', 'r') as f:
    create_db = f.read()
cursor.executescript(create_db)

categories = [('mining',), ('smelting',), ('crafting',), ('gathering',)]
sql = "INSERT OR IGNORE INTO Category (category_name) VALUES (?)"
cursor.executemany(sql, categories)

items = [('copper ore','mining',1,1), 
         ('iron ore','mining',500,2), 
         ('copper ingot', 'smelting',1,1), 
         ('iron ingot','smelting',500,2), 
         ('copper armor','crafting',1,1), 
         ('iron armor','crafting',500,2), 
         ('wood','gathering',1,1),
         ('wood plank','gathering',1,2),
         ('stick', 'gathering', 1, 1), 
         ('copper arrow', 'crafting', 1, 1),
         ('copper sword', 'crafting', 1, 1)
         ]
cursor.executemany("INSERT OR IGNORE INTO Item (item_name, category_id, difficulty, xp_reward) VALUES (?, (SELECT category_id FROM Category WHERE category_name = ?), ?, ?)", items)
sql_conn.commit()
cursor.execute("SELECT item_name FROM Item")

items = cursor.fetchall()
items = [item[0] for item in items]

recipes = [
    ('iron ingot', 'iron ore', 1),
    ('copper ingot', 'copper ore', 1),
    ('iron armor', 'iron ingot', 5),
    ('copper armor', 'copper ingot', 5),
    ('stick', 'wood', 1),
    ('wood plank', 'wood', 1),
    ('copper arrow', 'copper ingot', 1),
    ('copper arrow', 'stick', 1),
    ('copper sword', 'wood plank', 1),
    ('copper sword', 'copper ingot', 1)
]

sql = """INSERT OR IGNORE INTO Recipe (product_item_id, ingredient_item_id, amount) 
         VALUES ((SELECT item_id FROM Item WHERE item_name = ?), 
                 (SELECT item_id FROM Item WHERE item_name = ?), ?)"""
cursor.executemany(sql, recipes)

# sql = """INSERT OR IGNORE INTO EquippedItems (player_id, slot_name, item_id)"""
# cursor.execute(sql, (1, 'body', ))
sql_conn.commit()
sql_conn.close()

# Helper utilities for safe line-buffered serialization
def send_json(sock, data):
    payload = json.dumps(data) + '\n'
    sock.sendall(payload.encode('utf-8'))

def recv_json(sock):
    data = b""
    while True:
        chunk = sock.recv(1)
        if not chunk:
            # Connection dropped or closed mid-transmission
            return None 
        if chunk == b'\n':
            break
        data += chunk
        
    # Guard against parsing empty streams
    if not data:
        return None
        
    try:
        return json.loads(data.decode('utf-8'))
    except json.JSONDecodeError:
        return None

class Server():
    def __init__(self):
        pass
        
    def handle_client(self, conn, addr):
        """Function to handle individual client communication."""
        print(f"[NEW CONNECTION] {addr} connected.")
        cursor = None
        sql_connection = None
        try:
            with sqlite3.connect('data.db') as sql_connection:
                sql_connection.execute("PRAGMA journal_mode=WAL;")
                cursor = sql_connection.cursor()
                
                while True:
                    data = recv_json(conn)
                    if data is None:
                        break
                    print(f"[{addr}] says: {data}")

                    # Login Handshake Block
                    if isinstance(data, list) and len(data) == 2:
                        username = data[0]
                        password = data[1]
                        print(f'received username: {username} password: [redacted] from client')

                        for connection in connections:
                            if connection.conn == conn and connection.addr == addr:
                                connection.username = username
                                connection.password = password
                                cursor.execute("SELECT name, password FROM Player WHERE name = ?",(username,))
                                credentials = cursor.fetchall()
                                
                                if credentials and credentials[0][0] == username and bcrypt.checkpw(password.encode('utf-8'), credentials[0][1]):
                                    send_json(conn, ['good'])
                                if not credentials:
                                    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                                    print(f'no player found. Creating player with credentials')
                                    send_json(conn, ['new'])
                                    cursor.execute("INSERT INTO Player (name, password) VALUES (?, ?)",(username, hashed))
                                    sql_connection.commit()
                        
                        # Wait for acknowledgment handshake step from client
                        response = recv_json(conn)
                        print(f'response received: {response}')
                        
                        if response == ['canceled']:
                            print(f'User {username} canceled profile creation. Cleaning up.')
                            cursor.execute("DELETE FROM Player WHERE name = ?", (username,))
                            sql_connection.commit()
                            continue
                        
                        ## checks for relevant running threads then send info to client ##
                        conflict = False
                        matched_thread = None
                        if idle_threads:
                            for idle_thread in idle_threads:
                                if idle_thread.username == username:
                                    conflict = True
                                    matched_thread = idle_thread
                        if conflict and matched_thread:
                            send_json(conn, (matched_thread.item, matched_thread.count))
                            print(f'Threading info sent to client: ({matched_thread.item},{matched_thread.count})')
                        else:
                            print(f'no conflict sent to client: false')
                            send_json(conn, 'false')
                            
                        # Complete sync setup stage cleanly
                        self.sync(username, conn)
                        
                    elif isinstance(data, list) and data[0] == 'sync':
                        self.sync(username, conn)
                        
                    elif data in items or 'fight' in data:
                        already_running_this_item = False
                        for idle_thread in idle_threads:
                            if idle_thread.username == username:
                                if idle_thread.item == data:
                                    already_running_this_item = True
                                print(f'There is a conflict on username: {username}')
                                idle_thread.idling = False
                                if idle_thread in idle_threads:
                                    idle_threads.remove(idle_thread)
                        if not already_running_this_item:
                            print('Adding idle_thread...')
                            idle_thread = Idle_thread(username, data, conn, addr)
                            idle_threads.append(idle_thread)
                            idle_thread.thread.start()
            
        except (ConnectionResetError, ConnectionError):
            pass
        except sqlite3.Error:
            print('error connecting to database')
        finally:
            conn.close()
            print(f"[DISCONNECTED] {addr} closed.")

    def start_server(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((host, port))
        server.listen()
        print(f"[LISTENING] Server is listening on localhost: {port}")

        while True:
            conn, addr = server.accept()
            thread = threading.Thread(target=self.handle_client, args=(conn, addr))
            connection = Connection(conn, addr, thread)
            connections.append(connection)
            connection.thread.start()

    def sync(self, username, conn):
        with sqlite3.connect('data.db') as sql_conn:
            sql_conn.execute("PRAGMA journal_mode=WAL;")
            cursor = sql_conn.cursor()

            sql = "SELECT Item.item_name, count FROM PlayerItem JOIN Player ON PlayerItem.player_id = Player.player_id JOIN Item ON PlayerItem.item_id = Item.item_id WHERE Player.name = ?;"
            cursor.execute(sql,(username,))
            inventory = cursor.fetchall()

            sql = "SELECT Category.category_name, PlayerXP.xp FROM PlayerXP JOIN Category ON PlayerXP.category_id = Category.category_id JOIN Player ON PlayerXP.player_id = Player.player_id WHERE Player.name = ?"
            cursor.execute(sql, (username,))
            experience = cursor.fetchall()
            
            msg = {"inventory": inventory, "experience": experience}
            print(f'Inventory and Experience data sent to client')
            send_json(conn, msg)

class Idle_thread():
    def __init__(self, username, item, conn, addr):
        self.idling = True
        self.username = username
        self.item = item
        self.count = 15
        self.conn = conn
        self.addr = addr
        self.thread = threading.Thread(target=self.idle_loop, args=(self.conn, self.addr, self.username))
        
    def idle_loop(self, conn, addr, username):
        with sqlite3.connect('data.db') as sql_conn:
            sql_conn.execute("PRAGMA journal_mode=WAL;")
            cursor = sql_conn.cursor()

            sql = "SELECT player_id FROM Player WHERE name = ?"
            cursor.execute(sql, (username, ))
            player_id = cursor.fetchone()[0]
            sql = """INSERT OR IGNORE INTO PlayerStats (player_id, hp, strength, dexterity, defense, max_hp) VALUES (?, ?, ?, ?, ?, ?)"""            
            cursor.execute(sql, (player_id,10,1,1,1,10))
            while self.idling:
                if 'fight' in self.item:
                    pass
                    # time.sleep(1)
                    # enemy = self.item.removeprefix('fight ')
                    # sql = 'SELECT hp, strength, dexterity, defense, max_hp FROM PlayerStats WHERE player_id = ?'
                    # cursor.execute(sql,(player_id,))
                    # s = cursor.fetchall()
                else:
                    sql = "SELECT category_id FROM Item WHERE item_name = ?"
                    cursor.execute(sql, (self.item,))
                    category_id = cursor.fetchone()[0]
                    
                    sql = "INSERT OR IGNORE INTO PlayerXP (player_id, category_id, xp) VALUES (?,?,0)"
                    cursor.execute(sql, (player_id, category_id))
                    sql_conn.commit()

                    sql = "SELECT Item.difficulty, PlayerXP.xp FROM Item, PlayerXP WHERE Item.item_name = ? AND PlayerXP.player_id = (SELECT player_id FROM Player WHERE name = ?)"            
                    cursor.execute(sql, (self.item, self.username))
                    difficulty, xp = cursor.fetchone()
                    duration = difficulty / (xp + 1)
                    if duration < 1: duration = 1
                    
                    time.sleep(duration)

                    if self.idling:
                        cursor.execute("""
                            SELECT r.ingredient_item_id, r.amount, i.item_name 
                            FROM Recipe r 
                            JOIN Item i ON r.ingredient_item_id = i.item_id
                            WHERE r.product_item_id = (SELECT item_id FROM Item WHERE item_name = ?)
                        """, (self.item,))
                        ingredients = cursor.fetchall()

                        can_craft = True
                        for ing_id, req_amount, ing_name in ingredients:
                            cursor.execute("SELECT count FROM PlayerItem WHERE player_id = ? AND item_id = ?", (player_id, ing_id))
                            result = cursor.fetchone()
                            current_count = result[0] if result else 0
                            
                            if current_count < req_amount:
                                can_craft = False
                                break
                        if can_craft:
                            for ing_id, req_amount, ing_name in ingredients:
                                cursor.execute("UPDATE PlayerItem SET count = count - ? WHERE player_id = ? AND item_id = ?", 
                                            (req_amount, player_id, ing_id))
                                sql_conn.commit()

                            sql = "SELECT item_id, xp_reward, category_id FROM Item WHERE item_name = ?"
                            cursor.execute(sql, (self.item, ))
                            item_id, xp_reward, category_id = cursor.fetchone()
                            
                            sql = "INSERT OR IGNORE INTO PlayerItem (player_id, item_id, count) VALUES (?, ?, 0)"
                            cursor.execute(sql, (player_id, item_id))
                            sql_conn.commit()

                            sql = "UPDATE PlayerXP SET xp = xp + ? WHERE category_id = ? AND player_id = ?"
                            cursor.execute(sql, (xp_reward, category_id, player_id))
                            sql_conn.commit()

                            sql = "UPDATE PlayerItem SET count = count + 1 WHERE player_id = ? AND item_id = ?"
                            cursor.execute(sql, (player_id, item_id))
                            sql_conn.commit()

                    sql = "SELECT count FROM PlayerItem WHERE player_id = ? AND item_id = (SELECT item_id FROM Item WHERE item_name = ?)"
                    cursor.execute(sql, (player_id, self.item))
                    count = cursor.fetchone()

                    cursor.execute("""
                    SELECT px.xp 
                    FROM PlayerXP px
                    JOIN Item i ON px.category_id = i.category_id
                    WHERE px.player_id = ? AND i.item_name = ?
                    """, (player_id, self.item))

                    actual_xp = cursor.fetchone()[0]
                    print(f"SERVER UPDATE: {self.username} now has {actual_xp} XP in {self.item}'s category.")
                    print(f'UPDATE: Item: {self.item} Count: {count}')
                
        if self in idle_threads:
            idle_threads.remove(self)

class Connection():
    def __init__(self, conn, addr, thread):
        self.conn = conn
        self.addr = addr
        self.thread = thread
        self.username = None
        self.password = None
        self.active_idle_thread = None

    def stop_current_task(self):
        if self.active_idle_thread:
            print(f"Stopping task: {self.active_idle_thread.item} for {self.username}")
            self.active_idle_thread.idling = False
            self.active_idle_thread = None

if __name__ == "__main__":
    Server().start_server()