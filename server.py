import socket
import threading
import socketserver
from utils import get_phonebook, write_phonebook, delete_phonebook
from typing import List


PROTOCOL = "РКСОК/1.0"

METHOD = ("ОТДОВАЙ", "ЗОПИШИ", "УДОЛИ")
OK = "НОРМАЛДЫКС"
NOTFOUND = "НИНАШОЛ"
NOT_APPROVED = "НИЛЬЗЯ"
INCORRECT_REQUEST = "НИПОНЯЛ"


class RKSOKPhoneBook:
    """Phonebook working with RKSOK server."""

    def __init__(self):
        self._name, self._phone, self._method = None, None, None
        self.response = None

    def get_request(self, msg: str) -> str:
        """Processing clients request"""
        request = [x for x in msg.split("\r\n") if len(x) > 0]
        if len(request) > 1:
            self._phone = request[1::]
            msg = self.compile_response(request[0])
        else:
            msg = self.compile_response(request[0])
        return msg

    def compile_response(self, msg: str) -> str:
        """Collects response for client"""
        raw_response = self.parse_body_request(msg)
        self.response = self._raw_response(raw_response)
        return self.response

    def _raw_response(self, response: str) -> str:
        """Сheck that the request is correct"""
        if response.startswith(INCORRECT_REQUEST):
            raw_response = f"{INCORRECT_REQUEST} {PROTOCOL}\r\n\r\n".encode()
            return raw_response
        response_client = self.send_to_checking_server(response)
        return response_client

    def parse_body_request(self, req: str) -> str:
        """Parsing request and methoв"""
        verbs = req.split()
        if verbs[-1] == PROTOCOL and self.get_method(verbs[0]):
            verbs.remove(PROTOCOL)
            verbs.pop(0)
            if self.get_name(verbs):
                raw_response = f"{self._method} {self._name} {PROTOCOL}"
                return raw_response
        else:
            raw_response = f"{INCORRECT_REQUEST} {PROTOCOL}"
            return raw_response

    def get_method(self, method: str) -> str:
        """Get and checking method"""
        if method in METHOD:
            self._method = method
            return self._method

    def get_name(self, verbs: List[str]) -> str:
        """Сollects the username into a single variable"""
        name = " ".join(verbs)
        if self.checking_len_of_name(name):
            self._name = name
            return self._name

    def checking_len_of_name(self, name: str) -> bool:
        """Return True if name is correct"""
        return len(name) <= 30 and len(name) != 0

    def send_to_checking_server(self, enquiry: str) -> str:
        """Sends request to the serve checking"""
        method = "АМОЖНА? РКСОК/1.0"
        try:
            conn = socket.create_connection(("vragi-vezde.to.digital", 51624))
            request = f"{method}\r\n {enquiry}\r\n\r\n".encode()
            conn.send(request)
            official_response = conn.recv(1024).decode()
            respon = self.response_processing(official_response)
            return respon
        except:
            print("Партия занята и не может ответить на твои глупые запросы")

    def response_processing(self, official_response: str) -> str:
        """collets response after party verification"""
        if self.parse_response_check_server(official_response):
            if self.work_phonebook():
                if self._method == "ОТДОВАЙ":
                    response = f"{OK} {PROTOCOL}\r\n{self._phone}\r\n\r\n".encode()
                else:
                    response = f"{OK} {PROTOCOL}\r\n\r\n".encode()
            else:
                response = f"{NOTFOUND} {PROTOCOL}\r\n\r\n".encode()
            return response
        else:
            return f"{official_response}".encode()

    def parse_response_check_server(self, official_response: str) -> bool:
        """Party verification of the request"""
        if official_response.startswith("МОЖНА"):
            return True

    def work_phonebook(self) -> bool:
        """Working with utils phonebook"""
        if self._method == "ОТДОВАЙ":
            phone = get_phonebook(self._name)
            if phone:
                self._phone = phone
                return True
        elif self._method == "ЗОПИШИ":
            if write_phonebook(self._name, self._phone):
                return True
        elif self._method == "УДОЛИ":
            if delete_phonebook(self._name):
                return True


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
        client = RKSOKPhoneBook()
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
