# Epidemic Replication

## Description

In this project we were tasked with creating a layered distributed application in which each layer utilizes a different data replication strategy. The application would have 3 layers, a core layer, and two more layers each with multiple nodes. We were asked to replicate a scenario with seven nodes, three in the core layer, and two in both the first and second layer. The purpose of this application was to keep track of a data file, which has to be replicated in different ways for all of the nodes. Clients, which were simulated using a txt file with different transactions, could read and write to and from the core layer and only read from the first and second layer. Furthermore we were tasked with creating a web application where we could see the data in each node using websockets.

## Requirements

Our code mostly uses libraries built into Python, except PyYAML and websockets, thus, it is necessary to install them using pip.

```bash
pip install PyYAML websockets
```

## Execution

Please run the following commands in order and in separate terminals. Note that the program will not work properly if the nodes are not previously opened before the client executes transactions, in other words, the main program is executed. Also note that the main program initiates the process of executing transactions, thus we recommend running the web application boforehand (after initiating the different layer nodes but before executing the main program) in order to see real time data updates.

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

Open the file [web_app.html](web_app.html) in your desired browser.

### Main
Finally, run the main program responsible of executing client transactions.
```bash
python main.py 
```