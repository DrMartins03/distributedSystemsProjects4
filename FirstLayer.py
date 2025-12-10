import asyncio
import json
import socket
import threading
import time
import yaml
import sys
from websockets.asyncio.server import serve
from common import read, update_all, update_log, send_message, read_all, send_updates

event = asyncio.Event()


class FirstLayer:

    def __init__(self, port, node_id, children):
        self.port = port
        self.id = node_id
        self.children = children

        self.log_file = f"logs/B{self.id}.txt"
        self.data_file = f"data/B{self.id}.json"
        open(self.data_file, "w").close()

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(("0.0.0.0", self.port))

        threading.Thread(target=self.listen, daemon=True).start()
        threading.Thread(target=self.propagate_updates, daemon=True).start()

    def listen(self):
        self.socket.settimeout(1)
        while True:
            try:
                msg, _ = self.socket.recvfrom(1024)
                parts = msg.decode().split('-')
                msg_type = parts[0]

                print(msg.decode())

                if msg_type == "READ":
                    self.handle_read(int(parts[1]), parts[2])

                elif msg_type == "UPDATE":
                    data = json.loads(parts[1].replace("'", '"'))
                    update_all(self.data_file, data)
                    update_log(self.data_file, self.log_file, "UPDATE")
                    event.set()

            except socket.timeout:
                continue

    def handle_read(self, client_port, key):
        value = read(self.data_file, key)
        send_message(f"REPLY-{self.port}-{key}-{value}", client_port)

    def propagate_updates(self):
        while True:
            time.sleep(10)
            for child in self.children:
                send_updates(self.data_file, child)


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
        print("Usage: python3 FirstLayer.py <node_id>")
        sys.exit(1)

    cfg = yaml.load(open("config.yml"), Loader=yaml.FullLoader)
    node_cfg = cfg["Layers"]["FirstLayer"][f"b{sys.argv[1]}"]

    global global_data_file
    global_data_file = f"data/B{sys.argv[1]}.json"

    FirstLayer(node_cfg["port"], sys.argv[1], node_cfg["children"])
    asyncio.run(start_websocket(node_cfg["web"]))
