import sys
import socket
import threading
import time
import pickle
from pymongo import MongoClient
from bson.objectid import ObjectId

class IPServer:
    def __init__(self):
        # for DB connection
        self.conn = MongoClient()
        self.db = self.conn.blackchainIP
        self.col_main_node = self.db.main_node
        self.col_main_node.stats
        # for P2P connection
        self.socket_host = "127.0.0.1"
        self.socket_port = int(1111)
        self.target_host = ''
        self.target_port = int(0)
        self.start_socket_server()
        self.main_node = self.find_all_node()
    
    # find all node data from db
    def find_all_node(self):
        cursor = self.col_main_node.find({})
        data = list([])
        for d in cursor:
            tmp = {'IP': d['IP'], 'port': d['port'], 'state': True}
            data.append(tmp)
        if data != list([]): return data
        else: return None

    # get one free main node
    def get_free_node(self):
        final_data = dict({})
        for n in self.main_node:
            if n['state']:
                n['state'] = False
                final_data = n
        return final_data

    # open thread to waiting for the connection
    def start_socket_server(self):
        t = threading.Thread(target=self.wait_for_socket_connection)
        t.start()

    # keeping listening and open thread to handle receive msg.
    def wait_for_socket_connection(self):
        with socket.socket(
            socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.socket_host, self.socket_port))
            s.listen()
            while True:
                conn, address = s.accept()
                client_handler = threading.Thread(target=self.receive_socket_message, args=(conn, address))
                client_handler.start()
                client_handler.join()
                print(f'end {address} thread')

    # messages receiving from server handle
    def receive_socket_message(self, connection ,address):
        with connection:
            print(f'Connected by: {address}')
            message = connection.recv(1024)
            try:
                parsed_message = pickle.loads(message)
            except Exception:
                print(f"{message} cannot be parsed")
            print(f"[*] Received: {parsed_message}")
            if message:
                if parsed_message["identity"] == "user" and parsed_message["request"] == "get_balance":
                    # --find node's IP and Port number--
                    response = {"IP": "127.0.0.1", "Port_number": "1112"}
                    connection.send(pickle.dumps(response))

                elif parsed_message["identity"] == "user" and parsed_message["request"] == "transaction":
                    # --find all community nodes' IP and Port number--
                    response = {"IP": ["127.0.0.1", "127.0.0.1", "127.0.0.1"], "Port_number": ["1112", "1113", "1114"]}
                    connection.send(pickle.dumps(response))

                elif parsed_message["identity"] == "node" and parsed_message["request"] == "synchronize_chain":
                    # --find node's IP and Port number--
                    response = {"IP": "127.0.0.1", "Port_number": "1112"}
                    connection.send(pickle.dumps(response))

                    message = connection.recv(1024)
                    try:
                        parsed_message = pickle.loads(message)
                    except Exception:
                        print(f"{message} cannot be parsed")
                    print(f"[*] Received: {parsed_message}")
                    
                    # store the new node's ip and port number
                    self.target_port = parsed_message['IP']
                    self.target_host = int(parsed_message['Port_number'])

                    # --find all community nodes' IP and Port number--
                    response = {"IP": ["127.0.0.1", "127.0.0.1", "127.0.0.1"], "Port_number": ["1112", "1113", "1114"]}
                    connection.send(pickle.dumps(response))

                    # --broadcast the new node's ip and port number to every nodes in the same community--


if __name__ == "__main__":
    server = IPServer()