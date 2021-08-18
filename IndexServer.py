import sys
import socket
import threading
import time
import pickle
import pandas as pd
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
        self.socket_port = int(sys.argv[1])
        self.target_host = ''
        self.target_port = int(0)
        self.start_socket_server()
        self.main_node = self.find_all_node() # IP, Port_number, State(0: free, 1: busy, 2: blocking)
        self.print_mainnode()
    
    # find all node data from db
    # return list of dict of the data
    def find_all_node(self):
        cursor = self.col_main_node.find({})
        data = list([])
        for d in cursor:
            tmp = {'IP': d['IP'], 'Port_number': int(d['port']), 'State': int(0)}
            data.append(tmp)
        return data

    # insert node data to db
    def insert_node(self, ip, port, state):
        data = {'IP': ip, 'port': int(port)}
        self.col_main_node.insert_one(data)
        new_node = {'IP': ip, 'Port_number': int(port), 'State': int(state)}
        self.main_node.append(new_node)
    
    # get one free main node
    # return the index of the node's list or -1
    def get_free_node(self):
        final_data = None
        if len(self.main_node) != 0:
            index = 0
            for n in self.main_node:
                if n['State'] == 0:
                    final_data = index
                    break
                else:
                    index += 1
            return final_data
        elif len(self.main_node) == 0:
            return -1

    # get the blocking main node
    # return the index of the node's list
    def get_block_node(self):
        final_data = None
        index = 0
        for n in self.main_node:
            if n['State'] == 2:
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

    def print_mainnode(self):
        node_df = pd.DataFrame(self.main_node, index=None)
        print(node_df)

    def start_socket_server(self):
        t = threading.Thread(target=self.wait_for_socket_connection)
        t.start()

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
                    # send work_node loc to ask_node
                    response = {"IP": self.main_node[node_index]['IP'], "Port_number": self.main_node[node_index]['Port_number']}
                    self.main_node[node_index]['State'] = 1
                    connection.send(pickle.dumps(response))
                    self.print_mainnode()

                elif parsed_message["identity"] == "user" and parsed_message["request"] == "transaction":
                    # get work_node loc
                    while(True):
                        node_index = self.get_block_node()
                        if node_index != None: break
                    # send work_node loc to ask_node
                    response = {"IP": self.main_node[node_index]['IP'], "Port_number": self.main_node[node_index]['Port_number']}
                    connection.send(pickle.dumps(response))
                    self.print_mainnode()

                elif parsed_message["identity"] == "node" and parsed_message["request"] == "synchronize_chain":
                    # get work_node loc
                    node_index = self.get_free_node()
                    while(True):
                        node_index = self.get_free_node()
                        if node_index != None: break
                    # send work_node loc to new_node
                    if node_index != -1:
                        response = {"IP": self.main_node[node_index]['IP'], "Port_number": self.main_node[node_index]['Port_number']}
                        self.main_node[node_index]['State'] = 1
                        connection.send(pickle.dumps(response))
                    elif node_index == -1:
                        response = {"IP": -1, "Port_number": -1}
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
                    if node_index != -1: 
                        new_state = 1
                    elif node_index == -1:
                        new_state = 2
                    self.insert_node(new_ip, new_port, new_state)
                    self.print_mainnode()

                elif parsed_message["identity"] == "node" and parsed_message["request"] == "done_normal":
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
                    self.main_node[done_index]['State'] = 0
                    self.main_node.append(self.main_node[done_index])
                    self.main_node.remove(self.main_node[done_index])

                elif parsed_message["identity"] == "node" and parsed_message["request"] == "done_block":
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
                    # set done_node's state to busy
                    self.main_node[done_index]['State'] = 1
                    # get next_node loc
                    while(True):
                        next_index = self.get_free_node()
                        if next_index != None: break
                    # send next_node loc to done_node
                    response = {"IP": self.main_node[next_index]['IP'], "Port_number": self.main_node[next_index]['Port_number']}
                    self.main_node[next_index]['State'] = 2
                    connection.send(pickle.dumps(response))

if __name__ == "__main__":
    server = IPServer()