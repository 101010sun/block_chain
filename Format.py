import time
#格式函式
class Transaction: #交易格式
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
    def __init__(self,previous_hash,difficultly,miner,miner_rewards):
        self.previous_hash = previous_hash #前個區塊hash值
        self.hash = '' #此次區塊hash值
        self.difficultly = difficultly #當前難度
        self.nonce = 0 #key
        self.timestamp = int(time.time()) #區塊產生時間戳
        self.transactions = [] #交易紀錄
        self.miner = miner #礦工

class BlockChain: #區塊鏈架構
    def __init__(self):
        self.adjust_difficultly_blocks = 10 #多少個區塊調節一次難度
        self.difficultly = 1 #目前難度
        self.blocks_time = 30 #出塊時間
        self.block_limitation = 32 #區塊容量
        self.chain = [] #目前區塊鏈中儲存的所有區塊
        self.pending_transactions = [] #等待中的交易
    