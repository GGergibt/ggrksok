import socket
from pathlib import Path

PROTOCOL = "РКСОК/1.0"

METOD = ("ОТДОВАЙ", "ЗОПИШИ", "УДОЛИ")
OK = "НОРМАЛДЫКС"
NOTFOUND = "НИНАШОЛ"
NOT_APPROVED = "НИЛЬЗЯ"
INCORRECT_REQUEST = "НИПОНЯЛ"


class RKSOKPhoneBook:
    """Phonebook working with RKSOK server."""

    def __init__(self, conn: str):
        self._conn = conn
        self._name, self._phone, self._verb, self._method = None, None, None, None

    def recvall(self):
        BUFF_SIZE = 1024
        data = b""
        while True:
            part = self._conn.recv(BUFF_SIZE)
            # print(f"Часть запроса: {part.decode()}")
            data += part
            if len(part) < 1024:
                break
        msg = self.raw_request(data)
        return msg

    def raw_request(self, data):
        end = b"\r\n\r\n"
        if end in data:
            data = self.get_request(data.decode())
        else:
            data = f"{INCORRECT_REQUEST} {PROTOCOL}\r\n\r\n".encode()
        return data

    def get_request(self, msg):
        """Функция для обработки запроса от клиента"""
        request = [x for x in msg.split("\r\n") if len(x) > 0]
        response_client = self.compile_response(request)
        return response_client

    def compile_response(self, res):
        """Функция собирает ответ для клиента"""
        if len(res) > 1:
            body_response = self.parse_body_request(res[0])
            self._phone = res[1::]
            response = f"{body_response}\r\n{self._phone}"
        else:
            response = self.parse_body_request(res[0])

        if response.startswith(INCORRECT_REQUEST):
            response_client = f"{INCORRECT_REQUEST} {PROTOCOL}".encode()
        else:
            response_client = self.send_to_checking_server(response)
        return response_client

    def parse_body_request(self, req: str) -> str:
        """Функция для получения метода и имени пользователя"""
        verbs = req.split()
        verbs.remove(PROTOCOL)
        if self.get_method(verbs[0]):
            verbs.pop(0)
            if self.get_name(verbs):
                raw_response = f"{self._method} {self._name} {PROTOCOL}"
        else:
            raw_response = f"{INCORRECT_REQUEST} {PROTOCOL}"
        return raw_response

    def get_method(self, method):
        """Функция проверяет корректность метода РКСОК"""
        if method in METOD:
            self._method = method
            return self._method

    def get_name(self, verbs):
        """Функция проверяет имя пользователя"""
        name = " ".join(verbs)
        if self.checking_len_of_name(name):
            self._name = name
            return self._name

    def checking_len_of_name(self, name: str) -> bool:
        """Функция проверки длины имени пользователя"""
        return len(name) <= 30 and len(name) != 0

    def send_to_checking_server(self, res: str) -> str:
        """Функция для запроса на сервер проверки"""
        method = "АМОЖНА? РКСОК/1.0"
        conn = socket.create_connection(("vragi-vezde.to.digital", 51624))
        request = f"{method}\r\n {res}\r\n\r\n".encode()
        conn.send(request)
        res_vragi = conn.recv(1024).decode()
        if self.parse_response_check_server(res_vragi):
            response = self.work_phonebook(res_vragi)
            return response
        else:
            return f"{res_vragi}".encode()

    def parse_response_check_server(self, res_vragi: str) -> bool:
        """Функция для проверки МОЖНО или НИЛЬЗЯ"""
        if res_vragi.startswith("МОЖНА"):
            return True
        else:
            return False

    def work_phonebook(self, res_vragi: str):
        """Функция для работы с телефонной книгой"""
        if self._method == "ОТДОВАЙ":
            response = self.get_phonebook()
            return response
        elif self._method == "ЗОПИШИ":
            response = self.write_phonebook()
            return response
        elif self._method == "УДОЛИ":
            response = self.delete_phonebook()
            return response
        else:
            return f"{INCORRECT_REQUEST} {PROTOCOL}\r\n\r\n".encode()

    def get_phonebook(self):
        """Функция проверяет наличие файла и если он есть отдает номер телефона"""
        path = Path(f"phonebook/{self._name}.txt")
        if path.exists():
            with path.open() as f:
                phone = "".join(f.readlines())
            response = f"{OK} {PROTOCOL}\r\n{phone}\r\n\r\n".encode()
        else:
            response = f"{NOTFOUND} {PROTOCOL}\r\n\r\n".encode()
        return response

    def write_phonebook(self):
        """Функция  создает файла по имени и записывает номер телефона"""
        with open(f"phonebook/{self._name}.txt", "w") as file:
            file.writelines(self._phone)
        response = f"{OK} {PROTOCOL}\r\n\r\n".encode()
        return response

    def delete_phonebook(self):
        """Функция удаляет файл по имени"""
        path = Path(f"phonebook/{self._name}.txt")
        if path.exists():
            path.unlink()
            response = f"{OK} {PROTOCOL}\r\n\r\n".encode()
        else:
            response = f"{NOTFOUND} {PROTOCOL}\r\n\r\n".encode()
        return response


def run_server():
    """Функция для запуска сервера РКСОК"""
    try:
        server = socket.create_server(("localhost", 50007))
        server.listen(1)
        while True:
            conn, addr = server.accept()
            print("Главный цикл")
            while True:
                try:
                    client = RKSOKPhoneBook(conn)
                    msg = client.recvall()
                    conn.send(msg)
                    conn.close()
                    break
                except:
                    neponyal = f"НИПОНЯЛ РКСОК/1.0\r\n\r\n".encode()
                    conn.send(neponyal)
                    conn.close()
                    break

            # conn.close()
    except KeyboardInterrupt:
        server.close()
        print("Выключение сервера")


if __name__ == "__main__":
    run_server()
