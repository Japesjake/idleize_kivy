import socket
import threading, time, sqlite3, json

host = '0.0.0.0'
port = 1235

idle_threads = []
connections = []

sql_conn = sqlite3.connect('data.db')
cursor = sql_conn.cursor()

with open('create_db.sql', 'r') as f:
    create_db = f.read()
cursor.executescript(create_db)

items = [('copper ore',None,None), ('iron ore',None,None), ('copper ingot','copper ore',1), ('iron ingot', 'iron ore',1), ('copper armor', 'copper ingot',5), ('iron armor', 'iron ingot',5)]
cursor.executemany("INSERT OR IGNORE INTO Item (item_name, crafts_from_item_id, crafts_from_amount) VALUES (?, (SELECT item_id FROM Item WHERE item_name = ?), ?)", items)
sql_conn.commit()
cursor.execute("SELECT item_name FROM Item")
items = cursor.fetchall()
items = [item[0] for item in items]

class Server():
    def __init__(self):
        pass
    def handle_client(self, conn, addr):
        """Function to handle individual client communication."""
        print(f"[NEW CONNECTION] {addr} connected.")
        try:
            with sqlite3.connect('data.db') as sql_connection:
                cursor = sql_connection.cursor()
        except sqlite3.Error: print('error connecting to database')
        try:
            while True:
                data = conn.recv(1024).decode('utf-8')
                if data:
                    data = json.loads(data)
                if not data:
                    break
                print(f"[{addr}] says: {data}")

                if len(data) == 2:
                    username = data[0]
                    password = data[1]
                    print(f'received username: {username} password: [redacted] from client')

                    for connection in connections:
                        if connection.conn == conn and connection.addr == addr:
                            connection.username = username
                            connection.password = password
                            cursor.execute("SELECT name, password FROM Player WHERE name = ?",(username,))
                            credentials = cursor.fetchall()
                            if credentials and credentials[0][0] == username and credentials[0][1] == password:
                                conn.sendall(json.dumps(['good']).encode('utf-8'))
                            if not credentials:
                                print(f'no player found. Creating player with credentials')
                                conn.sendall(json.dumps(['new']).encode('utf-8'))
                                cursor.execute("INSERT INTO Player (name, password) VALUES (?, ?)",(username, password))
                                sql_connection.commit()
                    ## checks for relevant running threads then send info to client ##
                    conflict = False
                    if idle_threads:
                        for idle_thread in idle_threads:
                            if idle_thread.username == username:
                                conflict = True
                    if conflict:
                        conn.sendall(json.dumps((idle_thread.item,idle_thread.count)).encode('utf-8'))
                        print(f'Threading info sent to client: ({idle_thread.item},{idle_thread.count})')
                    else:
                        print(f'no conflict sent to client: false')
                        conn.sendall(json.dumps('false').encode('utf-8'))
                    response = json.loads(conn.recv(1024).decode())
                    print(f'response from client: {response}')
                    self.sync(username, conn)
                if data[0] == 'sync':
                    self.sync(username, conn)
                if data in items:
                    conflict = False
                    for connection in connections:
                        for idle_thread in idle_threads:
                            if idle_thread.username == username and idle_thread.idling:
                                print(f'There is a conflict on username: {connection.username}')
                                conflict = True
                                idle_thread.idling = False
                    if not conflict:
                        print('No conflict. Adding idle_thread...')
                        idle_thread = Idle_thread(username, data, conn, addr)
                        idle_threads.append(idle_thread)
                        idle_thread.thread.start()
            
        except ConnectionResetError:
            pass
        finally:
            conn.close()
            print(f"[DISCONNECTED] {addr} closed.")
    def start_server(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((host, port))
        server.listen()
        print(f"[LISTENING] Server is listening on localhost: {port}")

        sql_conn = sqlite3.connect('data.db')
        cursor = sql_conn.cursor()

        while True:
            # Wait for a new connection (blocking call)
            conn, addr = server.accept()
            ## Starts a new connection thread ##
            thread = threading.Thread(target=self.handle_client, args=(conn, addr))
            connection = Connection(conn, addr, thread)
            connections.append(connection)
            connection.thread.start()
    def sync(self, username, conn):
        sql_conn = sqlite3.connect('data.db')
        cursor = sql_conn.cursor()
        sql = "SELECT Item.item_name, count FROM PlayerItem JOIN Player ON PlayerItem.player_id = Player.player_id JOIN Item ON PlayerItem.item_id = Item.item_id WHERE Player.name = ?;"
        cursor.execute(sql,(username,))
        msg = cursor.fetchall()
        print(f'data sent to client: {msg}')
        conn.sendall(json.dumps(msg).encode('utf-8'))
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
        sql_conn = sqlite3.connect('data.db')
        cursor = sql_conn.cursor()
        while self.idling:
            time.sleep(1)
            sql = "SELECT 1 FROM Item WHERE item_name = ? AND crafts_from_item_id IS NOT NULL;"
            cursor.execute(sql,(self.item,))
            has_child = cursor.fetchone()


            sql = "SELECT count FROM PlayerItem, Item, Player WHERE PlayerItem.item_id = (SELECT crafts_from_item_id FROM Item WHERE item_name = ?) AND PlayerItem.player_id = (SELECT player_id FROM Player WHERE Player.name = ?)"
            cursor.execute(sql, (self.item, self.username))
            child_count = cursor.fetchall()
            print(f'child_count: {child_count}')

            sql = "SELECT crafts_from_amount FROM Item WHERE item_name = ?"
            cursor.execute(sql, (self.item,))
            amount = cursor.fetchall()[0][0]
            if not amount:
                sql = "UPDATE PlayerItem SET count = count + 1 FROM Item, Player WHERE PlayerItem.item_id = Item.item_id AND PlayerItem.player_id = Player.player_id AND Item.item_name = ? AND Player.name = ?;"
                cursor.execute(sql,(self.item,self.username))
                sql_conn.commit()
            elif amount and not child_count:
                pass
            else:
                child_count = child_count[0][0]
                if child_count - amount >= 0:
                    print(f'child count when above 0: {child_count}')
                    sql = "UPDATE PlayerItem SET count = count + 1 FROM Item, Player WHERE PlayerItem.item_id = Item.item_id AND PlayerItem.player_id = Player.player_id AND Item.item_name = ? AND Player.name = ?;"
                    cursor.execute(sql,(self.item,self.username))
                    sql_conn.commit()

                    sql = "UPDATE PlayerItem SET count = count - (SELECT crafts_from_amount FROM Item WHERE item_name = ?) FROM Item, Player WHERE PlayerItem.item_id = (SELECT crafts_from_item_id FROM Item WHERE Item.item_name = ?) AND Player.name = ?"
                    cursor.execute(sql,(self.item,self.item,self.username))
                    sql_conn.commit()


            sql = "SELECT count FROM PlayerItem JOIN Player ON PlayerItem.player_id = Player.player_id JOIN Item ON PlayerItem.item_id = Item.item_id WHERE Player.name = ? AND Item.item_name = ?"
            cursor.execute(sql,(self.username, self.item))
            item_count = cursor.fetchall()
            if not item_count:
                print('No record found. Inserting record')
                sql = 'INSERT INTO PlayerItem (player_id, item_id) VALUES ((SELECT player_id from player WHERE name = ?), (SELECT item_id FROM item WHERE item_name = ?))'
                cursor.execute(sql,(self.username, self.item))
                sql_conn.commit()
            else:
                # print(f'record found with count {item_count}')
                self.count = item_count[0][0]
                print(f'{self.item}, {self.count}')
        idle_threads.remove(self)
        sql_conn.close()
class Connection():
    def __init__(self, conn, addr, thread):
        self.conn = conn
        self.addr = addr
        self.thread = thread
        


if __name__ == "__main__":
    server = Server()
    server.start_server()
