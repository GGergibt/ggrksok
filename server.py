#!/home/www/code/ggrksok/venv/bin/python
import socket
import sys
import threading
import socketserver
from utils import get_phonebook, write_phonebook, delete_phonebook
from loguru import logger


logger.add("debug.log", format="{time} {level} {message}", level="DEBUG")


PROTOCOL = "РКСОК/1.0"

METOD = ("ОТДОВАЙ", "ЗОПИШИ", "УДОЛИ")
OK = "НОРМАЛДЫКС"
NOTFOUND = "НИНАШОЛ"
NOT_APPROVED = "НИЛЬЗЯ"
INCORRECT_REQUEST = "НИПОНЯЛ"


class RKSOKPhoneBook:
    """Phonebook working with RKSOK server."""

    def __init__(self):
        self._name, self._phone, self._method = None, None, None
        self.response = None


    def raw_request(self, data):
        msg = self.get_request(data)
        logger.debug(f"Запрос: {data}\nОТВЕТ: {msg.decode()}")
        return msg

    def get_request(self, msg):
        """Функция для обработки запроса от клиента"""
        request = [x for x in msg.split("\r\n") if len(x) > 0]
        msg = self.compile_response(request)
        return msg

    def compile_response(self, res):
        """Функция собирает ответ для клиента"""
        if len(res) > 1:
            body_response = self.parse_body_request(res[0])
            self._phone = res[1::]
            raw_response = f"{body_response}\r\n{self._phone}"
            self.response = self._raw_response(raw_response)
        else:
            try:
                raw_response = self.parse_body_request(res[0])
                self.response = self._raw_response(raw_response)
            except IndexError as e:
               pass
        return self.response

    def _raw_response(self, response: str) -> str:
        if response.startswith(INCORRECT_REQUEST):
            raw_response = f"{INCORRECT_REQUEST} {PROTOCOL}\r\n\r\n".encode()
            return raw_response
        response_client = self.send_to_checking_server(response)
        return response_client

    def parse_body_request(self, req: str) -> str:
        """Функция для получения метода и имени пользователя"""
        verbs = req.split()
        if verbs[-1] == PROTOCOL and self.get_method(verbs[0]):
            verbs.remove(PROTOCOL)
            verbs.pop(0)
            if self.get_name(verbs[0]):
                raw_response = f"{self._method} {self._name} {PROTOCOL}"
                return raw_response
        else:
            raw_response = f"{INCORRECT_REQUEST} {PROTOCOL}"
            return raw_response

    def get_method(self, method: str) -> str:
        """Функция проверяет корректность метода РКСОК"""
        if method in METOD:
            self._method = method
            return self._method

    def get_name(self, verbs) -> str:
        """Функция проверяет имя пользователя"""
        name = "".join(verbs)
        if self.checking_len_of_name(name):
            self._name = name
            return self._name

    def checking_len_of_name(self, name: str) -> bool:
        """Функция проверки длины имени пользователя"""
        return len(name) <= 30 and len(name) != 0

    def send_to_checking_server(self, enquiry: str) -> str:
        """Функция для запроса на сервер проверки"""
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
        """Функция для проверки МОЖНО или НИЛЬЗЯ"""
        if official_response.startswith("МОЖНА"):
            return True

    def work_phonebook(self) -> bool:
        """Функция для работы с телефонной книгой"""
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


class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    def recvall(self):
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
        data = self.recvall()
        cur_thread = threading.current_thread()
        client = RKSOKPhoneBook()
        response = client.raw_request(data)
        self.request.sendall(response)

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


if __name__ == "__main__":
    HOST, PORT = "", 50007
    try:
        server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
        with server:
            ip, port = server.server_address
            server_thread = threading.Thread(target=server.serve_forever)
            server_thread.daemon = True
            server_thread.start()
            print("Server loop running in thread:", server_thread.name)

            server.serve_forever()
    except KeyboardInterrupt:
        print("Shutdown Server")
