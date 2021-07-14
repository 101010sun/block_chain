import hashlib

def transaction_to_string(self,transcation): #transaction to string
    transaction_dict = {
        'sender': str(transaction.sender),
        'receiver': str(transaction.sender),
        'amounts': transaction.amounts,
        'fee': transaction.fee,
        'message': transaction.message
    }
    return str(transaction_dict)

def get_transaction_string(self,block): #take all transaction from block turn to string 
    transaction_str = ''
    for transaction in block.transactions:
        transaction_str += self.transaction_to_string(transaction) #transaction_str = transaction_str + self.transaction_to_string(transaction)
    return transaction_str 

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
    

