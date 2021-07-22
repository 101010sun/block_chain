from pymongo import MongoClient
from Wallet import generate_address

#local host
conn = MongoClient()
#database
db = conn.localcurrency
#collection
col_Information_user       = db.Information_user
#connect error or not
col_Information_user.stats

def insert_Information_user(name,sex,birth,email,phone,address,idd,photo_id,walletaddress,public_key,private_key):
    data = {
      'Name':name,
      'Sex': sex,
      'Birth': birth,
      'Email': email,
      'Phone': phone,
      'Address': address,
      'Id': idd,
      'Photo_id': photo_id,
      'Walletaddress': walletaddress,
      'Public_key': public_key,
      'Private_key': private_key
    }
    col_Information_user.insert_one(data)

def register():
  name = "10 6號"
  sex = "女"
  birth = "1999"
  email = "10mail"
  phone = "0910101010"
  address = ["高雄","台中"]
  idd = "10id"
  photo_id = "10photo"
  walletaddress,privatekey = generate_address() #產生公私鑰地址
  public_key = walletaddress 
  private_key = str(privatekey).replace('\\n','') #過濾私鑰
  private_key = private_key.replace("b'-----BEGIN RSA PRIVATE KEY-----", '')
  private_key = private_key.replace("-----END RSA PRIVATE KEY-----'", '')
  private_key = private_key.replace(' ', '')
  insert_Information_user(name,sex,birth,email,phone,address,idd,photo_id,walletaddress,public_key,private_key)

register()