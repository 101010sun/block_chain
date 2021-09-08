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

        self.done_list = list([])

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

                self.blocking = False
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
                while True:
                    if len(self.done_list) != 0:
                        done = self.done_list.pop(0)
                        con_index_done = threading.Thread(target=self.connect_to_index(done))
                        con_index_done.start()
                        con_index_done.join()
                    else:
                        break

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
                    # --計算帳戶餘額
                    response = {'result': '帳戶餘額結果'}
                    connection.send(pickle.dumps(response))

                    self.done_list.append('done_normal')
                
                elif parsed_message["identity"] == "user" and parsed_message["request"] == "transaction":
                    # --發布交易
                    response = {'result': 'success'}
                    connection.send(pickle.dumps(response))

                elif parsed_message["identity"] == "node" and parsed_message["request"] == "synchronize_chain":
                    # --傳送整個鏈資料
                    response = {'result': 'success'}
                    connection.send(pickle.dumps(response))

                    self.done_list.append('done_normal')
                
                elif parsed_message["identity"] == "node" and parsed_message["request"] == "you_block":
                    self.block_count = 0
                    self.blocking = True
                    # --開始產生新區塊工作

    def produce_block(self):
        if self.blocking:
            self.blockchain.node_block(self.Index_host)
            self.block_count += 1
            # --傳送這個block資料到所有主節點並進行驗證

if __name__ == "__main__":
    server = Node()