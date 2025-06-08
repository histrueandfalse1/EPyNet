import socket
import pickle
import warnings
import threading

TCP = socket.SOCK_STREAM
UDP = socket.SOCK_DGRAM

class Server:
    def __init__(self, host: str, port: int, max_data_size:int,max_conn: int = 5,mode:str="TCP",on_receive=None):
        self.C_sockets = []  
        self.max_data_size=max_data_size
        self.d_receive=on_receive
        
        self.socktype=None

        if mode.upper()=="TCP":
            self.server_socket=TCP

        elif mode.upper()=="UDP":
            self.server_socket=UDP

        else:
            raise ValueError("Incorrect socket mode given. Supported types are TCP and UDP.")
        

        self.server_socket = socket.socket(socket.AF_INET, TCP)

        self.server_socket.bind((host, port))

        self.server_socket.listen(max_conn)

        print(f"Server started on {host}:{port}")
        self.accept_conns()

    def accept_conns(self):
        while True:
            cs,ca=self.server_socket.accept()
            thread=threading.Thread(target=self.handle_client,
                                    args=(cs,ca),
                                    daemon=True)
    

    def handle_client(self,cs,ca):
        self.C_sockets.append((cs,ca))

        try:
            while True:
                data=pickle.loads(cs.recv(self.max_data_size))
                if self.d_receive:
                    self.d_receive(data,ca)
                if not data:
                    break
        except Exception as e:
            print(f"Error with {ca}:{e}")

        finally:
            cs.close()
            self.C_sockets=[
                (sock,addr) for sock, addr in self.C_sockets if sock != cs
            ]
            print(f"Connection at {ca} closed.")
    

    def send(self, address, data):
        data_s = pickle.dumps(data)
        for sock, addr in self.C_sockets:
            if addr == address:
                try:
                    sock.sendall(data_s)
                except Exception as e:
                    warnings.warn(f"Failed to send to {address}: {e}")
                break

    def broadcast(self, data):
        data_s = pickle.dumps(data)
        for sock, addr in self.C_sockets:
            try:
                sock.sendall(data_s)
            except Exception as e:
                warnings.warn(f"Error broadcasting to {addr}: {e}")


class Client:
    def __init__(self, host: str, port: int,max_data_receive:int,on_receive=None):
        self.client_socket = socket.socket(socket.AF_INET, TCP)
        self.on_receive=on_receive
        self.client_socket.connect((host, port))
        self.max_data_receive=max_data_receive
        print(f"Connected to server at {host}:{port}")

    def send(self, data):
        data_s = pickle.dumps(data)
        self.client_socket.sendall(data_s)

    def receive(self):
        try:
            while True:
                data = pickle.loads(self.client_socket.recv(self.max_data_receive))
                if self.on_receive:
                    self.on_receive(data)
                if not data:
                    break
                obj = pickle.loads(data)
                print("Received from server:", obj)
        except Exception as e:
            print(f"Receive error: {e}")
