import time
import hashlib
import rsa
import cryptocode

class Record: 
    def __init__(self,currency_name, currency_value, circulation, community, timestamp):
        self.currency_name = currency_name
        self.currency_value = float(currency_value) 
        self.circulation = int(circulation)
        self.community = community
        self.timestamp = timestamp

    # 打包創建社區貨幣資訊成一dict
    def pack_transaction_to_dict(self):
        record_dict = {
            'currency_name': self.currency_name,
            'currency_value': self.currency_value,
            'circulation ': self.circulation ,
            'community': self.community,
            'timestamp': self.timestamp
        }
        return record_dict