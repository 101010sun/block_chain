import time
import Format

def add_transaction_to_block(self, block): #放置交易紀錄至新區塊中
    # Get the transaction with highest fee by block_limitation
    self.pending_transactions.sort(key=lambda x: x.fee, reverse=True)
    if len(self.pending_transactions) > self.block_limitation:
        transcation_accepted = self.pending_transactions[:self.block_limitation]
        self.pending_transactions = self.pending_transactions[self.block_limitation:]
    else:
        transcation_accepted = self.pending_transactions
        self.pending_transactions = []
    block.transactions = transcation_accepted

def node_block(self, node): #挖掘新區塊
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

def verify_blockchain(self): #確認雜湊值是否正確
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