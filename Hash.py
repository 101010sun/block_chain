import hashlib

def transaction_to_string(self,transcation): #將一筆交易明細轉換成字串
    transaction_dict = {
        'sender': str(transaction.sender),
        'receiver': str(transaction.sender),
        'amounts': transaction.amounts,
        'fee': transaction.fee,
        'message': transaction.message
    }
    return str(transaction_dict)

def get_transaction_string(self,block): #將區塊內的交易明細轉成一個字串
    transaction_str = ''
    for transaction in block.transactions:
        transaction_str += self.transaction_to_string(transaction) #transaction_str = transaction_str + self.transaction_to_string(transaction)
    return transaction_str #加上區塊內新字串

def get_hash(self,block,nonce):
    s = hashlib.sha256()
    s.update(
        (
            block.previous_hash #前一區塊的雜湊值
            + str(block.timestamp) #區塊產生當下時間戳
            + str.get_transaction_string(block) #區塊內所有交易明細
            + str(nonce) #挖掘中的nonce
        ).encode("utf-8")
    ) #更新SHA256雜湊值
    h = s.hexdigest() #取得hash雜湊值
    return h
    

