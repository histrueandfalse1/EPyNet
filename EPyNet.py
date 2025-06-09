import socket
import json
import warnings
import threading

TCP_PROT = socket.SOCK_STREAM
UDP_PROT = socket.SOCK_DGRAM

class Server:
    def __init__(self, host: str, port: int, max_data_size: int, max_conn: int = 5, mode: str = "TCP", on_receive=None):
        self.C_sockets = []
        self.max_data_size = max_data_size
        self.d_receive = on_receive
        self._lock = threading.Lock()
        self.running = True  # <- Flag to control loop shutdown

        self.mode_str = mode.upper()
        if self.mode_str == "TCP":
            self.mode = TCP_PROT
        elif self.mode_str == "UDP":
            self.mode = UDP_PROT
        else:
            raise ValueError(f"Protocol {mode} is not supported.")

        self.server_socket = socket.socket(socket.AF_INET, self.mode)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((host, port))

        if self.mode == UDP_PROT:
            print(f"UDP Server started on {host}:{port}")
            threading.Thread(target=self.handle_udp_client, daemon=True).start()
        else:
            self.server_socket.listen(max_conn)
            print(f"TCP Server started on {host}:{port}")
            threading.Thread(target=self.accept_conns, daemon=True).start()

    def accept_conns(self):
        while self.running:
            try:
                cs, ca = self.server_socket.accept()
                with self._lock:
                    self.C_sockets.append((cs, ca))
                threading.Thread(target=self.handle_client, args=(cs, ca), daemon=True).start()
            except OSError:
                break  # Socket likely closed during shutdown

    def handle_client(self, cs, ca):
        try:
            while self.running:
                raw_data = cs.recv(self.max_data_size)
                if not raw_data:
                    print(f"Client {ca} disconnected.")
                    break
                try:
                    data = json.loads(raw_data.decode())
                    if self.d_receive:
                        self.d_receive(data, ca)
                    else:
                        print(f"{ca}: {data}")
                except json.JSONDecodeError as e:
                    print(f"Failed to decode JSON from {ca}: {e}")
        except Exception as e:
            print(f"Error with {ca}: {e}")
        finally:
            cs.close()
            with self._lock:
                self.C_sockets = [(sock, addr) for sock, addr in self.C_sockets if sock != cs]
            print(f"Connection at {ca} closed.")

    def handle_udp_client(self):
        while self.running:
            try:
                r_data, addr = self.server_socket.recvfrom(self.max_data_size)
                if not self.running:
                    break  

                try:
                    data = json.loads(r_data.decode())
                    if self.d_receive:
                        self.d_receive(data, addr)
                    else:
                        print(f"{addr}: {data}")
                except json.JSONDecodeError as e:
                    print(f"Failed to decode JSON from {addr}: {e}")
            except OSError:
                break  
            except Exception as e:
                print(f"UDP receive error: {e}")


    def send(self, address, data):
        data_s = json.dumps(data).encode()
        if self.mode == UDP_PROT:
            try:
                self.server_socket.sendto(data_s, address)
            except Exception as e:
                warnings.warn(f"Failed to send to {address}: {e}")
        else:
            with self._lock:
                for sock, addr in self.C_sockets:
                    if addr == address:
                        try:
                            sock.sendall(data_s)
                        except Exception as e:
                            warnings.warn(f"Failed to send to {address}: {e}")
                        break

    def broadcast(self, data):
        data_s = json.dumps(data).encode()
        if self.mode == UDP_PROT:
            warnings.warn("Broadcast is not supported for UDP mode.")
        else:
            with self._lock:
                for sock, addr in self.C_sockets:
                    try:
                        sock.sendall(data_s)
                    except Exception as e:
                        warnings.warn(f"Error broadcasting to {addr}: {e}")

    def close(self):
        self.running = False  # <- Stop all loops
        if self.mode == TCP_PROT:
            with self._lock:
                for sock, _ in self.C_sockets:
                    sock.close()
                self.C_sockets.clear()
        self.server_socket.close()
        print("Server socket closed.")

class Client:
    def __init__(self, host: str, port: int, max_data_receive: int, on_receive=None, mode: str = "TCP"):
        self.on_receive = on_receive
        self.max_data_receive = max_data_receive
        self.running = True

        self.mode_str = mode.upper()
        if self.mode_str == "TCP":
            self.mode = TCP_PROT
            self.client_socket = socket.socket(socket.AF_INET, TCP_PROT)
            self.client_socket.connect((host, port))
            print(f"Connected to TCP server at {host}:{port}")
            threading.Thread(target=self.receive, daemon=True).start()

        elif self.mode_str == "UDP":
            self.mode = UDP_PROT
            self.client_socket = socket.socket(socket.AF_INET, UDP_PROT)
            self.client_socket.bind(('127.0.0.1', 0))  # Bind to localhost and a random port
            self.server_addr = (host, port)
            threading.Thread(target=self.receive_udp, daemon=True).start()

        else:
            raise ValueError(f"Protocol {mode} is not supported.")

    def send(self, data):
        data_s = json.dumps(data).encode()
        if self.mode == UDP_PROT:
            try:
                self.client_socket.sendto(data_s, self.server_addr)
            except Exception as e:
                warnings.warn(f"Failed to send data (UDP): {e}")
        else:
            try:
                self.client_socket.sendall(data_s)
            except Exception as e:
                warnings.warn(f"Failed to send data (TCP): {e}")

    def receive(self):
        try:
            while self.running:
                raw_data = self.client_socket.recv(self.max_data_receive)
                if not raw_data:
                    print("Disconnected from server.")
                    self.close()
                    break
                try:
                    data = json.loads(raw_data.decode())
                    if self.on_receive:
                        self.on_receive(data)
                    else:
                        print("Received from server:", data)
                except json.JSONDecodeError as e:
                    print(f"Failed to decode server message: {e}")
        except Exception as e:
            if self.running:
                print(f"Receive error: {e}")

    def receive_udp(self):
        try:
            while self.running:
                raw_data, addr = self.client_socket.recvfrom(self.max_data_receive)
                try:
                    data = json.loads(raw_data.decode())
                    if self.on_receive:
                        self.on_receive(data)
                    else:
                        print(f"Received from {addr}:", data)
                except json.JSONDecodeError as e:
                    print(f"Failed to decode UDP message from {addr}: {e}")
        except Exception as e:
            if self.running:
                print(f"UDP receive error: {e}")

    def close(self):
        self.running = False
        self.client_socket.close()
        print("Client socket closed.")
