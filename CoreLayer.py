from common import *
import socket
import time
import threading
from queue import Queue
import yaml
import sys
import asyncio
import os
from websockets.asyncio.server import serve

event = asyncio.Event()
data_file = None

class CoreLayer:

    def __init__(self, port, id, peers, children):
        self.port = port
        self.id = id
        self.peers = peers
        self.children = children
        self.queue = Queue()
        self.lock = threading.Lock()
        self.num_acks = 0
        self.required_acks = 0
        self.num_updates = 0

        # Ensure required directories exist
        os.makedirs("logs", exist_ok=True)
        os.makedirs("data", exist_ok=True)

        self.log_file = f"logs/A{self.id}.txt"
        with open(self.log_file, "w") as file:
            pass

        global data_file
        data_file = f"data/A{self.id}.json"

        self.data_file = data_file
        with open(self.data_file, "w") as file:
            pass

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(("0.0.0.0", self.port))

        threading.Thread(target=self.listen, daemon=True).start()
        threading.Thread(target=self.handle_transactions, daemon=True).start()

    def listen(self):
        self.socket.settimeout(1)
        while True:
            try:
                message, _ = self.socket.recvfrom(1024)
                msg = message.decode()
                msg_parts = msg.split('-')
                type = msg_parts[0]

                print(msg)
                
                if type == "WRITE":
                    self.queue.put(msg)
                elif type == "READ":
                    self.queue.put(msg)
                elif type == "UPDATE":
                    self.queue.put(msg)
                elif type == "ACK":
                    with self.lock:
                        self.num_acks+=1

            except socket.timeout:
                pass

    def handle_transactions(self):
        while True:
            if not self.queue.empty():
                message = self.queue.get()
                msg_parts = message.split('-')
                type = msg_parts[0]
                port = int(msg_parts[1])
                key = msg_parts[2]
                value = int(msg_parts[3])

                if type == "WRITE":
                    
                    update(self.data_file, key, value)
                    update_log(self.data_file, self.log_file, type)
                    event.set()

                    for peer in self.peers:
                        send_message(f"UPDATE-{self.port}-{key}-{value}", peer)
                        self.required_acks+=1

                    while True:
                        time.sleep(0.001)
                        with self.lock:
                            if self.num_acks == self.required_acks: 
                                break

                    self.num_acks = 0
                    self.required_acks = 0

                    self.num_updates+=1
    
                    if self.num_updates == 10:
                        self.num_updates = 0
                        for child in self.children:
                            send_updates(self.data_file, child)

                    send_message(f"REPLY-{self.port}-1-1", port)

                elif type == "READ":

                    value_read = read(self.data_file, key)
                    send_message(f"REPLY-{self.port}-{key}-{value_read}", port)

            
                elif type == "UPDATE":
                    
                    update(self.data_file, key, value)
                    update_log(self.data_file, self.log_file, type)
                    event.set()

                    self.num_updates+=1
    
                    if self.num_updates == 10:
                        self.num_updates = 0
                        for child in self.children:
                            send_updates(self.data_file, child)
                    
                    send_message(f"ACK-{self.port}-1-1", port)

async def update_websocket(websocket):

    while True:
        if event.is_set():
            
            global data_file
            data = read_all(data_file)
            await websocket.send(f"{data}")

            event.clear()
        else:
            await asyncio.sleep(0.001)


async def start_websocket(port):
    async with serve(update_websocket, "localhost", port) as server:
        try:
            await asyncio.Future()  
        except asyncio.CancelledError:  
            pass 

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 CoreLayer.py <node_id>")
        sys.exit(1)

    with open("config.yml", "r") as file:
        config = yaml.load(file, Loader=yaml.FullLoader)["Layers"]["CoreLayer"][f"a{sys.argv[1]}"]

    node = CoreLayer(
        config["port"], 
        sys.argv[1], 
        config["peers"], 
        config["children"]
    )

    try:
        asyncio.run(start_websocket(config["web"]))
    except KeyboardInterrupt:
        pass
