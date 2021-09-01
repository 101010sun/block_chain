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
        self.blocking_host = ''
        self.blocking_port = int(0)

        self.index_flag = 0
        self.main_node = self.find_all_node() # IP, Port_number, Work

        self.start_socket_server()
        self.print_mainnode()
    
    # find all node data from db
    # return list of dict of the data
    def find_all_node(self):
        cursor = self.col_main_node.find({})
        data = list([])
        for d in cursor:
            tmp = {'IP': d['IP'], 'Port_number': int(d['port']), 'Work': int(0)}
            data.append(tmp)
        return data

    # insert node data to db
    def insert_node(self, ip, port):
        data = {'IP': ip, 'port': int(port)}
        self.col_main_node.insert_one(data)
        new_node = {'IP': ip, 'Port_number': int(port), 'Work': int(0)}
        self.main_node.append(new_node)
    
    # get one free main node
    # return the free ip and port, or -1
    def get_free_node(self, work):
        final_data = None
        if len(self.main_node) != 0:
            self.main_node = sorted(self.main_node, key=lambda k: k['Work'])
            final_data = {'IP': self.main_node[0]['IP'], 'Port_number': self.main_node[0]['Port_number']}
            if self.main_node[0]['Work'] >= 5 :
                return None
            else:
                self.main_node[0]['Work'] += int(work)
                return final_data
        elif len(self.main_node) == 0:
            final_data = {'IP': -1, 'Port_number': -1}
            return -1

    # get the blocking main node
    # return the dict of node ip and port
    def get_block_node(self):
        final_data = {'IP': self.blocking_host, 'Port_number': self.blocking_port}
        return final_data

    def set_work_done(self, ip, port, work):
        for n in self.main_node:
            if n['IP'] == str(ip) and n['Port_number'] == int(port):
                n['Work'] -= int(work)
                break

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
                        node_dict = self.get_free_node(1)
                        if node_dict != None and node_dict['IP'] != -1: break
                    # send work_node loc to ask_node
                    response = {"IP": node_dict['IP'], "Port_number": node_dict['Port_number']}
                    connection.send(pickle.dumps(response))
                    self.print_mainnode()

                elif parsed_message["identity"] == "user" and parsed_message["request"] == "transaction":
                    # get work_node loc
                    while(True):
                        node_dict = self.get_block_node()
                        if node_dict != None: break
                    # send work_node loc to ask_node
                    response = {"IP": node_dict['IP'], "Port_number": node_dict['Port_number']}
                    connection.send(pickle.dumps(response))
                    self.print_mainnode()

                elif parsed_message["identity"] == "node" and parsed_message["request"] == "synchronize_chain":
                    # get work_node loc
                    while(True):
                        node_dict = self.get_free_node(1)
                        if node_dict != None: break
                    # send work_node loc to new_node
                    if node_dict['IP'] != -1:
                        response = {"IP": node_dict['IP'], "Port_number": node_dict['Port_number']}
                        connection.send(pickle.dumps(response))
                    elif node_dict['IP'] == -1:
                        response = node_dict
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
                    work = int(0)
                    if node_dict['IP'] == -1:
                        self.blocking_host = new_ip
                        self.blocking_port = new_port
                        work = 3
                    self.insert_node(new_ip, new_port, work)
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
                    self.set_work_done(done_ip, done_port, 1)

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
                    self.set_work_done(done_ip, done_port, 2) # set done_node to free and do normal job, - 3 + 1 = - 2
                    # get next_node loc
                    while(True):
                        next_dict = self.get_free_node(3)
                        if next_dict != None and next_dict['IP'] != -1: break
                    # send next_node loc to done_node
                    response = {"IP": next_dict['IP'], "Port_number": next_dict['Port_number']}
                    self.blocking_host = next_dict['IP']
                    self.blocking_port = next_dict['Port_number']
                    connection.send(pickle.dumps(response))

if __name__ == "__main__":
    server = IPServer()