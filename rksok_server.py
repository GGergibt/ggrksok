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

    def get_request(self):
        """Функция для обработки запроса от клиента"""
        raw_request = self._conn.recv(1024).decode()
        body_request = [x for x in raw_request.split("\r\n") if len(x) > 0]
        if body_request[0].startswith(tuple(METOD)):
            response_client = self.compile_response(body_request)
        else:
            response_client = f"{INCORRECT_REQUEST} {PROTOCOL}\r\n\r\n".encode()
        print(f"ЗАПРОС: {raw_request}")
        print(f"ОТВЕТ: {response_client.decode()}")
        return self._conn.send(response_client)

    def compile_response(self, res):
        """Функция собирает ответ для клиента"""
        if len(res) > 1:
            body_response = self.parse_body_request(res[0])
            self.parse_phone_request(res[-1])
            response = f"{body_response}\r\n{self._phone}"
        else:
            response = self.parse_body_request(res[0])

        if response.startswith(INCORRECT_REQUEST):
            response_client = f"{INCORRECT_REQUEST} {PROTOCOL}".encode()
        else:
            response_client = self.send_to_checking_server(response)
        return response_client

    def parse_body_request(self, req: str) -> str:
        """Функция для обработки запроса и получения имени пользователя и если есть телефона"""
        if req.startswith(tuple(METOD)):
            verbs = req.split()
            self._method = verbs[0]
            verbs.remove(PROTOCOL)
            verbs.pop(0)
            self._name = " ".join(verbs)
            if self.checking_len_of_name(self._name):
                raw_response = f"{self._method} {self._name} {PROTOCOL}"
            else:
                raw_response = f"{INCORRECT_REQUEST} {PROTOCOL}"
            return raw_response

    def parse_phone_request(self, phone_req: str) -> str:
        """Функция для обработки номера телефона"""
        self._phone = "".join(filter(str.isdigit, phone_req))
        return self._phone

    def checking_len_of_name(self, name: str) -> bool:
        """Функция проверки длины имени пользователя"""
        return len(self._name) <= 30

    def send_to_checking_server(self, res: str) -> str:
        """Функция для запроса на сервер проверки"""
        method = "АМОЖНА? РКСОК/1.0"
        conn = socket.create_connection(("vragi-vezde.to.digital", 51624))
        request = f"{method}\r\n {res}\r\n\r\n".encode()
        conn.send(request)
        res_vragi = conn.recv(1024).decode()
        if self.parse_response_check_server(res_vragi):
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
        else:
            return f"{res_vragi}".encode()

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
            file.write(self._phone)
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

    def parse_response_check_server(self, res_vragi: str) -> bool:
        """Функция для проверки МОЖНО или НИЛЬЗЯ"""
        if res_vragi.startswith("МОЖНА"):
            return True
        else:
            return False


def run_server():
    """Функция для запуска сервера РКСОК"""
    server = socket.create_server(("localhost", 5000))
    server.listen(1)
    while True:
        conn, addr = server.accept()
        print("Главный цикл")
        while True:
            client = RKSOKPhoneBook(conn)
            client.get_request()
            conn.close()
            break
    server.close()


if __name__ == "__main__":
    run_server()
