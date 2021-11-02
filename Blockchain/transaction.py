import time
import hashlib
import rsa
import cryptocode

class Transaction: 
    def __init__(self,sender,receiver,amounts,message,community):
        self.sender = sender 
        self.receiver = receiver 
        self.amounts = amounts 
        self.fee = amounts * 0.01 
        self.message = message 
        self.community = community
    
    # 打包交易資訊成一dict
    def pack_transaction_to_dict(self):
        tmp_dict = {
            'sender': self.sender,
            'receiver': self.receiver,
            'amounts': self.amounts,
            'msg': self.message,
            'community': self.community
        }
        return tmp_dict