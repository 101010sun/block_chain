from Crypto.PublicKey import RSA #不能import rsa
#def generate_address(self): #為什麼不能副函式
# 產生 1024 位元 RSA 金鑰 #不能用512位元
private = RSA.generate(1024)
public = RSA.generate(1024)
# 產生私鑰
private_Key = private.export_key()
with open("private.pem", "wb") as f:
    f.write(private_Key)
# 產生公鑰
public_Key = public.publickey().export_key()
with open("public.pem", "wb") as f:
    f.write(public_Key)

"""encodedKey = open("public.pem", "rb").read()
key = RSA.import_key(encodedKey)
print(public.publickey().export_key().decode('utf-8'))"""

address = (public_Key.decode('utf-8')).replace('\\n','')
address = address.replace("-----BEGIN PUBLIC KEY-----",'')
address = address.replace("-----END PUBLIC KEY-----",'')
address = address.replace(' ', '')
print('Address:', address)
#return