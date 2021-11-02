import time
import hashlib
import rsa
import cryptocode

class Createrecord: 
    def __init__(self,currency_name,circulation,currency_value,community):
        self.currency_name = currency_name
        self.currency_value = currency_value 
        self.circulation = circulation
        self.community = community


    # 打包創建社區貨幣資訊成一dict
    def pack_transaction_to_dict(self):
        record_dict = {
            'currency_name': self.currency_name,
            'currency_value': self.currency_value,
            'circulation ': self.circulation ,
            'community': self.community,
        }
        return record_dict