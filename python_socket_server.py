import socket


server = socket.create_server(("localhost", 5000))
server.listen(1)
conn, addr = server.accept()
while True:
    name = conn.recv(1024)
    my = name.decode().split()
    if my[0] == "ЗОПИШИ":
    #response = my[0]
         if len(my) == 5: 
             name = (my[1], my[2])
             name = "".join(name)
             conn.sendall("НОРМАЛДЫКС РКСОК/1.0".encode())
             conn.sendall(my)
             print(my)
         elif len(my) == 3:
             name = my[1]
             print(name)
         else:
             print("not understand")



    if not my:
        break
    #conn.sendall(my)
server.close()
