import asyncio
import os
import socket
import threading
import time
from queue import Queue
import yaml
import sys
from websockets.asyncio.server import serve
from common import send_message, update, read, send_updates, update_log, read_all

event = asyncio.Event()


class CoreLayer:

    def __init__(self, port, node_id, peers, children):
        self.port = port
        self.id = node_id
        self.peers = peers
        self.children = children

        self.queue = Queue()
        self.lock = threading.Lock()
        self.pending_acks = 0
        self.required_acks = 0
        self.update_counter = 0

        # Ensure required directories exist
        os.makedirs("logs", exist_ok=True)
        os.makedirs("data", exist_ok=True)

        self.log_file = f"logs/A{self.id}.txt"
        self.data_file = f"data/A{self.id}.json"

        open(self.log_file, "w").close()
        open(self.data_file, "w").close()

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(("0.0.0.0", self.port))

        threading.Thread(target=self.listen, daemon=True).start()
        threading.Thread(target=self.process_messages, daemon=True).start()

    def listen(self):
        self.socket.settimeout(1)
        while True:
            try:
                msg, _ = self.socket.recvfrom(1024)
                parts = msg.decode().split('-')
                msg_type = parts[0]

                print(msg.decode())

                if msg_type in {"WRITE", "READ", "UPDATE"}:
                    self.queue.put(parts)
                elif msg_type == "READ":
                    self.queue.put(msg)
                elif msg_type == "UPDATE":
                    self.queue.put(msg)
                elif msg_type == "ACK":
                    with self.lock:
                        self.pending_acks += 1

            except socket.timeout:
                pass

    def process_messages(self):
        while True:
            if self.queue.empty():
                continue

            parts = self.queue.get()
            msg_type, src_port, key, value = parts[0], int(parts[1]), parts[2], int(parts[3])

            if msg_type == "WRITE":
                self.handle_write(src_port, key, value)

            elif msg_type == "READ":
                value = read(self.data_file, key)
                send_message(f"REPLY-{self.port}-{key}-{value}", src_port)

            elif msg_type == "UPDATE":
                self.handle_update(src_port, key, value)

    def handle_write(self, client_port, key, value):
        update(self.data_file, key, value)
        update_log(self.data_file, self.log_file, "WRITE")
        event.set()

        self.required_acks = len(self.peers)
        self.pending_acks = 0

        for peer in self.peers:
            send_message(f"UPDATE-{self.port}-{key}-{value}", peer)

        while True:
            time.sleep(0.001)
            with self.lock:
                if self.pending_acks >= self.required_acks:
                    break

        self.update_counter += 1
        if self.update_counter >= 10:
            self.update_counter = 0
            for child in self.children:
                send_updates(self.data_file, child)

        send_message(f"REPLY-{self.port}-1-1", client_port)

    def handle_update(self, src_port, key, value):
        update(self.data_file, key, value)
        update_log(self.data_file, self.log_file, "UPDATE")
        event.set()

        self.update_counter += 1
        if self.update_counter >= 10:
            self.update_counter = 0
            for child in self.children:
                send_updates(self.data_file, child)

        send_message(f"ACK-{self.port}-1-1", src_port)


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
        print("Usage: python3 CoreLayer.py <node_id>")
        sys.exit(1)

    cfg = yaml.load(open("config.yml"), Loader=yaml.FullLoader)
    node_cfg = cfg["Layers"]["CoreLayer"][f"a{sys.argv[1]}"]

    global global_data_file
    global_data_file = f"data/A{sys.argv[1]}.json"

    CoreLayer(node_cfg["port"], sys.argv[1], node_cfg["peers"], node_cfg["children"])
    asyncio.run(start_websocket(node_cfg["web"]))
