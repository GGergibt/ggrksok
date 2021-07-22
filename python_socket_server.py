import socket

s = socket.create_server(("localhost", 5000))
s.listen(1)

while True:
    print("Главный цикл")
    conn, addr = s.accept()
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
s.close()
