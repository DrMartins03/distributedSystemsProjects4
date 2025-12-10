import asyncio
import json
import socket
import threading
import yaml
import sys
from websockets.asyncio.server import serve
from common import read, update_all, update_log, send_message, read_all

event = asyncio.Event()


class SecondLayer:

    def __init__(self, port, id):
        self.port = port
        self.id = id

        self.log_file = f"logs/C{self.id}.txt"
        self.data_file = f"data/C{self.id}.json"
        open(self.data_file, "w").close()

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(("0.0.0.0", self.port))

        threading.Thread(target=self.listen, daemon=True).start()

    def listen(self):
        self.socket.settimeout(1)
        while True:
            try:
                msg, _ = self.socket.recvfrom(1024)
                parts = msg.decode().split('-')
                msg_type = parts[0]

                print(msg.decode())

                if msg_type == "READ":
                    client_port, key = int(parts[1]), parts[2]
                    value = read(self.data_file, key)
                    send_message(f"REPLY-{self.port}-{key}-{value}", client_port)

                elif msg_type == "UPDATE":
                    data = json.loads(parts[1].replace("'", '"'))
                    update_all(self.data_file, data)
                    update_log(self.data_file, self.log_file, "UPDATE")
                    event.set()

            except socket.timeout:
                continue


async def websocket_handler(ws):
    while True:
        if event.is_set():
            await ws.send(read_all(global_data_file))
            event.clear()
        else:
            await asyncio.sleep(0.001)


async def start_websocket(port):
    async with serve(websocket_handler, "localhost", port):
        await asyncio.Future()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 SecondLayer.py <node_id>")
        sys.exit(1)

    cfg = yaml.load(open("config.yml"), Loader=yaml.FullLoader)
    node_cfg = cfg["Layers"]["SecondLayer"][f"c{sys.argv[1]}"]

    global global_data_file
    global_data_file = f"data/C{sys.argv[1]}.json"

    SecondLayer(node_cfg["port"], sys.argv[1])
    asyncio.run(start_websocket(node_cfg["web"]))
