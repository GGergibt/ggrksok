import asyncio
from RKSOKPhonebook import RKSOKPhoneBook


async def recvall(reader):
    """Reading data from socket"""
    data = b""
    while True:
        part = await reader.read(100)
        data += part
        end = b"\r\n\r\n"
        if part.endswith(end):
            break
    return data


async def handle_echo(reader, writer):
    # data = await reader.read(100)
    data = await recvall(reader)
    message = data.decode()
    client = RKSOKPhoneBook()
    official_response = client.get_request(message)

    writer.write(official_response)
    await writer.drain()

    print("Close the connection")
    writer.close()


async def main():
    server = await asyncio.start_server(handle_echo, "127.0.0.1", 50007)

    addr = server.sockets[0].getsockname()
    print(f"Serving on {addr}")

    async with server:
        await server.serve_forever()


asyncio.run(main())
