from pymongo import MongoClient
from Wallet import generate_address
from Wallet import encryption_password
from Wallet import encryption_privatekey
from Wallet import decryption_privatekey
import cryptocode

#local host
conn = MongoClient()
#database
db = conn.localcurrency
#collection
col_Information_user = db.Information_user
#connect error or not
col_Information_user.stats

def insert_Information_user(name,sex,birth,email,phone,address,idd,photo_id,walletaddress,public_key,e_private_key,e_password):
    data = {
      'name':name,
      'sex': sex,
      'birth': birth,
      'email': email,
      'phone': phone,
      'address': address,
      'id': idd,
      'photo_id': photo_id,
      'walletaddress': walletaddress,
      'public_key': public_key,
      'private_key': e_private_key,
      'e_password': e_password
    }
    col_Information_user.insert_one(data)

def register():
  name = "快成功了"
  sex = "女"
  birth = "2000-08-09"
  #database-date
  #birth = datetime.datetime.strptime("2017-10-13T10:53:53.000Z", "%Y-%m-%dT%H:%M:%S.000Z")
  email = "53mail"
  phone = "095353535"
  address = ["台中"]
  idd = "53id"
  photo_id = "53photo"
  walletaddress,privatekey = generate_address() #產生公私鑰地址
  public_key = walletaddress 
  private_key = str(privatekey).replace('\\n','') #過濾私鑰
  private_key = private_key.replace("b'-----BEGIN RSA PRIVATE KEY-----", '')
  private_key = private_key.replace("-----END RSA PRIVATE KEY-----'", '')
  private_key = private_key.replace(' ', '')
  #密碼
  password = "abcabcimsecret"
  e_password = encryption_password(password,idd) #加密密碼
  e_private_key = encryption_privatekey(private_key,password) #加密私鑰
  insert_Information_user(name,sex,birth,email,phone,address,idd,photo_id,walletaddress,public_key,e_private_key,e_password)
