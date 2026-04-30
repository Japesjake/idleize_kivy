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

categories = [('mining',), ('smelting',), ('crafting',)]
sql = "INSERT OR IGNORE INTO Category (category_name) VALUES (?)"
cursor.executemany(sql, categories)
sql_conn.commit()

items = [('copper ore',None,None,'mining',1,1), ('iron ore',None,None,'mining',500,2), ('copper ingot','copper ore',1, 'smelting',1,1), ('iron ingot', 'iron ore',1,'smelting',500,2), ('copper armor', 'copper ingot',5,'crafting',1,1), ('iron armor', 'iron ingot',5,'crafting',500,2)]
cursor.executemany("INSERT OR IGNORE INTO Item (item_name, crafts_from_item_id, crafts_from_amount, category_id, difficulty, xp_reward) VALUES (?, (SELECT item_id FROM Item WHERE item_name = ?), ?, (SELECT category_id FROM Category WHERE category_name = ?), ?, ?)", items)
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
                    already_running_this_item = False
                    for idle_thread in idle_threads:
                        if idle_thread.username == username:
                            if idle_thread.item == data:
                                already_running_this_item = True
                            print(f'There is a conflict on username: {username}')
                            idle_thread.idling = False
                            idle_threads.remove(idle_thread)
                    if not already_running_this_item:
                        print('Adding idle_thread...')
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
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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
        inventory = cursor.fetchall()

        sql = "SELECT Category.category_name, PlayerXP.xp FROM PlayerXP JOIN Category ON PlayerXP.category_id = Category.category_id JOIN Player ON PlayerXP.player_id = Player.player_id WHERE Player.name = ?"
        cursor.execute(sql, (username,))
        experience = cursor.fetchall()
        msg = {"inventory": inventory, "experience": experience}
        # print(f'data sent to client: {msg}')
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
            current_item = self.item
            sql = "SELECT Category.category_id FROM Category, Item WHERE Category.category_id = (SELECT category_id FROM Item WHERE Item.category_id = Category.category_id AND Item.item_name = ?)"
            cursor.execute(sql, (self.item,))
            category_id = cursor.fetchone()[0]
            
            sql = "SELECT EXISTS (SELECT 1 FROM PlayerXP, Player WHERE PlayerXP.player_id = (SELECT player_id FROM Player WHERE Player.name = ?) AND PlayerXP.category_id = ?)"
            cursor.execute(sql, (username, category_id))
            xp_record_exists = cursor.fetchone()[0]
            if not xp_record_exists:
                sql = "INSERT INTO PlayerXP (player_id, category_id, xp) VALUES ((SELECT player_id FROM Player WHERE Player.name = ?),?,0)"
                cursor.execute(sql, (username, category_id))
                sql_conn.commit()


            sql = "SELECT Item.difficulty, PlayerXP.xp FROM Item, PlayerXP WHERE Item.item_name = ? AND PlayerXP.player_id = (SELECT player_id FROM Player WHERE name = ?)"
            cursor.execute(sql, (self.item, self.username))
            difficulty, xp = cursor.fetchone()
            duration = difficulty / (xp + 1)
            if duration < 1: duration = 1
            print(f'Time until reward: {duration}')
            time.sleep(duration)
            # elapsed = 0
            # while elapsed < duration:
            #     if not self.idling or current_item != self.item:
            #         return
            #     time.sleep(0.1)
            #     elapsed += 0.1

            if self.idling:
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

                        cursor.execute("SELECT count FROM PlayerItem, Item WHERE PlayerItem.item_id = (SELECT Item.item_id WHERE item_name = ?) AND PlayerItem.player_id = (SELECT player_id FROM Player WHERE name = ?)", (self.item, self.username))
                        count = cursor.fetchone()
                        print(f'{self.item}: count')

                        sql = "UPDATE PlayerItem SET count = count - (SELECT crafts_from_amount FROM Item WHERE item_name = ?) FROM Item, Player WHERE PlayerItem.item_id = (SELECT crafts_from_item_id FROM Item WHERE Item.item_name = ?) AND Player.name = ?"
                        cursor.execute(sql,(self.item,self.item,self.username))
                        sql_conn.commit()

                sql = "SELECT xp_reward FROM Item WHERE item_name = ?"
                cursor.execute(sql, (self.item,))
                xp_reward = cursor.fetchone()[0]

                ### adds XP ###
                sql = "UPDATE PlayerXP SET xp = xp + ? WHERE category_id = ? AND player_id = (SELECT player_id FROM Player WHERE name = ?)"
                cursor.execute(sql, (xp_reward, category_id, username))
                sql_conn.commit()

                sql = "SELECT xp FROM PlayerXP WHERE player_id = (SELECT player_id FROM Player WHERE name = ?) AND category_id = (SELECT category_id FROM Item WHERE item_name = ?)"
                cursor.execute(sql, (username, self.item))
                print(f'added xp to category id: {category_id} Total: {xp}')
                        
                sql = "SELECT count FROM PlayerItem JOIN Player ON PlayerItem.player_id = Player.player_id JOIN Item ON PlayerItem.item_id = Item.item_id WHERE Player.name = ? AND Item.item_name = ?"
                cursor.execute(sql,(self.username, self.item))
                item_count = cursor.fetchall()
                if not item_count:
                    print('No record found. Inserting record')
                    sql = 'INSERT INTO PlayerItem (player_id, item_id) VALUES ((SELECT player_id from player WHERE name = ?), (SELECT item_id FROM item WHERE item_name = ?))'
                    cursor.execute(sql,(self.username, self.item))
                    sql_conn.commit()
        if self in idle_threads:
            idle_threads.remove(self)
        sql_conn.close()
class Connection():
    def __init__(self, conn, addr, thread):
        self.conn = conn
        self.addr = addr
        self.thread = thread
        self.username = None
        self.password = None
        self.active_idle_thread = None # Store the thread here

    def stop_current_task(self):
        if self.active_idle_thread:
            print(f"Stopping task: {self.active_idle_thread.item} for {self.username}")
            self.active_idle_thread.idling = False
            self.active_idle_thread = None
        


if __name__ == "__main__":
    server = Server()
    server.start_server()
