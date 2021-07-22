import socket

server = socket.create_server(("localhost", 5000))
server.listen(1)
def checking_len_of_name(request:str) -> bool:
     return len(request) >= 30

while True:
    print("Главный цикл")
    conn, addr = server.accept()
    while True:
        data = conn.recv(1024)
        if not data:
            break
        res = "НОРМАЛДЫКС РКСОК/3.0".encode()
        print(data.decode())
        # conn.send(res)
        conn.sendall(res)
        conn.close()
        break
server.close()
