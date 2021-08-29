import asyncio
from RKSOKPhonebook import RKSOKPhoneBook


async def recvall(reader) -> str:
    """Reading data from socket"""
    data = b''
    while True:
        part = await reader.read(2048)
        data += part
        end = b"\r\n\r\n"
        if data.endswith(end) or part == b'':
            break
    return data.decode()

async def handle_echo(reader, writer):
    data = await recvall(reader)
    client = RKSOKPhoneBook()
    official_response = client.get_request(data)
    writer.write(official_response)
    await writer.drain()
    writer.close()


async def main():
    server = await asyncio.start_server(handle_echo, "", 50007)
    async with server:
        await server.serve_forever()


asyncio.run(main())
