import sys
import socket
import threading
import time
import pickle
import Blockchain

class Node:
    def __init__(self):
        self.Index_host = '127.0.0.1'
        self.Index_port = int(sys.argv[1])
        self.socket_host = "127.0.0.1"
        self.socket_port = int(sys.argv[2])
        self.target_host = ""
        self.target_port = int(0)

        self.blocking = False
        self.block_count = int(0)

        self.blockchain = Blockchain.BlockChain()

        self.start_socket_server()

    def start_socket_server(self):
        con_index_syn = threading.Thread(target=self.connect_to_index('synchronize_chain'))
        con_index_syn.start()
        con_index_syn.join()

        if self.target_host == '-1' and self.target_port == -1:
            self.blockchain.create_genesis_block(self.socket_host) # 產生創式塊
            self.blocking = True
            start_blocking = threading.Thread(target=self.produce_block()) # 開始產生新區塊
            start_blocking.start()
            start_blocking.join()
        elif self.target_host != '-1' and self.target_port != -1:
            con_main_syn = threading.Thread(target=self.connect_to_main_node('synchronize_chain'))
            con_main_syn.start()
            con_main_syn.join()
            time.sleep(0.5)
            con_index_donormal = threading.Thread(target=self.connect_to_index('done_first_syn'))
            con_index_donormal.start()
            con_index_donormal.join()

        t = threading.Thread(target=self.wait_for_socket_connection)
        t.start()

    def connect_to_index(self, request):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.Index_host, self.Index_port))
            # 發送身分、請求
            message = {"identity": "node", "request": request}
            s.send(pickle.dumps(message))

            if request == 'synchronize_chain':
                response = s.recv(4096)
                if response:
                    try:
                        parsed_message = pickle.loads(response)
                    except Exception:
                        print(f"{message} cannot be parsed")
                    self.target_host = str(parsed_message['IP'])
                    self.target_port = int(parsed_message['Port_number'])
                    print("[*] target_host: ", end="")
                    print(self.target_host)
                    print("[*] target_port: ", end="")
                    print(self.target_port)
                # 傳送自己的節點IP、Port number
                message = {"IP": self.socket_host, "Port_number": self.socket_port}
                s.send(pickle.dumps(message))

            elif request == 'done_normal':
                time.sleep(0.5)
                # 傳送自己的節點IP、Port number
                message = {"IP": self.socket_host, "Port_number": self.socket_port}
                s.send(pickle.dumps(message))

            elif request == 'done_block':
                time.sleep(0.5)
                # 傳送自己的節點IP、Port number
                message = {"IP": self.socket_host, "Port_number": self.socket_port}
                s.send(pickle.dumps(message))
                # 告知另一主節點 接任blocking
                response = s.recv(4096)
                if response:
                    try:
                        parsed_message = pickle.loads(response)
                    except Exception:
                        print(f"{message} cannot be parsed")
                    self.target_host = str(parsed_message['IP'])
                    self.target_port = int(parsed_message['Port_number'])
                    print("[*] target_host: ", end="")
                    print(self.target_host)
                    print("[*] target_port: ", end="")
                    print(self.target_port)
                con_node_doblock = threading.Thread(target=self.connect_to_main_node('you_block'))
                con_node_doblock.start()
                con_node_doblock.join()

                con_index_donormal = threading.Thread(target=self.connect_to_index('done_normal'))
                con_index_donormal.start()
                con_index_donormal.join()

            elif request == 'done_first_syn':
                time.sleep(0.5)
                # 傳送自己的節點IP、Port number
                message = {"IP": self.socket_host, "Port_number": self.socket_port}
                s.send(pickle.dumps(message))

            s.shutdown(2)
            s.close()

    def connect_to_main_node(self, request):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.target_host, self.target_port))
            # 發送身分、請求
            message = {"identity": "node", "request": request}
            s.send(pickle.dumps(message))

            if request == 'synchronize_chain':
                while(True):
                    response = s.recv(4096)
                    if response:
                        try:
                            parsed_message = pickle.loads(response)
                            print(parsed_message)
                        except Exception:
                            print(f"{message} cannot be parsed")
                        
                    if parsed_message['result'] == 'finish':
                        break
                    elif parsed_message['result'] == 'not_yet':
                        a_block = Blockchain.Block(parsed_message['previous_hash'], parsed_message['node'])
                        a_block.add_other_info(parsed_message['hash'], parsed_message['nonce'], parsed_message['timestamp'])
                        for i in range(0, parsed_message['transactions_len']):
                            response = s.recv(4096)
                            if response:
                                try:
                                    parsed_message = pickle.loads(response)
                                    print(parsed_message)
                                except Exception:
                                    print(f"{message} cannot be parsed")
                            a_transaction = Blockchain.Transaction(parsed_message['sender'], parsed_message['receiver'], parsed_message['amounts'], parsed_message['msg'], parsed_message['community'])
                            a_block.add_transaction(a_transaction)
                        self.blockchain.chain.append(a_block)
            
            else:
                # waiting for the response
                response = s.recv(4096)
                if response:
                    try:
                        parsed_message = pickle.loads(response)
                    except Exception:
                        print(f"{message} cannot be parsed")
                    print(parsed_message)
            
            s.shutdown(2)
            s.close()

    def wait_for_socket_connection(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.socket_host, self.socket_port))
            s.listen()
            while True:
                conn, address = s.accept()
                client_handler = threading.Thread(target=self.receive_socket_message, args=(s, conn, address))
                client_handler.start()
                client_handler.join()

    def receive_socket_message(self, s, connection ,address):
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
                    message = connection.recv(1024)
                    try:
                        parsed_message = pickle.loads(message)
                    except Exception:
                        print(f"{message} cannot be parsed")
                    print(f"[*] Received: {parsed_message}")

                    balance = self.blockchain.get_balance(parsed_message['account']) # 計算帳戶餘額
                    response = {'result': balance}
                    connection.send(pickle.dumps(response))

                    con_index_done = threading.Thread(target=self.connect_to_index('done_normal'))
                    con_index_done.start()
                    con_index_done.join()
                
                elif parsed_message["identity"] == "user" and parsed_message["request"] == "transaction":
                    message = connection.recv(1024)
                    try:
                        parsed_message = pickle.loads(message)
                    except Exception:
                        print(f"{message} cannot be parsed")
                    print(f"[*] Received: {parsed_message}")
                    if self.block_count:
                        transaction = Blockchain.Transaction(parsed_message['sender'], parsed_message['receiver'], parsed_message['amounts'], parsed_message['msg'], parsed_message['community'])
                        self.blockchain.add_transaction_to_pool(transaction)
                        response = {'result': 'success'}
                    else:
                        response = {'result': 'not me'}
                    connection.send(pickle.dumps(response))

                elif parsed_message["identity"] == "node" and parsed_message["request"] == "synchronize_chain":
                    if self.blockchain.chain != []:
                        for b in self.blockchain.chain: # 傳送整個鏈資料
                            a_block_dict = b.pack_block_to_dict()
                            a_block_dict['result'] = 'not_yet'
                            connection.send(pickle.dumps(a_block_dict))
                            time.sleep(0.5)
                            for t in b.transactions:
                                a_transaction_dict = t.pack_transaction_to_dict()
                                connection.send(pickle.dumps(a_transaction_dict))
                                time.sleep(0.5)
                                
                    response = {'result': 'finish'}
                    connection.send(pickle.dumps(response))

                    con_index_done = threading.Thread(target=self.connect_to_index('done_normal'))
                    con_index_done.start()
                    con_index_done.join()
                
                elif parsed_message["identity"] == "node" and parsed_message["request"] == "you_block":
                    self.block_count = 0
                    self.blocking = True
                    start_blocking = threading.Thread(target=self.produce_block()) # 開始產生新區塊
                    start_blocking.start()
                    start_blocking.join()

    def produce_block(self):
        while(self.blocking):
            self.blockchain.node_block(self.Index_host)
            # --傳送這個block資料到所有主節點並進行驗證
            self.block_count += 1
            if self.block_count == 5:
                self.blocking = False
                self.block_count = 0
                con_index_doneb = threading.Thread(target=self.connect_to_index('done_block'))
                con_index_doneb.start()
                con_index_doneb.join()

if __name__ == "__main__":
    server = Node()