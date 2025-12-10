from common import *
import socket
import time
import threading
import yaml
import sys
import asyncio
from websockets.asyncio.server import serve

event = asyncio.Event()
data_file = None

class FirstLayer:

    def __init__(self, port, id, children):
        self.port = port
        self.id = id
        self.children = children
        self.num_updates = 0

        self.log_file = f"logs/B{self.id}.txt"

        global data_file 
        data_file = f"data/B{self.id}.json"

        self.data_file = data_file
        with open(self.data_file, "w") as file:
            pass

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(("0.0.0.0", self.port))

        threading.Thread(target=self.listen, daemon=True).start()
        threading.Thread(target=self.timer, daemon=True).start()

    def listen(self):
        self.socket.settimeout(1)
        while True:
            try:
                message, _ = self.socket.recvfrom(1024)

                print(message.decode())
                
                msg_parts = message.decode().split('-')
                type = msg_parts[0]
                
                if type == "READ":
                    port = int(msg_parts[1])
                    key = msg_parts[2]
                    value_read = read(self.data_file, key)
                    send_message(f"REPLY-{self.port}-{key}-{value_read}", port)

                elif type == "UPDATE":
                    data = msg_parts[1]
                    update_all(self.data_file, json.loads(data.replace("'", '"')))
                    update_log(self.data_file, self.log_file, type)
                    event.set()

            except socket.timeout:
                pass
    
    def timer(self):
        while(True):
            time.sleep(10)
            for child in self.children:
                send_updates(self.data_file, child)


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
        print("Usage: python3 FirstLayer.py <node_id>")
        sys.exit(1)

    with open("config.yml", "r") as file:
        config = yaml.load(file, Loader=yaml.FullLoader)["Layers"]["FirstLayer"][f"b{sys.argv[1]}"]

    node = FirstLayer(
        config["port"], 
        sys.argv[1],  
        config["children"]
    )

    try:
        asyncio.run(start_websocket(config["web"]))
    except KeyboardInterrupt:
        pass


