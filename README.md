# EPyNet

**EPyNet** is a lightweight Python framework that wraps around the built-in `socket` module. It simplifies client-server communication, making it easier to develop multiplayer games or other networked applications.

---

## Overview

- Built-in support for **TCP and UDP** connections
- Handles multiple TCP clients using background threads
- Uses `json` for Python object serialization (safe for basic types)
- Callback-based data reception on both server and client
- Simple interface for sending and broadcasting data
- Thread-safe client management for TCP

---

## Classes & Important Variables

### `class Server`
**Description:**  
Main server class that manages TCP or UDP connections, handles client data, and sends responses.

#### Constructor
```python
Server(host, port, max_data_size, max_conn=5, mode="TCP", on_receive=None)
```
| Parameter        | Type       | Description |
|------------------|------------|-------------|
| `host`           | `str`      | IP address to bind the server to (e.g., `"127.0.0.1"`) |
| `port`           | `int`      | Port number to listen on |
| `max_data_size`  | `int`      | Max size in bytes for incoming data |
| `max_conn`       | `int`      | Max number of queued connections (TCP only) |
| `mode`           | `str`      | Protocol mode: `"TCP"` or `"UDP"` |
| `on_receive`     | `callable` | Function called when data is received: `on_receive(data, client_address)` |

> Automatically starts listening for connections or datagrams in a background thread.

#### Methods

- **`send(address, data)`**  
  Sends data (must be JSON-serializable) to a specific connected client (TCP) or address (UDP).
  ```python
  server.send(("127.0.0.1", 5000), {"type": "chat", "message": "Hello!"})
  ```

- **`broadcast(data)`**  
  Sends the same data to all connected clients (TCP only).
  ```python
  server.broadcast({"type": "event", "name": "game_start"})
  ```
  > For UDP, this method will warn that broadcast is not supported.

- **`close()`**  
  Closes all client connections (TCP) and the server socket, and stops all server threads.

- **`C_sockets`**  
  A list containing connected TCP clients, formatted as: `(socket, (ip, port))`.  
  > Not used for UDP.

#### Internal Methods (for internal use only, do not call directly)
- `accept_conns(self)`: Accepts incoming TCP client connections in a background thread.
- `handle_client(self, cs, ca)`: Handles communication with a connected TCP client.
- `handle_udp_client(self)`: Handles incoming UDP datagrams in a background thread.

---

### `class Client`
**Description:**  
Handles connection to the server (TCP or UDP), data sending, and optionally receives incoming data using a callback function.

#### Constructor
```python
Client(host, port, max_data_receive, on_receive=None, mode="TCP")
```
| Parameter             | Type       | Description |
|-----------------------|------------|-------------|
| `host`                | `str`      | Server IP address |
| `port`                | `int`      | Server port |
| `max_data_receive`    | `int`      | Max size of data to receive at once |
| `on_receive`          | `callable` | Optional callback: `on_receive(data)` |
| `mode`                | `str`      | Protocol mode: `"TCP"` or `"UDP"` |

> Automatically connects to the server and begins listening in a background thread.

#### Methods

- **`send(data)`**  
  Sends data (must be JSON-serializable) to the connected server (TCP) or to the server address (UDP).
  ```python
  client.send({"action": "jump", "player_id": 3})
  ```

- **`close()`**  
  Closes the connection to the server and stops the client thread.

#### Internal Methods (for internal use only, do not call directly)
- `receive()`: Receives data from the server (TCP) and processes it using the callback function if provided.
- `receive_udp()`: Receives data from the server (UDP) and processes it using the callback function if provided.

---

## Notes

- Data is serialized using `json`. Only basic Python types (dict, list, str, int, float, bool, None) are supported.
- Both TCP and UDP are supported.  
  - **TCP:** Supports multiple clients, broadcasting, and per-client addressing.
  - **UDP:** Connectionless, no client tracking, no broadcast support.
- All transmitted objects must be JSON-serializable.
- If `on_receive` on either the `Client` or `Server` is not set, received data will be printed to the console.
- To install EPyNet, simply drag the EPyNet.py file into your working directory. Then in another script, write `from EPyNet import Server, Client`.

---

## Example Usage

### TCP Server

```python
from EPyNet import Server

def on_receive(data, addr):
    print(f"Received from {addr}: {data}")

server = Server("127.0.0.1", 12345, max_data_size=4096, on_receive=on_receive, mode="TCP")
```

### TCP Client

```python
from EPyNet import Client

def handle_server_message(data):
    print("Received:", data)

client = Client("127.0.0.1", 12345, max_data_receive=4096, on_receive=handle_server_message, mode="TCP")
client.send({"type": "message", "text": "Hello, server!"})
```

### UDP Server

```python
from EPyNet import Server

def on_receive(data, addr):
    print(f"Received from {addr}: {data}")

server = Server("127.0.0.1", 12346, max_data_size=4096, on_receive=on_receive, mode="UDP")
```

### UDP Client

```python
from EPyNet import Client

def handle_server_message(data):
    print("Received:", data)

client = Client("127.0.0.1", 12346, max_data_receive=4096, on_receive=handle_server_message, mode="UDP")
client.send({"type": "message", "text": "Hello, UDP server!"})
```

---

## Limitations

- UDP mode does **not** support broadcasting to all clients.
- Only JSON-serializable data can be sent.
- For UDP, the server does not track clients; you must manage addressing yourself if needed.

---
