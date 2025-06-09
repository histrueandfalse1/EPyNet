# EPyNet

**EPyNet** is a lightweight Python framework that wraps around the built-in `socket` module. It simplifies client-server communication, making it easier to develop multiplayer games or other networked applications.

---

## Overview

- Built-in support for TCP connections (UDP not currently supported)
- Handles multiple clients using background threads
- Uses `json` for Python object serialization (safe for basic types)
- Callback-based data reception on both server and client
- Simple interface for sending and broadcasting data

---

## Classes & Important Variables

### `class Server`
**Description:**  
Main server class that manages TCP connections, handles client data, and sends responses.

#### Constructor
```python
Server(host, port, max_data_size, max_conn=5, mode="TCP", on_receive=None)
```
| Parameter        | Type       | Description |
|------------------|------------|-------------|
| `host`           | `str`      | IP address to bind the server to (e.g., `"127.0.0.1"`) |
| `port`           | `int`      | Port number to listen on |
| `max_data_size`  | `int`      | Max size in bytes for incoming data |
| `max_conn`       | `int`      | Max number of queued connections |
| `mode`           | `str`      | Protocol mode (currently only `"TCP"` is supported) |
| `on_receive`     | `callable` | Function called when data is received: `on_receive(data, client_address)` |

> Automatically starts listening for connections in a background thread.

#### Methods

- **`send(address, data)`**  
  Sends data (must be JSON-serializable) to a specific connected client.
  ```python
  server.send(("127.0.0.1", 5000), {"type": "chat", "message": "Hello!"})
  ```

- **`broadcast(data)`**  
  Sends the same data to all connected clients.
  ```python
  server.broadcast({"type": "event", "name": "game_start"})
  ```

- **`close()`**  
  Closes all client connections and the server socket.

- **`C_sockets`**  
  A list containing connected clients, formatted as: `(socket, (ip, port))`.

#### Internal Methods (for internal use only, do not call directly)
- `accept_conns(self)`: Accepts incoming client connections in a background thread.
- `handle_client(self, cs, ca)`: Handles communication with a connected client.

---

### `class Client`
**Description:**  
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

> Automatically connects to the server and begins listening in a background thread.

#### Methods

- **`send(data)`**  
  Sends data (must be JSON-serializable) to the connected server.
  ```python
  client.send({"action": "jump", "player_id": 3})
  ```

- **`close()`**  
  Closes the connection to the server.

#### Internal Methods (for internal use only, do not call directly)
- `receive()`: Receives messages from the server and processes them using the callback function if provided.

---

## Notes

- Data is serialized using `json`. Only basic Python types (dict, list, str, int, float, bool, None) are supported.
- Only TCP is supported in the current version.
- All transmitted objects must be JSON-serializable.
- If `on_receive` on either the `Client` or `Server` is not set, received data will be printed to the console.
- To install EPyNet, simply drag the EPyNet.py file into your working directory. Then in another script, write `from EPyNet import Server, Client`.

---

## Example Usage

### Server

```python
from EPyNet import Server

def on_receive(data, addr):
    print(f"Received from {addr}: {data}")

server = Server("127.0.0.1", 12345, max_data_size=4096, on_receive=on_receive)
```

### Client

```python
from EPyNet import Client

def handle_server_message(data):
    print("Received:", data)

client = Client("127.0.0.1", 12345, max_data_receive=4096, on_receive=handle_server_message)
client.send({"type": "message", "text": "Hello, server!"})
```

---