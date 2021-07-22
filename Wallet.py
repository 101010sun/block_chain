import rsa
def generate_address():
    public, private = rsa.newkeys(512) #rsa key
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