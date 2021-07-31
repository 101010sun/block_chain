import hashlib
import Format

# 將交易明細轉換成字串
def transaction_to_string(self,transaction): #transaction to string
    transaction_dict = {
        'sender': str(transaction.sender),
        'receiver': str(transaction.sender),
        'amounts': transaction.amounts,
        'fee': transaction.fee,
        'message': transaction.message
    }
    return str(transaction_dict)

# 把區塊紀錄內的所有交易明細轉換成一個字串
def get_transaction_string(self,block): #take all transaction from block turn to string 
    transaction_str = ''
    for transaction in block.transactions:
        transaction_str += self.transaction_to_string(transaction) #transaction_str = transaction_str + self.transaction_to_string(transaction)
    return transaction_str 

# 依據資料產生相對應的雜湊值
def get_hash(self,block,nonce):
    s = hashlib.sha256()
    s.update(
        (
            block.previous_hash 
            + str(block.timestamp) #When block produce
            + str.get_transaction_string(block) #all transaction from block
            + str(nonce) #mining nonce
        ).encode("utf-8")
    ) #Update hash SHA256
    h = s.hexdigest() #get hash
    return h

# 產生創世塊
def create_genesis_block(self):
    print("Create genesis block...")
    new_block = Format.Block('https://www.youtube.com/watch?v=QuUWPqlhuNU&ab_channel=%E5%8B%95%E7%89%A9%E5%AE%B6','IM53Q101010SUNALLEN0201')
    new_block.hash = self.get_hash(new_block,0)
    self.chain.append(new_block) #Add genesis to blockchain