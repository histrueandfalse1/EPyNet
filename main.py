import socket
import os
import platform
import pickle

TCP=socket.SOCK_STREAM
UDP=socket.SOCK_DGRAM

class Server():
    def __init__(self,host:str, port:int,max_conn:int=1):

        self.C_sockets = []

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((host, port))
        self.server_socket.listen(max_conn)
        print(f"Server started on {host}:{port}")

        while True:
            client_socket, addr = self.server_socket.accept()
            print(f"Connection from {addr}")
            self.C_sockets.append(client_socket)
    
    def send(self, address):
        pass

    def broadcast(self,data):
        data_s=pickle.dumps(data)
        for sock,_ in self.C_sockets:
            try:
                sock.sendall(data_s)
            except:
                print(f"Error occured while attempting to broadcast data to client {sock}")
                continue



class Client():
    def __init__(self, host:str, port:int):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((host, port))
        print(f"Connected to server at {host}:{port}")

    def send(self, data):
        data_s=pickle.dumps(data)
        self.client_socket.sendall(data_s)

    

    