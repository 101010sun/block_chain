import sys
import socket
import threading
import time
import pickle
from Blockchain import block, blockchain, record, transaction
from Model import getData

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
        self.main_node_list = list([])
        self.blockchain = blockchain.BlockChain()

        self.start_socket_server()
    
    # 啟動func.
    def start_socket_server(self):
        con_index_syn = threading.Thread(target=self.connect_to_index, args=('synchronize_chain',)) # 告知索引伺服器需同步資料
        con_index_syn.start()
        con_index_syn.join() # 等待同步執行結束

        if self.target_host == '-1' and self.target_port == -1:
            self.blockchain.create_genesis_block(self.socket_host) # 產生創式塊
            self.blocking = True
            start_blocking = threading.Thread(target=self.produce_block) # 開始產生新區塊
            start_blocking.start() # 執行該子執行緒
        elif self.target_host != '-1' and self.target_port != -1:
            con_main_syn = threading.Thread(target=self.connect_to_main_node, args=("synchronize_chain",)) # 與主節點聯絡並同步資料
            con_main_syn.start() 
            con_main_syn.join() # 等待同步資料執行結束
            time.sleep(0.5)
            con_index_donormal = threading.Thread(target=self.connect_to_index, args=("done_hard",)) # 告知索引伺服器同步資料完成
            con_index_donormal.start()

        t = threading.Thread(target=self.wait_for_socket_connection) # 開始監聽
        t.start()

    # 聯絡索引伺服器func.
    def connect_to_index(self, request):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.Index_host, self.Index_port))
            message = {"identity": "node", "request": request} # 發送身分、請求
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
                message = {"IP": self.socket_host, "Port_number": self.socket_port} # 傳送自己的節點IP、Port number
                s.send(pickle.dumps(message))

            elif request == 'done_normal':
                time.sleep(0.5)
                message = {"IP": self.socket_host, "Port_number": self.socket_port} # 傳送自己的節點IP、Port number
                s.send(pickle.dumps(message))

            elif request == 'done_block':
                time.sleep(1.5)
                message = {"IP": self.socket_host, "Port_number": self.socket_port} # 傳送自己的節點IP、Port number
                s.send(pickle.dumps(message))
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
                con_node_doblock = threading.Thread(target=self.connect_to_main_node, args=('you_block',)) # 告知另一主節點 接任blocking
                con_node_doblock.start()

                con_index_donormal = threading.Thread(target=self.connect_to_index, args=('done_normal',))
                con_index_donormal.start()

            elif request == 'done_middle':
                time.sleep(0.5)
                message = {"IP": self.socket_host, "Port_number": self.socket_port}
                s.send(pickle.dumps(message))

            elif request == 'done_hard':
                time.sleep(0.5)
                message = {"IP": self.socket_host, "Port_number": self.socket_port} # 傳送自己的節點IP、Port number
                s.send(pickle.dumps(message))

            elif request == 'broadcast_list':
                response = s.recv(4096)
                if response:
                    try:
                        parsed_message = pickle.loads(response)
                    except Exception:
                        print(f"{message} cannot be parsed")
                    length = int(parsed_message['length'])
                for i in range(0, length):
                    response = s.recv(4096)
                    if response:
                        try:
                            parsed_message = pickle.loads(response)
                        except Exception:
                            print(f"{message} cannot be parsed")
                        node_ip = str(parsed_message['IP'])
                        Port_number = int(parsed_message['Port_number'])
                        tmp = {'IP': node_ip, 'Port_number': Port_number}
                        if tmp not in self.main_node_list:
                            self.main_node_list.append({'IP': node_ip, 'Port_number': Port_number})
                   
            s.shutdown(2)
            s.close()

    # 聯絡主節點func.
    def connect_to_main_node(self, request):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.target_host, self.target_port))
            message = {"identity": "node", "request": request} # 發送身分、請求
            s.send(pickle.dumps(message))

            if request == 'synchronize_chain':
                while(True):
                    response = s.recv(4096)
                    if response:
                        try:
                            parsed_message = pickle.loads(response)
                        except Exception:
                            print(f"{message} cannot be parsed")
                        
                    if parsed_message['result'] == 'finish':
                        break
                    elif parsed_message['result'] == 'not_yet':
                        a_block = block.Block(parsed_message['previous_hash'], parsed_message['node'])
                        a_block.add_other_info(parsed_message['hash'], parsed_message['nonce'], parsed_message['timestamp'])
                        for i in range(0, parsed_message['transactions_len']):
                            response = s.recv(4096)
                            if response:
                                try:
                                    parsed_message = pickle.loads(response)
                                except Exception:
                                    print(f"{message} cannot be parsed")
                            a_transaction = transaction.Transaction(parsed_message['sender'], parsed_message['receiver'], parsed_message['amounts'], parsed_message['msg'], parsed_message['community'])
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

    # 廣播新區塊func.
    def connect_to_main_node_new_block(self, request, new_block):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.target_host, self.target_port))
            message = {"identity": "node", "request": request} # 發送身分、請求
            s.send(pickle.dumps(message))
            time.sleep(0.5)
            new_block_dict = new_block.pack_block_to_dict()
            new_block_dict['result'] = 'not_yet'
            s.send(pickle.dumps(new_block_dict))
            time.sleep(0.5)
            for t in new_block.transactions:
                a_transaction_dict = t.pack_trainsaction_to_dict()
                s.send(pickle.dumps(a_transaction_dict))
                time.sleep(0.5)
            
            response = {'result': 'finish'}
            s.send(pickle.dumps(response))

            s.shutdown(2)
            s.close()

    # 廣播新交易func.
    def connect_to_main_node_new_record(self, request, new_record):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.target_host, self.target_port))
            message = {"identity": "node", "request": request} # 發送身分、請求
            s.send(pickle.dumps(message))

            time.sleep(0.5)
            new_record_dict = new_record.pack_transaction_to_dict()
            s.send(pickle.dumps(new_record_dict))

            s.shutdown(2)
            s.close()

    # 監聽func.
    def wait_for_socket_connection(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.socket_host, self.socket_port))
            s.listen()
            while True:
                conn, address = s.accept()
                client_handler = threading.Thread(target=self.receive_socket_message, args=(s, conn, address)) # 處理收到的請求
                client_handler.start()

    # 處理請求func.
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

                    con_index_done = threading.Thread(target=self.connect_to_index, args=('done_normal',))
                    con_index_done.start()
                
                elif parsed_message["identity"] == "user" and parsed_message["request"] == "transaction":
                    message = connection.recv(1024)
                    try:
                        parsed_message = pickle.loads(message)
                    except Exception:
                        print(f"{message} cannot be parsed")
                    print(f"[*] Received: {parsed_message}")
                    if self.blocking:
                        a_transaction = self.blockchain.initialize_transaction(parsed_message['sender'], parsed_message['receiver'], parsed_message['amounts'], parsed_message['msg'], parsed_message['community'])
                        private = getData.taken_privatekey(parsed_message['account'], parsed_message['password']) # 取sender私鑰
                        signature = self.blockchain.sign_transaction(a_transaction, private) # 簽署交易
                        self.blockchain.add_transaction_to_pool(a_transaction, signature) # 將交易資料放入交易池
                        response = {'result': 'success'}
                    else:
                        response = {'result': 'sign failed!'}
                    connection.send(pickle.dumps(response))
                
                elif parsed_message['identity'] == "user" and parsed_message['request'] == 'system_transaction':
                    message = connection.recv(1024)
                    try:
                        parsed_message = pickle.loads(message)
                    except Exception:
                        print(f"{message} cannot be parsed")
                    print(f"[*] Received: {parsed_message}")
                    if self.blocking:
                        a_transaction = self.blockchain.initialize_system_transaction(parsed_message['sender'], parsed_message['receiver'], parsed_message['amounts'], parsed_message['msg'], parsed_message['community'])
                        sys_private = getData.taken_system_privatekey(parsed_message['system_password']) # 取平台私鑰
                        signature = self.blockchain.sign_transaction(a_transaction, sys_private) # 簽署交易
                        self.blockchain.add_transaction_to_pool(a_transaction, signature) # 將交易資料放入交易池
                        response = {'result': 'success'}
                    else:
                        response = {'result': 'sign failed!'}
                    connection.send(pickle.dumps(response))

                elif parsed_message["identity"] == "user" and parsed_message["request"] == "issue_money":
                    message = connection.recv(1024)
                    try:
                        parsed_message = pickle.loads(message)
                    except Exception:
                        print(f"{message} cannot be parsed")
                    print(f"[*] Received: {parsed_message}")

                    a_record = record.Record(parsed_message['currency_name'], parsed_message['currency_value'], parsed_message['circulation'], parsed_message['community'], parsed_message['timestamp'])
                    self.blockchain.add_record_to_block(a_record)

                    con_index_node_list = threading.Thread(target=self.connect_to_index, args=('broadcast_list',)) # 更新廣播清單
                    con_index_node_list.start()
                    print('[*] broadcast_list!')
                    for node_address in self.main_node_list: # 廣播
                        if (node_address['IP'] != self.socket_host) or (node_address['Port_number'] != self.socket_port):
                            self.target_host = node_address['IP']
                            self.target_port = int(node_address['Port_number'])
                            print('[*] !', self.target_host, self.target_port)
                            con_node_broad = threading.Thread(target=self.connect_to_main_node_new_record, args=('new_record', a_record,))
                            con_node_broad.start()
                    
                    con_index_done_middle = threading.Thread(target=self.connect_to_index, args=('done_middle',)) # 告知所以伺服器 done_middle
                    con_index_done_middle.start()

                elif parsed_message["identity"] == "user" and parsed_message["request"] == "get_system_balance":
                    message = connection.recv(1024)
                    try:
                        parsed_message = pickle.loads(message)
                    except Exception:
                        print(f"{message} cannot be parsed")
                    print(f"[*] Received: {parsed_message}")
                    balance = self.blockchain.get_system_balance(parsed_message['account']) # 計算帳戶餘額
                    response = {'result': balance}
                    connection.send(pickle.dumps(response))

                    con_index_done = threading.Thread(target=self.connect_to_index, args=('done_normal',))
                    con_index_done.start()

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

                    con_index_done = threading.Thread(target=self.connect_to_index, args=('done_normal',))
                    con_index_done.start()
                
                elif parsed_message["identity"] == "node" and parsed_message["request"] == "you_block":
                    self.block_count = 0
                    self.blocking = True
                    start_blocking = threading.Thread(target=self.produce_block) # 開始產生新區塊
                    start_blocking.start()
                
                elif parsed_message['identity'] == "node" and parsed_message['request'] == "new_block":
                    while(True):
                        message = connection.recv(1024)
                        try:
                            parsed_message = pickle.loads(message)
                        except Exception:
                            print(f"{message} cannot be parsed")
                        print(parsed_message)
                        if parsed_message['result'] == 'finish':
                            break
                        elif parsed_message['result'] == 'not_yet':
                            a_block = block.Block(parsed_message['previous_hash'], parsed_message['node'])
                            a_block.add_other_info(parsed_message['hash'], parsed_message['nonce'], parsed_message['timestamp'])
                            for i in range(0, parsed_message['transactions_len']):
                                response = s.recv(4096)
                                if response:
                                    try:
                                        parsed_message = pickle.loads(response)
                                        print(parsed_message)
                                    except Exception:
                                        print(f"{message} cannot be parsed")
                                a_transaction = transaction.Transaction(parsed_message['sender'], parsed_message['receiver'], parsed_message['amounts'], parsed_message['msg'], parsed_message['community'])
                                a_block.add_transaction(a_transaction)
                            self.blockchain.chain.append(a_block)
                    print(self.blockchain.chain)

                elif parsed_message['identity'] == "node" and parsed_message['request'] == "new_record":
                    message = connection.recv(1024)
                    try:
                        parsed_message = pickle.loads(message)
                    except Exception:
                        print(f"{message} cannot be parsed")
                    print(parsed_message)
                    a_record = record.Record(parsed_message['currency_name'], parsed_message['currency_value'], parsed_message['circulation'], parsed_message['community'], parsed_message['timestamp'])
                    self.blockchain.add_record_to_block(a_record)

    # 產生新區塊func.
    def produce_block(self):
        while(self.blocking):
            new_block = self.blockchain.node_block(self.Index_host) # 產生新區塊
            con_index_node_list = threading.Thread(target=self.connect_to_index, args=('broadcast_list',)) # 更新廣播清單
            con_index_node_list.start()
            print('[*] broadcast_list!')
            for node_address in self.main_node_list: # 廣播
                if (node_address['IP'] != self.socket_host) or (node_address['Port_number'] != self.socket_port):
                    self.target_host = node_address['IP']
                    self.target_port = int(node_address['Port_number'])
                    print('[*] !', self.target_host, self.target_port)
                    con_node_broad = threading.Thread(target=self.connect_to_main_node_new_block, args=('new_block', new_block,))
                    con_node_broad.start()
            self.block_count += 1
            if self.block_count == 5:
                self.blocking = False
                self.block_count = 0
        con_index_doneb = threading.Thread(target=self.connect_to_index, args=('done_block',))
        con_index_doneb.start()


if __name__ == "__main__":
    server = Node()