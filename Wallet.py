import rsa
import hashlib
import cryptocode

def generate_address():
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
    address = str(public_key).replace('\\n','')
    address = address.replace("b'-----BEGIN RSA PUBLIC KEY-----", '')
    address = address.replace("-----END RSA PUBLIC KEY-----'", '')
    address = address.replace(' ', '')
    return address, private_key

def encryption_password(password,id):
    s = hashlib.sha256()
    s.update(
        (
           str(password)
           +str(id)
        ).encode("utf-8")
    ) #Update hash SHA256
    h = s.hexdigest() #get hash
    return h

def encryption_privatekey(private_key,password): #加密私鑰
    e_private_key = cryptocode.encrypt(str(private_key),str(password))
    return e_private_key

def decryption_privatekey(e_private_key,password): #解密私鑰
    private_key = cryptocode.decrypt(str(e_private_key),str(password))
    return private_key

