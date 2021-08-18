import time
import hashlib

class Transaction: 
    def __init__(self,sender,receiver,amounts,fee,message,community):
        self.sender = sender 
        self.receiver = receiver 
        self.amounts = amounts 
        self.fee = fee 
        self.message = message 
        self.community = community


    #  # test method
    # def test(self):
    #     print(f"Sender:{self.sender}\nReceiver:{self.receiver}\nAmounts:{self.amounts}\nFee:{self.fee}\nMessage:{self.message}")

class Block: 
    def __init__(self,previous_hash,node):
        self.previous_hash = previous_hash #next block hash
        self.hash = '' #this block hash
        self.difficulty = 2 
        self.nonce = 0 #key
        self.timestamp = int(time.time()) 
        self.transactions = [] 
        self.node = node

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
        return h



class BlockChain: 
    def __init__(self):
        self.difficultly = 2 
        self.block_limitation = 32 
        self.chain = [] #All block store in blockchain now
        self.pending_transactions = [] #transactions pool


# Firsttrans = Transaction("father", "son",10000,15,"生活費")
# Firsttrans.test()  #執行結果 
test= Block('hash', 'node')
test.get_hash()