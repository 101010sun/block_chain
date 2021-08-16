import hashlib
import Format
import time

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

# 放置交易紀錄至新區塊中
def add_transaction_to_block(self, block):
    # Get the transaction with highest fee by block_limitation
    self.pending_transactions.sort(key=lambda x: x.fee, reverse=True)
    if len(self.pending_transactions) > self.block_limitation:
        transcation_accepted = self.pending_transactions[:self.block_limitation]
        self.pending_transactions = self.pending_transactions[self.block_limitation:]
    else:
        transcation_accepted = self.pending_transactions
        self.pending_transactions = []
    block.transactions = transcation_accepted

#我還沒改的---------------------

# 挖掘新區塊
def node_block(self, node):
    start = time.process_time()

    last_block = self.chain[-1]
    new_block = Format.Block(last_block.hash,node)

    self.add_transaction_to_block(new_block)
    new_block.previous_hash = last_block.hash
    new_block.hash = self.get_hash(new_block, new_block.nonce)

    while new_block.hash[0: self.difficulty] != '0' * self.difficulty:
        new_block.nonce += 1
        new_block.hash = self.get_hash(new_block, new_block.nonce)

    time_consumed = round(time.process_time() - start, 5)
    print(f"Hash found: {new_block.hash} @ difficulty {self.difficulty}, time cost: {time_consumed}s")
    self.chain.append(new_block)

def get_balance(self, account): 
    balance = 0
    for block in self.chain:
        # Check miner reward
        node = False
        if block.node == account:
            node = True
            balance += block.miner_rewards
        for transaction in block.transactions:
            if node:
                balance += transaction.fee
            if transaction.sender == account:
                balance -= transaction.amounts
                balance -= transaction.fee
            elif transaction.receiver == account:
                balance += transaction.amounts
    return balance

# 確認雜湊值是否正確
def verify_blockchain(self):
    previous_hash = ''
    for idx,block in enumerate(self.chain):
        if self.get_hash(block, block.nonce) != block.hash:
            print("Error:Hash not matched!")
            return False
        elif previous_hash != block.previous_hash and idx:
            print("Error:Hash not matched to previous_hash")
            return False
        previous_hash = block.hash
    print("Hash correct!")
    return True