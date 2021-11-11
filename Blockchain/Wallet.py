import rsa
import hashlib
import cryptocode

# 產生錢包地址
# return: 錢包地址(公鑰)、私鑰
def generate_address():
    public, private = rsa.newkeys(512) #rsa 
    #public key
    public_key = public.save_pkcs1()
    # with open('public.pem','wb')as f:
    #     f.write(public_key)
    #private key
    private_key = private.save_pkcs1()
    # with open('private.pem','wb')as f:
    #     f.write(private_key)
    
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
def encryption_password(password, e_id_card):
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
def encryption_id_card(id_card):
    s = hashlib.sha256()
    s.update(
        (
           str(id_card)
        ).encode("utf-8")
    ) #Update hash SHA256
    e_id_card = s.hexdigest() #get hash
    return e_id_card

# 加密私鑰
def encryption_privatekey(private_key, password):
    e_private_key = cryptocode.encrypt(str(private_key),str(password))
    return e_private_key

# 解密私鑰
# return: 私鑰
def decryption_privatekey(e_private_key, password):
    private_key = cryptocode.decrypt(str(e_private_key),str(password))
    return private_key

# 加密社區私鑰
def encryption_comm_privatekey(private_key,timestamp,community_name):
    key = str(timestamp) + community_name
    e_private_key = cryptocode.encrypt(str(private_key),str(key))
    return e_private_key

# 解密社區私鑰
def decryption_comm_privatekey(e_private_key, timestamp, community_name):
    key = str(timestamp) + community_name
    private_key = cryptocode.decrypt(str(e_private_key),str(key))
    return private_key

