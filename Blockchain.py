import time
import hashlib

class Transaction: 
    def __init__(self,sender,receiver,amounts,message,community):
        self.sender = sender 
        self.receiver = receiver 
        self.amounts = amounts 
        self.fee = amounts * 0.1 
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

class Block: 
    def __init__(self,previous_hash,node):
        self.previous_hash = previous_hash #next block hash
        self.hash = '' # this block hash
        self.difficulty = 2 
        self.nonce = 0 #key
        self.timestamp = int(time.time()) 
        self.transactions = [] 
        self.node = node

    # 添加(除建構子和交易外的)資訊填入
    def add_other_info(self, hash, nonce, timestamp):
        self.hash = hash
        self.nonce = nonce
        self.timestamp = timestamp

    # 添加交易資訊填入
    def add_transaction(self, transaction):
        self.transactions.append(transaction)

    # 打包區塊資訊成一dict(除交易)
    def pack_block_to_dict(self):
        tmp_dict = {
            'previous_hash': self.previous_hash,
            'hash': self.hash,
            'nonce': self.nonce,
            'timestamp': self.timestamp,
            'transactions_len': len(self.transactions),
            'node': self.node
            }
        return tmp_dict

    # 將交易明細轉換成字串(dict)
    def transaction_to_string(self, transaction): #transaction to string
        transaction_dict = {
            'sender': str(transaction.sender),
            'receiver': str(transaction.sender),
            'amounts': transaction.amounts,
            'fee': transaction.fee,
            'message': transaction.message
        }
        return str(transaction_dict)

    # 把區塊紀錄內的所有交易明細轉換成一個字串
    def get_transaction_string(self): #take all transaction from block turn to string 
        transaction_str = ''
        for transaction in self.transactions:
            transaction_str += self.transaction_to_string(transaction) #transaction_str = transaction_str + self.transaction_to_string(transaction)
        return transaction_str 
    
    # 依據資料產生相對應的雜湊值
    def get_hash(self):
        s = hashlib.sha256()
        s.update(
            (
                self.previous_hash 
                + str(self.timestamp) #When block produce
                + str(self.get_transaction_string()) #all transaction from block
                + str(self.nonce) #mining nonce
            ).encode("utf-8")
        ) #Update hash SHA256
        h = s.hexdigest() #get hash
        self.hash = h
        return h

class BlockChain: 
    def __init__(self):
        self.difficultly = 2 
        self.block_limitation = 5 
        self.chain = [] #All block store in blockchain now
        self.pending_transactions = [] #transactions pool
        self.pre_hash = ''

    # 產生創世塊
    def create_genesis_block(self, nodeaddr):
        print("Create genesis block...")
        new_block = Block('https://www.youtube.com/watch?v=QuUWPqlhuNU&ab_channel=%E5%8B%95%E7%89%A9%E5%AE%B6', nodeaddr)
        self.pre_hash = new_block.get_hash()
        self.chain.append(new_block) #Add genesis to blockchain

    # 放置交易紀錄至新區塊中
    def add_transactions_to_block(self, block):
        self.pending_transactions.sort(key=lambda x: x.fee, reverse=True)
        if len(self.pending_transactions) > self.block_limitation:
            transcation_accepted = self.pending_transactions[:self.block_limitation]
            self.pending_transactions = self.pending_transactions[self.block_limitation:]
        else:
            transcation_accepted = self.pending_transactions
            self.pending_transactions = []
        block.transactions = transcation_accepted

    # 放置交易明細放入交易池裡
    def add_transaction_to_pool(self, transaction):
        self.pending_transactions.append(transaction)

    # 挖掘新區塊
    def node_block(self, node):
        start = time.process_time()

        last_block = self.chain[-1]
        new_block = Block(last_block.hash,node)

        self.add_transactions_to_block(new_block)
        new_block.previous_hash = last_block.hash
        new_block.hash = self.get_hash(new_block, new_block.nonce)

        while new_block.hash[0: self.difficulty] != '0' * self.difficulty:
            new_block.nonce += 1
            new_block.hash = self.get_hash(new_block, new_block.nonce)

        time_consumed = round(time.process_time() - start, 5)
        print(f"Hash found: {new_block.hash} @ difficulty {self.difficulty}, time cost: {time_consumed}s")
        self.chain.append(new_block)
    
    # 取得帳戶餘額
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
