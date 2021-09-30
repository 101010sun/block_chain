import time
import hashlib
import rsa
import cryptocode

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
        self.difficulty = 6
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
        self.difficultly = 6
        self.block_limitation = 5 
        self.chain = [] #All block store in blockchain now
        self.pending_transactions = [] #transactions pool
        self.pre_hash = ''

    #初始化一筆交易
    def initialize_transaction(self, sender, receiver, amount, fee, message):
        if self.get_balance(sender) < amount + fee:
            print("Balance not enough!")
            return False
        new_transaction = Transaction(sender, receiver, amount, fee, message)
        return new_transaction

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

    # 挖掘新區塊
    def node_block(self, node):
        start = time.process_time()

        last_block = self.chain[-1]
        new_block = Block(last_block.hash,node)

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
    
    # 取得帳戶餘額
    def get_balance(self, account): 
        balance = 0
        for block in self.chain:
            for transaction in block.transactions:
                if block.node == account:
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

    #送上鏈
    def add_transaction_to_pool(self, transaction, signature):
        public_key = '-----BEGIN RSA PUBLIC KEY-----\n'
        public_key += transaction.sender
        public_key += '\n-----END RSA PUBLIC KEY-----\n'
        public_key_pkcs = rsa.PublicKey.load_pkcs1(public_key.encode('utf-8'))
        transaction_str = self.transaction_to_string(transaction)
        if transaction.fee + transaction.amounts > self.get_balance(transaction.sender):
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

      ###Wallet      
    # 產生錢包地址
    # return: 錢包地址、?私鑰
    def generate_address(self):
        public, private = rsa.newkeys(512) #rsa 
        #PublicKey(8110652037018951423415384068343669562112781192066917099227440355062887030082561641925872544251324619419460659259927466333657527066898085681936273858467987, 65537)
        #PrivatKey
        #public key
        public_key = public.save_pkcs1()
        with open('public.pem','wb')as f:
            f.write(public_key)
        #private key
        private_key = private.save_pkcs1()
        with open('private.pem','wb')as f:
            f.write(private_key)
        #print(str(public_key))
        
        #過濾地址
        address = str(public_key).replace('\\n','')
        address = address.replace("b'-----BEGIN RSA PUBLIC KEY-----", '')
        address = address.replace("-----END RSA PUBLIC KEY-----'", '')
        address = address.replace(' ', '')
        #過濾私鑰
        private_key = str(private_key).replace('\\n','') 
        private_key = private_key.replace("b'-----BEGIN RSA PRIVATE KEY-----", '')
        private_key = private_key.replace("-----END RSA PRIVATE KEY-----'", '')
        private_key = private_key.replace(' ', '')
        return address, private_key

    # 加密明文密碼
    # return: 加密密碼
    def encryption_password(self,password, e_id_card):
        s = hashlib.sha256()
        s.update(
            (
            str(password)
            +str(e_id_card)
            ).encode("utf-8")
        ) #Update hash SHA256
        e_password = s.hexdigest() #get hash
        return e_password

    # 加密身分證字號
    # return: 加密身分證字號
    def encryption_id_card(self,id_card):
        s = hashlib.sha256()
        s.update(
            (
            str(id_card)
            ).encode("utf-8")
        ) #Update hash SHA256
        e_id_card = s.hexdigest() #get hash
        return e_id_card

    # 加密私鑰
    def encryption_privatekey(self,private_key, password):
        e_private_key = cryptocode.encrypt(str(private_key),str(password))
        return e_private_key

    # 解密私鑰
    # return: 私鑰
    def decryption_privatekey(self,e_private_key, password):
        private_key = cryptocode.decrypt(str(e_private_key),str(password))
        return private_key


    #測試    
    def start(self):
        address, private = self.generate_address()
        self.create_genesis_block('me')
        
        while(True):           
            # Step1: initialize a transaction
            transaction = self.initialize_transaction(address, 'test123', 0, 0, 'Test')
            if transaction:
                # Step2: Sign your transaction
                signature = self.sign_transaction(transaction, private)
                # Step3: Send it to blockchain
                self.add_transaction_to_pool(transaction, signature)
            self.node_block(address)
            print(self.get_balance(address))
            

# BC1 = BlockChain()
# BC1.start()