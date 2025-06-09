# EPyNet

**EPyNet** is a lightweight Python framework that wraps around the built-in `socket` module. It simplifies client-server communication, making it easier to develop multiplayer games or other networked applications.

---

## Overview

- Built-in support for TCP connections (UDP planned)
- Supports multiple clients using threads
- Uses `pickle` for easy object serialization
- Callback-based data reception on both server and client
- Simple interface for sending and broadcasting data

---

## Classes & Functions

---

### `class Server`

**Main server class** that manages connections, handles client data, and sends responses.

#### Constructor

```python
Server(host, port, max_data_size, max_conn=5, mode="TCP", on_receive=None)
```

| Parameter        | Type     | Description |
|------------------|----------|-------------|
| `host`           | `str`    | IP address to bind the server to (e.g., `"127.0.0.1"`) |
| `port`           | `int`    | Port number to listen on |
| `max_data_size`  | `int`    | Max size in bytes for incoming data |
| `max_conn`       | `int`    | Max number of queued connections |
| `mode`           | `str`    | Protocol mode (currently only `"TCP"` is supported) |
| `on_receive`     | `callable` | Function called when data is received: `on_receive(data, client_address)` |

> Starts listening for connections immediately by calling `accept_conns()`.

---

#### `send(address, data)`

Sends data to a specific connected client.

```python
server.send(("127.0.0.1", 5000), {"type": "chat", "message": "Hello!"})
```

- **`address`**: A tuple `(host, port)` identifying the client.
- **`data`**: Any Python object that can be serialized with `pickle`.

---

#### `broadcast(data)`

Sends the same data to all connected clients.

```python
server.broadcast({"type": "event", "name": "game_start"})
```

- **`data`**: A serializable Python object.
- Great for notifying all clients of a shared event.

---

### `class Client`

Handles connection to the server, data sending, and optionally receives incoming data using a callback function.

#### Constructor

```python
Client(host, port, max_data_receive, on_receive=None)
```

| Parameter             | Type       | Description |
|-----------------------|------------|-------------|
| `host`                | `str`      | Server IP address |
| `port`                | `int`      | Server port |
| `max_data_receive`    | `int`      | Max size of data to receive at once |
| `on_receive`          | `callable` | Optional callback: `on_receive(data)` |

---

#### `send(data)`

Sends data to the connected server.

```python
client.send({"action": "jump", "player_id": 3})
```

- **`data`**: Any picklable object to transmit to the server.

---

#### `receive()`

Listens for messages from the server and processes them.

```python
client.receive()
```

- Runs an infinite loop waiting for data from the server.
- If `on_receive` is set, it is called with the received data.
- If no callback is set, data is printed to the console.
- **Blocking**: run in a separate thread if the client needs to stay responsive.

Example:

```python
import threading

def handle_data(data):
    print("Server said:", data)

client = Client("localhost", 9999, 4096, on_receive=handle_data)
threading.Thread(target=client.receive, daemon=True).start()
```

---

## ⚠️ Notes

- Data is serialized using `pickle`. Be cautious when using `pickle` with untrusted input.
- Currently only supports TCP sockets.
- All communication must be with picklable Python objects.

---

## Example Usage

```python
# Server-side
def on_receive(data, address):
    print(f"Received from {address}: {data}")

server = main.Server("localhost", 1234, max_data_size=4096, on_receive=on_receive)
# Client-side
```

```python
# Client-side
client = Client("localhost", 1234, max_data_receive=4096)
client.send({"message": "Hello, server!"})
```

---
