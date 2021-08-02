import socket


def send_to_checking_server(enquiry: str) -> str:

    """Sends request to the serve checking"""
    method = "АМОЖНА? РКСОК/1.0"
    try:
        conn = socket.create_connection(("vragi-vezde.to.digital", 51624))
        request = f"{method}\r\n {enquiry}\r\n\r\n".encode()
        conn.send(request)
        official_response = conn.recv(1024).decode()
        if parse_response_check_server(official_response):
            return True
        else:
            return official_response

    except:
        print("Партия занята и не может ответить на твои глупые запросы")


def parse_response_check_server(official_response: str) -> bool:
    """Party verification of the request"""
    if official_response.startswith("МОЖНА"):
        return True
