import json
import socket
from datetime import datetime

#Messages
def send_message(message, port):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.sendto(message.encode(), ("localhost", port))

def update(filename, key, value):
    try:
        with open(filename, "r") as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}

    data[key] = value

    with open(filename, "w") as file:
        json.dump(data, file, indent=4)

def read(filename, key):

    try:
        with open(filename, "r") as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}

    return data.get(key, None)

def send_updates(filename, port):
    try:
        with open(filename, "r") as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}

    send_message(f"UPDATE-{data}", port)

def update_all(filename, data):
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)

def read_all(filename):
    try:
        with open(filename, "r") as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}

    return json.dumps(data, indent=4)

def update_log(data_file, log_file, operation):
    try:
        with open(data_file, "r") as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}

    try:
        with open(log_file, "a") as file:
           file.write(f"{datetime.now()} | {operation}\n{json.dumps(data, indent=4)}\n\n")
    except (FileNotFoundError, json.JSONDecodeError):
        pass