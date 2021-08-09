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
        self.main_node = self.find_all_node() # IP, Port_number, State
    
    # find all node data from db
    # return list of dict of the data
    def find_all_node(self):
        cursor = self.col_main_node.find({})
        data = list([])
        for d in cursor:
            tmp = {'IP': d['IP'], 'Port_number': int(d['port']), 'State': True}
            data.append(tmp)
        if data != list([]): return data
        else: return None

    # insert node data to db
    def insert_node(self, ip, port):
        data = {'IP': ip, 'port': int(port)}
        self.col_main_node.insert_one(data)
    
    # get one free main node
    # return the index of the node's list
    def get_free_node(self):
        final_data = None
        index = 0
        for n in self.main_node:
            if n['State']:
                n['State'] = False
                final_data = index
                break
            else:
                index += 1
        return final_data

    # get this node's index
    # return int of the node's index
    def get_node_index(self, ip, port):
        final_data = None
        index = 0
        for n in self.main_node:
            if n['IP'] == ip and n['Port_number'] == port:
                final_data = index
                break
            else:
                index += 1
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
                    # get work_node loc
                    while(True):
                        node_index = self.get_free_node()
                        if node_index != None: break
                    # send work_node to ask_node
                    response = {"IP": self.main_node[node_index]['IP'], "Port_number": self.main_node[node_index]['Port_number']}
                    self.main_node[node_index]['State'] = True
                    connection.send(pickle.dumps(response))

                elif parsed_message["identity"] == "user" and parsed_message["request"] == "transaction":
                    # get work_node loc
                    while(True):
                        node_index = self.get_free_node()
                        if node_index != None: break
                    # send work_node to ask_node
                    response = {"IP": self.main_node[node_index]['IP'], "Port_number": self.main_node[node_index]['Port_number']}
                    self.main_node[node_index]['State'] = True
                    connection.send(pickle.dumps(response))

                elif parsed_message["identity"] == "node" and parsed_message["request"] == "synchronize_chain":
                    # get work_node loc
                    node_index = self.get_free_node()
                    while(True):
                        node_index = self.get_free_node()
                        if node_index != None: break
                    # send work_node to new_node
                    response = {"IP": self.main_node[node_index]['IP'], "Port_number": self.main_node[node_index]['Port_number']}
                    self.main_node[node_index]['State'] = True
                    connection.send(pickle.dumps(response))
                    # receive new_node loc
                    message = connection.recv(1024)
                    try:
                        parsed_message = pickle.loads(message)
                    except Exception:
                        print(f"{message} cannot be parsed")
                    print(f"[*] Received: {parsed_message}")
                    # store the new_node's loc
                    new_ip = parsed_message['IP']
                    new_port = int(parsed_message['Port_number'])
                    self.insert_node(new_ip, new_port)
                    new_node = {'IP': new_ip, 'Port_number': new_port, 'State': True}
                    self.main_node.append(new_node)

                elif parsed_message["identity"] == "node" and parsed_message["request"] == "done":
                    # receive done_node loc
                    message = connection.recv(1024)
                    try:
                        parsed_message = pickle.loads(message)
                    except Exception:
                        print(f"{message} cannot be parsed")
                    print(f"[*] Received: {parsed_message}")
                    done_ip = parsed_message['IP']
                    done_port = int(parsed_message['Port_number'])
                    done_index = self.get_node_index(done_ip, done_port)
                    # set done_node's state to free and to the end
                    self.main_node[done_index]['State'] = False
                    self.main_node.append(self.main_node[done_index])
                    self.main_node.remove(self.main_node[done_index])

if __name__ == "__main__":
    server = IPServer()