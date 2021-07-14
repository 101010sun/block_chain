import time
class Transaction: 
    def __init__(self,sender,receiver,amounts,fee,message):
        self.sender = sender 
        self.receiver = receiver 
        self.amounts = amounts 
        self.fee = fee 
        self.message = message 

    """ # 方法(Method)
    def test(self):
        print(f"Sender:{self.sender}\nReceiver:{self.receiver}\nAmounts:{self.amounts}\nFee:{self.fee}\nMessage:{self.message}")

Firsttrans = Transaction("father", "son",10000,15,"生活費")
Firsttrans.test()  #執行結果 """

class Block: 
    def __init__(self,previous_hash,miner):
        self.previous_hash = previous_hash #next block hash
        self.hash = '' #this block hash
        self.difficulty = 2 
        self.nonce = 0 #key
        self.timestamp = int(time.time()) 
        self.transactions = [] 
        self.miner = miner 

class BlockChain: 
    def __init__(self):
        self.difficultly = 2 
        self.block_limitation = 32 
        self.chain = [] #All block store in blockchain now
        self.pending_transactions = [] #transactions pool