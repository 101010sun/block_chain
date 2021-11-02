import time
import hashlib
import rsa
import cryptocode

class Block: 
    def __init__(self,previous_hash,node):
        self.previous_hash = previous_hash #next block hash
        self.hash = '' # this block hash
        self.difficulty = 5
        self.nonce = 0 #key
        self.timestamp = int(time.time()) 
        self.transactions = [] 
        self.node = node

    # 添加(除建構子和交易外的)資訊填入
    def add_other_info(self, hash, nonce, timestamp):
        self.hash = hash
        self.nonce = nonce
        self.timestamp = timestamp

    # 添加交易資訊填入
    def add_transaction(self, transaction):
        self.transactions.append(transaction)

    # 打包區塊資訊成一dict(除交易)
    def pack_block_to_dict(self):
        tmp_dict = {
            'previous_hash': self.previous_hash,
            'hash': self.hash,
            'nonce': self.nonce,
            'timestamp': self.timestamp,
            'transactions_len': len(self.transactions),
            'node': self.node
            }
        return tmp_dict

    # 將交易明細轉換成字串(dict)
    def transaction_to_string(self, transaction): #transaction to string
        transaction_dict = {
            'sender': str(transaction.sender),
            'receiver': str(transaction.sender),
            'amounts': transaction.amounts,
            'fee': transaction.fee,
            'message': transaction.message
        }
        return str(transaction_dict)

    # 把區塊紀錄內的所有交易明細轉換成一個字串
    def get_transaction_string(self): #take all transaction from block turn to string 
        transaction_str = ''
        for transaction in self.transactions:
            transaction_str += self.transaction_to_string(transaction) #transaction_str = transaction_str + self.transaction_to_string(transaction)
        return transaction_str 
    
    # 依據資料產生相對應的雜湊值
    def get_hash(self):
        s = hashlib.sha256()
        s.update(
            (
                self.previous_hash 
                + str(self.timestamp) #When block produce
                + str(self.get_transaction_string()) #all transaction from block
                + str(self.nonce) #mining nonce
            ).encode("utf-8")
        ) #Update hash SHA256
        h = s.hexdigest() #get hash
        self.hash = h
        return h