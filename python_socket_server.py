import socket

PROTOCOL = "РКСОК/1.0"

METOD = ("ОТДОВАЙ", "ЗОПИШИ", "УДОЛИ")


def send_response(conn: str, response: str):
    """Функция для отправки ответа клиенту"""
    response_hard = "НОРМАЛДЫКС РКСОК/1.0".encode()
    conn.sendall(response_hard)


def send_to_checking_server(res: str):
    print(res)
    method = "АМОЖНА? РКСОК/1.0"
    conn = socket.create_connection(("vragi-vezde.to.digital", 51624))
    response = f"{method}\r\n {res}\r\n\r\n".encode()
    conn.send(response)
    res = conn.recv(1024)
    print(f"ОТВЕТ от ПАРТИИ: {res.decode()}")


def checking_len_of_name(request: str) -> bool:
    """Функция проверки длины имени пользователя"""
    return len(request) >= 30


def get_request(conn: str) -> str:
    """Функция для обработки запроса от клиента"""
    raw_request = conn.recv(1024).decode()
    body_request = [x for x in raw_request.split("\r\n") if len(x) > 0]
    if len(body_request) > 1:
        body_response = parse_request(body_request[0])
        phone_response = parse_phone(body_request[-1])
        response = f"{body_response}\r\n{phone_response}"
        return response
    else:
        body_response = parse_request(body_request[0])
        return body_response


def parse_request(req: str) -> str:
    """Функция для обработки запроса и получения имени пользователя и если есть телефона"""
    if req.startswith(tuple(METOD)):
        verbs = req.split()
        metod = verbs[0]
        verbs.remove("РКСОК/1.0")
        verbs.pop(0)
        name = " ".join(verbs)
        body_response = f"{metod} {name} {PROTOCOL}"
    return body_response


def parse_phone(phone_req: str) -> str:
    """Функция для обработки номера телефона"""
    phone = "".join(filter(str.isdigit, phone_req))
    if len(phone) == 11 and (phone.startswith("89") or phone.startswith("79")):
        phone = phone[1::]
    if len(phone) == 10 and phone.startswith("9"):
        phone = f"8 ({phone[0:3]}) {phone[3:6]}-{phone[6:8]}-{phone[8::]}"
    return phone


def run_server():
    """Функция для запуска сервера РКСОК"""
    server = socket.create_server(("localhost", 5000))
    server.listen(1)
    while True:
        print("Главный цикл")
        conn, addr = server.accept()
        while True:
            res = get_request(conn)
            send_to_checking_server(res)
            send_response(conn, res)
            conn.close()
            break
    server.close()


if __name__ == "__main__":
    run_server()
