import socket
import sys
from pathlib import Path
from utils import get_phonebook, write_phonebook, delete_phonebook


PROTOCOL = "РКСОК/1.0"

METOD = ("ОТДОВАЙ", "ЗОПИШИ", "УДОЛИ")
OK = "НОРМАЛДЫКС"
NOTFOUND = "НИНАШОЛ"
NOT_APPROVED = "НИЛЬЗЯ"
INCORRECT_REQUEST = "НИПОНЯЛ"


def recvall(conn):
    BUFF_SIZE = 1024
    data = b""
    while True:
        part = conn.recv(BUFF_SIZE)
        print(sys.getsizeof(part))
        data += part

        if len(part) < BUFF_SIZE:
            break
    return data


class RKSOKPhoneBook:
    """Phonebook working with RKSOK server."""

    def __init__(self):
        self._name, self._phone, self._method = None, None, None
        self.response = None

    def raw_request(self, data):
        msg = self.get_request(data.decode())
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
            raw_response = self.parse_body_request(res[0])
            self.response = self._raw_response(raw_response)
        return self.response

    def _raw_response(self, response: str) -> str:
        if response.startswith("НИПОНЯЛ"):
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

    def send_to_checking_server(self, res: str) -> str:
        """Функция для запроса на сервер проверки"""
        method = "АМОЖНА? РКСОК/1.0"
        try:
            conn = socket.create_connection(("vragi-vezde.to.digital", 51624))
            request = f"{method}\r\n {res}\r\n\r\n".encode()
            conn.send(request)
            res_vragi = conn.recv(1024).decode()
            respon = self.response_processing(res_vragi)
            return respon
        except:
            print("Партия занята и не может ответить на твои глупые запросы")

    def response_processing(self, res_vragi: str) -> str:
        if self.parse_response_check_server(res_vragi):
            if self.work_phonebook():
                if self._method == "ОТДОВАЙ":
                    response = f"{OK} {PROTOCOL}\r\n{self._phone}\r\n\r\n".encode()
                else:
                    response = f"{OK} {PROTOCOL}\r\n\r\n".encode()
            else:
                response = f"{NOTFOUND} {PROTOCOL}\r\n\r\n".encode()
            return response
        else:
            return f"{res_vragi}".encode()

    def parse_response_check_server(self, res_vragi: str) -> bool:
        """Функция для проверки МОЖНО или НИЛЬЗЯ"""
        if res_vragi.startswith("МОЖНА"):
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


def run_server():
    """Функция для запуска сервера РКСОК"""
    try:
        server = socket.create_server(("", 50007))
        server.listen(1)
        while True:
            conn, addr = server.accept()
            print("Главный цикл")
            while True:
                data = recvall(conn)
                end = b"\r\n\r\n"
                if end in data:
                    client = RKSOKPhoneBook()
                    msg = client.raw_request(data)
                    conn.send(msg)
                    conn.close()
                    break
                else:
                    response = f"{INCORRECT_REQUEST} {PROTOCOL}\r\n\r\n".encode()
                    conn.send(response)
                    conn.close()
                    break
    except KeyboardInterrupt:
        server.close()
        print("Выключение сервера")


if __name__ == "__main__":
    run_server()
