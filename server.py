import socket, sqlite3, threading, json, bcrypt

host = '0.0.0.0'
port = 1235

connections = {}

sql_conn = sqlite3.connect('server.db')
sql_conn.execute("PRAGMA journal_mode=WAL;")
cursor = sql_conn.cursor()

with open('create_db.sql', 'r') as f:
    create_db = f.read()
cursor.executescript(create_db)

def send_json(sock, data):
    payload = json.dumps(data) + '\n'
    sock.sendall(payload.encode('utf-8'))

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
        while True:
            data = recv_json(conn)
            if data is None:
                break
            print(f"[{addr}] says: {data}")
            type = data.get('type')

            if type == 'login':
                username = data.get('username')
                password = data.get('password')
                server_password = cursor.execute("SELECT password FROM Player WHERE username = ?",(username,)).fetchone()
                if server_password is not None:
                    server_password = server_password[0]
                    if bcrypt.checkpw(password.encode('utf-8'), server_password):
                        print('correct password')
                        send_json(conn, {'type': 'login', 'message': 'good'})
                    else:
                        print('incorrect password')
                        send_json(conn, {'type': 'login', 'message': 'bad'})
                else:
                    print(f'username not found.')
                    send_json(conn, {'type': 'login', 'message': 'bad'})
            elif type == 'new':
                username = data.get('username')
                password = data.get('password')
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                try:
                    cursor.execute("INSERT INTO Player (username, password) VALUES (?,?)",(username, hashed_password))
                except sqlite3.IntegrityError:
                    print('Username already exists.')
                sql_conn.commit()

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

class Connection():
    def __init__(self, conn, addr, thread):
        self.conn = conn
        self.addr = addr
        self.thread = thread


server = Server()
server.start_server()