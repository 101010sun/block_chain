import sys
import socket
import threading
import time
import pickle

class Node:
    def __init__(self):
        # for P2P connection
        self.socket_host = "127.0.0.1"
        self.socket_port = int(1117)
        self.start_socket_server()
        self.community_host = []
        self.community_port = []

    # open thread
    def start_socket_server(self):
        t = threading.Thread(target=self.wait_for_socket_connection)
        t.start()

    # waiting for the connection by keeping listening
    def wait_for_socket_connection(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.socket_host, self.socket_port))
            s.listen()
            while True:
                # accept this connection
                conn, address = s.accept()
                # open one thread to handle the mission
                client_handler = threading.Thread(target=self.receive_socket_message, args=(conn, address))
                client_handler.start()
    
    # messages receiving from server handle
    def receive_socket_message(self, connection ,address):
        with connection:
            print(f'Connected by: {address}')
            while True:
                message = connection.recv(1024)
                print(f"[*] Received: {message}")
                # try:
                #     parsed_message = pickle.loads(message)
                # except Exception:
                #     print(f'{message} cannot be parsed')

    # start the node
    def start(self):
        print('start!')

if __name__ == "__main__":
    IPserver_host = '127.0.0.1'
    IPserver_port = int(sys.argv[1])

    target_host = ""
    target_port = int(0)
    community_host = []
    community_port = []

    # build the connection with IPserver
    IPclient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    IPclient.connect((IPserver_host, IPserver_port))

    # send the identity and request msg. to IPserver
    message = {"identity": "node", "request": "synchronize_chain"}
    IPclient.send(pickle.dumps(message))
    # waiting for the IPserver response
    response = IPclient.recv(4096)
    if response:
        try:
            parsed_message = pickle.loads(response)
        except Exception:
            print(f"{message} cannot be parsed")

        # print(f"[*] Message from node: {parsed_message}")
        target_host = parsed_message['IP']
        target_port = parsed_message['Port_number']
        print("[*] target_host: " + target_host)
        print("[*] target_port: " + target_port)

    # send self ip and port number msg. to IPserver
    message = {"IP": "127.0.0.1", "Port_number": int(1117)}
    IPclient.send(pickle.dumps(message))
    # waiting for the IPserver response
    response = IPclient.recv(4096)
    if response:
        try:
            parsed_message = pickle.loads(response)
        except Exception:
            print(f"{message} cannot be parsed")

        # print(f"[*] Message from node: {parsed_message}")
        community_host = parsed_message['IP']
        community_port = parsed_message['Port_number']
        print("[*] community_host: ", end="")
        print(community_host)
        print("[*] community_port: ", end="")
        print(community_port)

    IPclient.shutdown(2)
    IPclient.close()
    print('connection to IPserver close')
    
    # --start for node's jobs--
    # server = Node()