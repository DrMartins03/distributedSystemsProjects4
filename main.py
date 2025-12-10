import socket
import time
from random import randint
import yaml


def send_message(msg, port):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.sendto(msg.encode(), ("localhost", port))


def wait_for_reply(sock):
    sock.settimeout(1)
    while True:
        try:
            msg, _ = sock.recvfrom(1024)
            parts = msg.decode().split('-')
            value = parts[3]
            return None if value == "None" else int(value)
        except socket.timeout:
            continue


def pick_random_replica(port_list):
    return port_list[randint(0, len(port_list) - 1)]


if __name__ == "__main__":
    cfg = yaml.load(open("config.yml"), Loader=yaml.FullLoader)
    main_port = cfg["Main"]["port"]

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", main_port))

    layers = [[node["port"] for node in layer.values()] for layer in cfg["Layers"].values()]

    with open("transactions.txt") as f:
        for line in f.read().splitlines():
            parts = line.split(', ')

            if parts[0] == 'b':
                for op in parts[1:]:
                    if op.startswith('w'):
                        key, val = op[2:].rstrip(')').split(',')
                        send_message(f"WRITE-{main_port}-{key}-{val}", pick_random_replica(layers[0]))
                        wait_for_reply(sock)
                        print("write successful")
                    elif op.startswith('r'):
                        key = op[2:].rstrip(')')
                        send_message(f"READ-{main_port}-{key}-0", pick_random_replica(layers[0]))
                        value = wait_for_reply(sock)
                        print(f"read: {value}" if value is not None else f"Error: no value found for {key}")
                    time.sleep(2)
            else:
                layer = int(parts[0][1])
                for op in parts[1:]:
                    if op.startswith('c'):
                        continue
                    key = op[2:].rstrip(')')
                    send_message(f"READ-{main_port}-{key}-0", pick_random_replica(layers[layer]))
                    value = wait_for_reply(sock)
                    print(f"read: {value}" if value is not None else f"Error: no value found for {key}")
                    time.sleep(2)
