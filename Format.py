import time
#格式函式
class Transaction: #交易明細格式
    #建構式
    def __init__(self,sender,receiver,amounts,fee,message):
        self.sender = sender #發送方
        self.receiver = receiver #收款方
        self.amounts = amounts #金額大小
        self.fee = fee #手續費
        self.message = message #訊息

    """ # 方法(Method)
    def test(self):
        print(f"Sender:{self.sender}\nReceiver:{self.receiver}\nAmounts:{self.amounts}\nFee:{self.fee}\nMessage:{self.message}")

Firsttrans = Transaction("father", "son",10000,15,"生活費")
Firsttrans.test()  #執行結果 """

class Block: #區塊格式
    def __init__(self,previous_hash,miner):
        self.previous_hash = previous_hash #前個區塊hash值
        self.hash = '' #此次區塊hash值
        self.difficulty = 2 #當前難度
        self.nonce = 0 #key
        self.timestamp = int(time.time()) #區塊產生時間戳
        self.transactions = [] #交易紀錄
        self.miner = miner #礦工

class BlockChain: #區塊鏈架構
    def __init__(self):
        self.difficultly = 2 #目前難度
        self.block_limitation = 32 #區塊容量
        self.chain = [] #目前區塊鏈中儲存的所有區塊
        self.pending_transactions = [] #等待中的交易 