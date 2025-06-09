import socket
import json
import warnings
import threading

TCP = socket.SOCK_STREAM

class Server:
    def __init__(self, host: str, port: int, max_data_size: int, max_conn: int = 5, mode: str = "TCP", on_receive=None):
        self.C_sockets = []  
        self.max_data_size = max_data_size
        self.d_receive = on_receive

        if mode.upper() != "TCP":
            raise ValueError("Only TCP is supported in this version.")

        self.server_socket = socket.socket(socket.AF_INET, TCP)
        self.server_socket.bind((host, port))
        self.server_socket.listen(max_conn)

        print(f"Server started on {host}:{port}")
        threading.Thread(target=self.accept_conns, daemon=True).start()

    def handle_client(self, cs, ca):
        self.C_sockets.append((cs, ca))
        try:
            while True:
                raw_data = cs.recv(self.max_data_size)
                if not raw_data:
                    break
                data = json.loads(raw_data.decode())
                if self.d_receive:
                    self.d_receive(data, ca)
                else:
                    print(f"{ca}: {data}")
        except Exception as e:
            print(f"Error with {ca}: {e}")
        finally:
            cs.close()
            self.C_sockets = [(sock, addr) for sock, addr in self.C_sockets if sock != cs]
            print(f"Connection at {ca} closed.")

    def send(self, address, data):
        data_s = json.dumps(data).encode()
        for sock, addr in self.C_sockets:
            if addr == address:
                try:
                    sock.sendall(data_s)
                except Exception as e:
                    warnings.warn(f"Failed to send to {address}: {e}")
                break

    def broadcast(self, data):
        data_s = json.dumps(data).encode()
        for sock, addr in self.C_sockets:
            try:
                sock.sendall(data_s)
            except Exception as e:
                warnings.warn(f"Error broadcasting to {addr}: {e}")

    def close(self):
        for sock,_ in self.C_sockets:
            sock.close()
        self.server_socket.close()
        self.C_sockets.clear()

class Client:
    def __init__(self, host: str, port: int, max_data_receive: int, on_receive=None):
        self.client_socket = socket.socket(socket.AF_INET, TCP)
        self.on_receive = on_receive
        self.client_socket.connect((host, port))
        self.max_data_receive = max_data_receive
        print(f"Connected to server at {host}:{port}")
        threading.Thread(target=self.receive, daemon=True).start()

    def send(self, data):
        data_s = json.dumps(data).encode()
        try: 
            self.client_socket.sendall(data_s)
        except Exception as e:
            warnings.warn(f"Failed to send data: {e}")

    def receive(self):
        try:
            while True:
                raw_data = self.client_socket.recv(self.max_data_receive)
                if not raw_data:
                    break
                data = json.loads(raw_data.decode())
                if self.on_receive:
                    self.on_receive(data)
                else:
                    print("Received from server:", data)
        except Exception as e:
            print(f"Receive error: {e}")
    
    def close(self):
        self.client_socket.close()
