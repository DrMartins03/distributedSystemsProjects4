# Epidemic Replication
Martí Gómez & Marc Soto (ICE Group)

## Description
This project implements a three-layer distributed system where each layer uses a different replication strategy. The setup includes seven nodes: three in the core layer and two in each outer layer. Each maintain its own copy of a shared data file. Client operations, defined in a transaction file, are processed by the core layer, while the other layers serve read-only requests. To visualize how updates propagate through the system, a WebSocket-based web dashboard displays the live state of every node in real time.
## Previous Requirements

Our project uses standard Python libraries with the exception of PyYAML and websockets, which might be necessary to install with pip before executing the code.

```bash
pip install PyYAML websockets
```

## Program Execution

To run the full system, open several terminals and execute the following commands.
Important: All nodes must be running before executing the main program; otherwise, transactions will not propagate correctly. 
### Core Layer
#### A1 Node
```bash
python CoreLayer.py 1
```

#### A2 Node
```bash
python CoreLayer.py 2
```

#### A3 Node
```bash
python CoreLayer.py 3
```

### First Layer
#### B1 Node
```bash
python FirstLayer.py 1
```

#### B2 Node
```bash
python FirstLayer.py 2
```

### Second Layer
#### C1 Node
```bash
python SecondLayer.py 1
```

#### C2 Node
```bash
python SecondLayer.py 2
```

### Web Application

Open the file [web_app.html](web_app.html) in your web browser.

### Main
Finally, run the main program responsible of executing client transactions (on a different terminal as well).
```bash
python main.py 
```

### Clients request
The clients request can be edited directly on the following file
```bash
python clientRequests.txt 
```