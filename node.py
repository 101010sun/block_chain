import sys
import socket
import threading
import time
import pickle

class Node:
    def __init__(self):
        # for P2P connection
        self.IPserver_host = '127.0.0.1'
        self.IPserver_port = int(sys.argv[1])
        self.socket_host = "127.0.0.1"
        self.socket_port = int(sys.argv[2])
        self.target_host = ""
        self.target_port = int(0)

        self.init_self()
        # self.start_socket_server()
    
    def init_self(self):
        # build the connection with IPserver
        IPclient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        IPclient.connect((self.IPserver_host, self.IPserver_port))
        # 發送身分、請求
        message = {"identity": "node", "request": "synchronize_chain"}
        IPclient.send(pickle.dumps(message))
        # waiting for the IPserver response
        response = IPclient.recv(4096)
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
        IPclient.send(pickle.dumps(message))
        IPclient.shutdown(2)
        IPclient.close()
        print('connection to IPserver close')
        
        if self.target_host == '-1' and self.IPserver_port == -1:
            # --產生創式塊
            # --產生新區塊工作
            print('produce new block!')
        elif self.target_host != '-1' and self.IPserver_port != -1:
            # --聯繫其他區塊同步資料
            print('connect to another main node!')

    def start_socket_server(self):
        t = threading.Thread(target=self.wait_for_socket_connection)
        t.start()

    def wait_for_socket_connection(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.socket_host, self.socket_port))
            s.listen()
            while True:
                conn, address = s.accept()
                client_handler = threading.Thread(target=self.receive_socket_message, args=(s, conn, address))
                client_handler.start()
                client_handler.join()
                print(f'end {address} thread')
    
    def finish_normal_job(self, s):
        message = {}
        indexclient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        indexclient.connect((self.IPserver_host, self.IPserver_port))
        indexclient.send(pickle.dumps(message))
        
        response = indexclient.recv(4096)
        if response:
            try:
                parsed_message = pickle.loads(response)
            except Exception:
                print(f"{message} cannot be parsed")
            target_host = parsed_message['IP']
            target_port = int(parsed_message['Port_number'])
            tmp = {'IP': target_host, 'Port_number': target_port}
            indexclient.shutdown(2)
            indexclient.close()
            print('[*] ',end='')
            print(tmp)
            print('connection close')
            # --聯絡此target節點，跟節點說要查詢，並取得錢包總額資料

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
                
                elif parsed_message["identity"] == "user" and parsed_message["request"] == "transaction":
                    # --發布交易
                    response = {'result': 'success'}
                    connection.send(pickle.dumps(response))

                elif parsed_message["identity"] == "node" and parsed_message["request"] == "synchronize_chain":
                    # --傳送整個鏈資料
                    response = {'result': 'success'}
                    connection.send(pickle.dumps(response))

if __name__ == "__main__":
    server = Node()