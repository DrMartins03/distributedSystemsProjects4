import json
import socket
from datetime import datetime


def _load_json(filename):
    """Load JSON content from file"""
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _save_json(filename, data):
    """Write JSON data to file"""
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)


def send_updates(filename, port):
    data = _load_json(filename)
    send_message(f"UPDATE-{data}", port)


def update(filename, key, value):
    data = _load_json(filename)
    data[key] = value
    _save_json(filename, data)


def update_all(filename, data):
    _save_json(filename, data)


def read(filename, key):
    return _load_json(filename).get(key)


def read_all(filename):
    return json.dumps(_load_json(filename), indent=4)


# Messages
def send_message(message, port):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.sendto(message.encode(), ("localhost", port))


def record_version_change(data_file, log_file, op):
    data = _load_json(data_file)

    try:
        with open(log_file, "a") as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"{timestamp} | {op}\n{json.dumps(data, indent=4)}\n\n")
    except (FileNotFoundError, json.JSONDecodeError):
        pass
