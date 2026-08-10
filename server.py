import socket, sqlite3, threading, json, bcrypt
from server_data import items, categories, server_version
host = '0.0.0.0'
port = 1235

connections = {}

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
            data_type = data.get('type')

            if data_type == 'login':
                username = data.get('username')
                password = data.get('password')
                server_password = cursor.execute("SELECT password FROM Player WHERE username = ?",(username,)).fetchone()
                if server_password is not None:
                    server_password = server_password[0]
                    if bcrypt.checkpw(password.encode('utf-8'), server_password):
                        send_json(conn, {'type': 'login', 'message': 'good'})
                    else:
                        send_json(conn, {'type': 'login', 'message': 'bad'})
                else:
                    send_json(conn, {'type': 'login', 'message': 'bad'})
            elif data_type == 'new':
                username = data.get('username')
                password = data.get('password')
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                try:
                    cursor.execute("INSERT INTO Player (username, password) VALUES (?,?)",(username, hashed_password))
                except sqlite3.IntegrityError:
                    print('Username already exists.')
                sql_conn.commit()
            elif data_type == 'version':
                client_version = data.get('version')
                if not client_version == server_version:
                    category_data = self.get_category_data()
                    send_json(conn, {'type':'update version','version': server_version, 'categories': category_data})


        conn.close()
    def start_server(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((host, port))
        server.listen()
        print(f"[LISTENING] Server is listening on localhost: {port}")

        while True:
            conn, addr = server.accept()
            thread = threading.Thread(target=self.handle_client, args=(conn, addr))
            thread.start()
    def get_category_data(self):
        sql_conn = sqlite3.connect('server.db')
        sql_conn.execute("PRAGMA journal_mode=WAL;")
        cursor = sql_conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        sql = "SELECT Category.name, json_group_array(Item.item_id ORDER BY Item.sort_order ASC) FROM Item JOIN Category ON Item.category_id = Category.category_id GROUP BY Category.name ORDER BY Category.sort_order ASC;"
        cursor.execute(sql)
        category_data = cursor.fetchall()
        category_data = self.convert_items_from_json(category_data)
        return category_data
    def convert_items_from_json(self, rows):
        dictionary = {}
        for category, items_json in rows:
            items_list = json.loads(items_json)
            dictionary[category] = items_list
        return dictionary
class Connection():
    def __init__(self, conn, addr, thread):
        self.conn = conn
        self.addr = addr
        self.thread = thread


server = Server()
server.start_server()