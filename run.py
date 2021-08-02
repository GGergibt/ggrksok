import socket
import threading
import socketserver
import server


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    def recvall(self) -> str:
        """Reading data from socket"""
        BUFF_SIZE = 2048
        data = ""
        while True:
            part = self.request.recv(BUFF_SIZE).decode()
            data += part
            end = "\r\n\r\n"
            if part.endswith(end):
                break
        return data

    def handle(self):
        """Function getting request from user,
        sends to the RKSOK class and returns the response to the user
        """
        data = self.recvall()
        cur_thread = threading.current_thread()
        client = server.RKSOKPhoneBook()
        official_response = client.get_request(data)
        self.request.sendall(official_response)


def run_server():
    """Start the server RKSOK"""
    HOST, PORT = "", 50007
    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    with server:
        ip, port = server.server_address
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        print("Server loop running in thread:", server_thread.name)

        server.serve_forever()


if __name__ == "__main__":
    run_server()
