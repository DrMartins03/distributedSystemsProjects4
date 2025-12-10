import socket
from random import randint
import time
import yaml

def send_message(message, port):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.sendto(message.encode(), ("localhost", port))

def await_reply(sock):
    sock.settimeout(1)
    while True:
        try:
            message, _ = sock.recvfrom(1024)
            msg_parts = message.decode().split('-')
            type = msg_parts[0]
            port = int(msg_parts[1])
            key = msg_parts[2]

            if msg_parts[3] != 'None':
                return int(msg_parts[3])
            else:
                return None

        except socket.timeout:
            pass


if __name__ == "__main__":
    with open("config.yml", "r") as file:
        config = yaml.load(file, Loader=yaml.FullLoader)

    port = config["Main"]["port"]
    main_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    main_socket.bind(("0.0.0.0", port))

    layer_ports = []
    for layer_name, layer_data in config["Layers"].items():
        ports = [node["port"] for node in layer_data.values()]
        layer_ports.append(ports)

    with open("transactions.txt", "r") as file:
        lines = file.readlines()
        lines = [line.strip() for line in lines]    

        for line in lines:
            parts = line.split(', ')

            if parts[0] == 'b':
                for part in parts[1:]:
                    if part[0] == 'w':
                        key, value = part[2:].replace(')', '').split(',')
                        send_message(f"WRITE-{port}-{key}-{value}", layer_ports[0][randint(0, len(layer_ports[0]) - 1)])
                        reply = await_reply(main_socket)
                        print(f"write successful")
                    elif part[0] == 'r': 
                        key= part[2:].replace(')', '')
                        send_message(f"READ-{port}-{key}-0", layer_ports[0][randint(0, len(layer_ports[0]) - 1)])
                        reply = await_reply(main_socket)
                        if reply == None:
                            print(f"Error: no value doun with key {key}.")
                        else:
                            print(f"read: {reply}")
                    else:
                        break
                    time.sleep(2)
            else:
                layer = parts[0][1]
                for part in parts[1:]:
                    if part[0] != 'c': 
                        key= part[2:].replace(')', '')
                        send_message(f"READ-{port}-{key}-0", layer_ports[int(layer)][randint(0, len(layer_ports[int(layer)]) - 1)])
                        reply = await_reply(main_socket)
                        if reply == None:
                            print(f"Error: no value doun with key {key}.")
                        else:
                            print(f"read: {reply}")
                    time.sleep(2)                 
            
            