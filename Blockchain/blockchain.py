import time
import hashlib
import rsa
import cryptocode
from Model import getData
from Blockchain import block, record, transaction

class BlockChain: 
    def __init__(self):
        self.difficultly = 5
        self.block_limitation = 10 
        self.chain = [] #All block store in blockchain now
        self.pending_transactions = [] #transactions pool
        self.pre_hash = ''
        self.recordchain = []

    #初始化一筆交易
    def initialize_transaction(self,sender,receiver,amounts,message,community):
        fee = amounts * 0.01
        allbalance = self.get_balance(sender)
        if community in allbalance.keys():
            if allbalance[community] < float(amounts) + float(fee):
                print("Balance not enough!")
                return False
            new_transaction = transaction.Transaction(sender,receiver,amounts,message,community)
            return new_transaction
        return None

    #初始化一筆系統交易
    def initialize_system_transaction(self,sender,receiver,amounts,message,community):
        fee = amounts * 0.01
        allbalance = self.get_system_balance(sender)
        if community in allbalance.keys():
            if allbalance[community] < float(amounts) + float(fee):
                print("[*] ", end='')
                print(allbalance[community])
                print("Balance not enough!")
                return False
            new_transaction = transaction.Transaction(sender,receiver,amounts,message,community)
            return new_transaction
        return None

    # 產生創世塊
    def create_genesis_block(self, nodeaddr):
        print("Create genesis block...")
        new_block = block.Block('https://www.youtube.com/watch?v=QuUWPqlhuNU&ab_channel=%E5%8B%95%E7%89%A9%E5%AE%B6', nodeaddr)
        self.pre_hash = new_block.get_hash()
        self.chain.append(new_block) #Add genesis to blockchain

    # 放置創建社區貨幣紀錄
    def add_record_to_block(self, record):
        self.recordchain.append(record)

    # 放置交易紀錄至區塊中
    def add_transactions_to_block(self, block):
        self.pending_transactions.sort(key=lambda x: x.fee, reverse=True)
        if len(self.pending_transactions) > self.block_limitation:
            transcation_accepted = self.pending_transactions[:self.block_limitation]
            self.pending_transactions = self.pending_transactions[self.block_limitation:]
        else:
            transcation_accepted = self.pending_transactions
            self.pending_transactions = []
        block.transactions = transcation_accepted

    # 挖掘新區塊
    def node_block(self, node):
        start = time.process_time()

        last_block = self.chain[-1]
        new_block = block.Block(last_block.hash,node)

        self.add_transactions_to_block(new_block)
        new_block.previous_hash = last_block.hash
        new_block.hash = new_block.get_hash()

        while new_block.hash[0: new_block.difficulty] != '0' * new_block.difficulty:
            new_block.nonce += 1
            new_block.hash = new_block.get_hash()

        time_consumed = round(time.process_time() - start, 5)
        print(f"Hash found: {new_block.hash} @ difficulty {new_block.difficulty}, time cost: {time_consumed}s")
        self.chain.append(new_block)
        print(self.chain)
        return new_block
    
    # 取得帳戶餘額(account = 錢包地址)
    def get_balance(self, account): 
        result = dict({})
        for block in self.chain:
            for transaction in block.transactions:
                if transaction.sender == account:
                    result[transaction.community] -= transaction.amounts
                    result[transaction.community] -= transaction.fee
                elif transaction.receiver == account:
                    result[transaction.community] += transaction.amounts
        return result

    # 取得平台錢包帳戶餘額
    def get_system_balance(self, plat_address): 
        platform_balance = dict({})
        # 計算交易手續費
        for block in self.chain:
            for transaction in block.transactions:
                if transaction.community in platform_balance.keys():
                    platform_balance[transaction.community] += transaction.fee
                else:
                    platform_balance[transaction.community] = transaction.fee
                if transaction.sender == plat_address:
                    platform_balance[transaction.community] -= transaction.amounts
                    platform_balance[transaction.community] -= transaction.fee
                elif transaction.receiver == plat_address:
                    platform_balance[transaction.community] += transaction.amounts

        for record in self.recordchain:
            if record.community in platform_balance.keys():
                platform_balance[record.community] += int(record.circulation)
            else:
                platform_balance[record.community] = int(record.circulation)
        return platform_balance

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

    # 將交易明細轉換成字串(dict)
    def transaction_to_string(self, transaction): #transaction to string
        transaction_dict = {
            'sender': str(transaction.sender),
            'receiver': str(transaction.receiver),
            'amounts': transaction.amounts,
            'fee': transaction.fee,
            'message': transaction.message
        }
        return str(transaction_dict)

    # 將創建社區貨幣紀錄轉換成字串(dict)
    def record_to_string(self, record): #transaction to string
        record_dict = {
            'currencyname': str(record.currencyname),
            'currencyvalue': float(record.currencyvalue),
            'circulation ': record.circulation,
            'community': str(record.community)
        }
        return str(record_dict)

    #簽署交易
    def sign_transaction(self, transaction, private_key):
        pem_prefix = '-----BEGIN RSA PRIVATE KEY-----\n'
        pem_suffix = '\n-----END RSA PRIVATE KEY-----'
        key = private_key
        key = '{}{}{}'.format(pem_prefix, key, pem_suffix)
        private_key_pkcs = rsa.PrivateKey.load_pkcs1(key)
        transaction_str = self.transaction_to_string(transaction)
        signature = rsa.sign(transaction_str.encode('utf-8'), private_key_pkcs, 'SHA-256')
        return signature

    # 放置交易紀錄至交易池中
    def add_transaction_to_pool(self, transaction, signature):
        public_key = '-----BEGIN RSA PUBLIC KEY-----\n'
        public_key += transaction.sender
        public_key += '\n-----END RSA PUBLIC KEY-----\n'
        public_key_pkcs = rsa.PublicKey.load_pkcs1(public_key.encode('utf-8'))
        transaction_str = self.transaction_to_string(transaction)
        system_addr = getData.taken_plat_address()
        if transaction.sender == system_addr:
            sender_balance = self.get_system_balance(transaction.sender)
        else:
            sender_balance = self.get_balance(transaction.sender)
        if transaction.community not in sender_balance.keys():
            print("No this community dollars")
            return False
        else:
            if transaction.fee + transaction.amounts > sender_balance[transaction.community]:
                print("Balance not enough!")
                return False
        try:
            # 驗證發送者
            rsa.verify(transaction_str.encode('utf-8'), signature, public_key_pkcs)
            print("Authorized successfully!")
            self.pending_transactions.append(transaction)
            return True
        except Exception:
            print("RSA Verified wrong!")
            
    #驗證區塊
    def receive_broadcast_block(self, block_data):
        last_block = self.chain[-1]
        # Check the hash of received block
        if block_data.previous_hash != last_block.hash:
            print("[**] Received block error: Previous hash not matched!")
            return False
        elif block_data.difficulty != self.difficulty:
            print("[**] Received block error: Difficulty not matched!")
            return False
        elif block_data.hash != self.get_hash(block_data, block_data.nonce):
            print(block_data.hash)
            print("[**] Received block error: Hash calculation not matched!")
            return False
        else:
            if block_data.hash[0: self.difficulty] == '0' * self.difficulty:
                for transaction in block_data.transactions:
                    self.chain.remove(transaction)
                self.receive_verified_block = True
                self.chain.append(block_data)
                return True
            else:
                print(f"[**] Received block error: Hash not matched by diff!")
            return False
