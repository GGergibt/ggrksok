import socket

PROTOCOL = "РКСОК/1.0"
response = "НОРМАЛДЫКС РКСОК/3.0".encode()


def send_response():
    """Функция для отправки ответа клиенту"""
    pass


def checking_len_of_name(request: str) -> bool:
    """Функция проверки длины имени пользователя"""
    return len(request) <= 30


def get_request(conn: str) -> str:
    """Функция для обработки запроса от клиента"""
    raw_request = conn.recv(1024)
    hra_request = raw_request.decode().strip()
    print(f"ЗАПРОС: {hra_request}")
    var_list = ["ОТДОВАЙ", "ЗОПИШИ", "УДОЛИ"]
    if hra_request.startswith(tuple(var_list)):
        verbs = hra_request.split()
        metod = verbs[0]
        verbs.remove("РКСОК/1.0")
        verbs.pop(0)
        body = " ".join(verbs)
    print(f"ОТВЕТ: {metod} {body} {PROTOCOL}")


def run_server():
    """Функция для запуска сервера РКСОК"""

    server = socket.create_server(("localhost", 5000))
    server.listen(1)
    while True:
        print("Главный цикл")
        conn, addr = server.accept()
        while True:
            get_request(conn)
            conn.sendall(response)
            conn.close()
            break
    server.close()


if __name__ == "__main__":
    run_server()
