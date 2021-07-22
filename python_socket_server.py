import socket


server = socket.create_server(("localhost", 5000))
server.listen(2)

#def checking_len_of_request():

while True:
    print("we are on the top level")
    conn, addr = server.accept()
    while True:
        name = conn.recv(1024)
        print(name)
        # my = name.decode().split()
        # if my[0] == "ЗОПИШИ":
        #      if len(my) == 5:
        # name = (my[1], my[2])
        # name = "".join(name)
        conn.sendall("НОРМАЛДЫКС РКСОК/1.0".encode())
        conn.close()
        break
             # elif len(my) == 3:
             #     name = my[1]
             #     print(name)
             # else:
             #    pass


        #conn.sendall(my)
server.close()
