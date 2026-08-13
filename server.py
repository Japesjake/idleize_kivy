import socket, sqlite3, threading, json, bcrypt, time, hashlib, secrets
from server_data import items, categories, server_version
host = '0.0.0.0'
port = 1235

SESSION_TTL_SECONDS = 60 * 60 * 24 * 7

sql_conn = sqlite3.connect('server.db')
sql_conn.execute("PRAGMA journal_mode=WAL;")
cursor = sql_conn.cursor()
cursor.execute("PRAGMA foreign_keys = ON;")

with open('create_db.sql', 'r') as f:
    create_db = f.read()
cursor.executescript(create_db)

sql = "INSERT OR IGNORE INTO Category (name, sort_order) VALUES (?, ?)"
cursor.executemany(sql, categories)

sql = "INSERT OR IGNORE INTO Item VALUES (?,?,(SELECT category_id FROM Category WHERE name = ?),?,?,?)"
cursor.executemany(sql, items)
sql_conn.commit()
sql_conn.close()

def hash_token(token: str) -> bytes:
    return hashlib.sha256(token.encode("ascii")).digest()

def create_session(cursor, player_id: int):
    token = secrets.token_urlsafe(32)
    now = int(time.time())
    expires_at = now + SESSION_TTL_SECONDS

    cursor.execute(
        """
        INSERT INTO Session (token_hash, player_id, created_at, expires_at)
        VALUES (?, ?, ?, ?)
        """,
        (hash_token(token), player_id, now, expires_at),
    )
    return token, expires_at

def get_authenticated_player(cursor, data):
    token = data.get("session")

    if not isinstance(token, str):
        return None

    row = cursor.execute(
        """
        SELECT player_id
        FROM Session
        WHERE token_hash = ? AND expires_at > ?
        """,
        (hash_token(token), int(time.time())),
    ).fetchone()

    return row[0] if row else None

def send_json(sock, data):
    payload = json.dumps(data) + '\n'
    sock.sendall(payload.encode('utf-8'))
    print(f'sent:')
    print(data)
def recv_json(sock):
    data = b""
    while True:
        chunk = sock.recv(1)
        if not chunk:
            return None
        if chunk == b'\n':
            break
        data += chunk
    if not data:
        return None
    try:
        return(json.loads(data.decode('utf-8')))
    except json.JSONDecodeError:
        return None

class Server():
    connections = []
    def start_server(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((host, port))
        server.listen()
        print(f"[LISTENING] Server is listening on localhost: {port}")
        while True:
            conn, addr = server.accept()
            connection = Connection(conn, addr)
            self.connections.append(connection)

class Connection():
    def __init__(self, conn, addr):
        self.conn = conn
        self.addr = addr
        self.thread = threading.Thread(target=self.handle_client,args=(conn, addr))
        self.thread.start()
    def handle_client(self, conn, addr):
        sql_conn = sqlite3.connect('server.db')
        sql_conn.execute("PRAGMA journal_mode=WAL;")
        cursor = sql_conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        while True:
            data = recv_json(conn)
            if data is None:
                break
            print('received: ')
            print(data)
            try:
                self.handle_message(cursor, sql_conn, conn, addr, data)
            except Exception as e:
                sql_conn.rollback()
                print(f"[ERROR] failed to handle message {data}: {e}")
                try:
                    send_json(conn, {"type": "error", "message": "server error"})
                except OSError:
                    break

        conn.close()

    def handle_message(self, cursor, sql_conn, conn, addr, data):
        data_type = data.get('type')
        if data_type == "login":
            username = data.get("username")
            password = data.get("password")

            row = cursor.execute(
                "SELECT player_id, password FROM Player WHERE username = ?",
                (username,),
            ).fetchone()

            if row and bcrypt.checkpw(password.encode("utf-8"), row[1]):
                token, expires_at = create_session(cursor, row[0])
                sql_conn.commit()

                inventory_rows = cursor.execute(
                    "SELECT item_id, quantity FROM Inventory WHERE player_id = ?",
                    (row[0],)
                ).fetchall()

                send_json(conn, {
                    "type": "login",
                    "message": "good",
                    "session": token,
                    "expires_at": expires_at,
                    "inventory": dict(inventory_rows)
                })
            else:
                send_json(conn, {"type": "login", "message": "bad"})
        elif data_type == 'new':
            username = data.get('username')
            password = data.get('password')
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            try:
                cursor.execute("INSERT INTO Player (username, password) VALUES (?,?)",(username, hashed_password))
            except sqlite3.IntegrityError as e:
                print(e)
            sql_conn.commit()
        elif data_type == 'version check':
            client_version = data.get('version')
            if not client_version == server_version:
                category_data = self.get_category_data()
                send_json(conn, {'type':'version','message':'version mismatch','version': server_version, 'categories': category_data})
            else:
                print('versions match. No update needed.')
                send_json(conn, {'type': 'version', 'message': 'good'})


        elif data_type == "toggle idling":
            player_id = get_authenticated_player(cursor, data)

            if player_id is None:
                send_json(conn, {
                    "type": "error",
                    "message": "authentication required",
                })
                return

            item_id = data.get("item")

            matching_thread = None
            for idle_thread in IdleThread.idle_threads:
                if idle_thread.player_id == player_id:
                    matching_thread = idle_thread
                    break

            if matching_thread:
                matching_thread.idling = False
                IdleThread.idle_threads.remove(matching_thread)
                print("Existing idle thread stopped.")
            else:
                new_thread = IdleThread(conn, addr, player_id, item_id)
                IdleThread.idle_threads.append(new_thread)
                print("New idle thread started.")

    def get_category_data(self):
        sql_conn = sqlite3.connect('server.db')
        sql_conn.execute("PRAGMA journal_mode=WAL;")
        cursor = sql_conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        sql = "SELECT Category.name, json_group_array(Item.item_id ORDER BY Item.sort_order ASC) FROM Item JOIN Category ON Item.category_id = Category.category_id GROUP BY Category.name ORDER BY Category.sort_order ASC;"
        cursor.execute(sql)
        category_data = cursor.fetchall()
        category_data = self.convert_items_from_json(category_data)
        sql_conn.close()
        return category_data
    def convert_items_from_json(self, rows):
        dictionary = {}
        for category, items_json in rows:
            items_list = json.loads(items_json)
            dictionary[category] = items_list
        return dictionary

class IdleThread():
    idle_threads = []
    def __init__(self, conn, addr, player_id, item_id):
        self.conn = conn
        self.addr = addr
        self.player_id = player_id
        self.item = item_id
        self.idling = True
        self.thread = threading.Thread(target=self.idle_process)
        self.thread.start()
    def idle_process(self):
        self.idling = True
        while self.idling:
            time.sleep(1)
            print('idling...')
            self.increment()
    def increment(self, amount_to_add=1):
        sql_conn = sqlite3.connect('server.db')
        sql_conn.execute("PRAGMA journal_mode=WAL;")
        cursor = sql_conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        cursor.execute(
            """
            INSERT INTO Inventory (player_id, item_id, quantity)
            VALUES (?, ?, ?)
            ON CONFLICT(player_id, item_id)
            DO UPDATE SET quantity = quantity + excluded.quantity
            """,
            (self.player_id, self.item, amount_to_add),
        )
        sql_conn.commit()
        new_quantity = cursor.execute(
            "SELECT quantity FROM Inventory WHERE player_id = ? AND item_id = ?",
            (self.player_id, self.item),
        ).fetchone()[0]
        try:
            send_json(self.conn, {'type':'inventory update', 'item': self.item, 'quantity':new_quantity})
        except OSError:
            pass
server = Server()
server.start_server()