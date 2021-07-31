from pymongo import MongoClient
import cryptocode
import Wallet

#local host
conn = MongoClient()
#database
db = conn.localcurrency
#collection
col_Information_user         = db.Information_user
col_Information_demand       = db.Information_demand
col_Photo                    = db.Photo
col_Check_community_manager  = db.Check_community_manager
col_Check_community_user     = db.Check_community_user
col_Check_createcommunity    = db.Check_createcommunity
col_Communitymembers         = db.Communitymembers
#connect error or not
col_Information_user.stats
col_Information_demand.stats
col_Photo.stats
col_Check_community_manager.stats
col_Check_community_user.stats
col_Check_createcommunity.stats
col_Communitymembers.stats

def insert_Information_user(name,sex,birth,email,phone,address,idd,photo_id,walletaddress,public_key,e_private_key,e_password): #加入帳戶資訊
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
  name = "臨終委"
  sex = "男"
  birth = "2000-02-01"
  #database-date
  #birth = datetime.datetime.strptime("2017-10-13T10:53:53.000Z", "%Y-%m-%dT%H:%M:%S.000Z")
  email = "ALLENuglymail"
  phone = "091078364"
  address = ["台中"]
  idd = "aaaallenn"
  photo_id = "allenphoto"
  walletaddress,privatekey = Wallet.generate_address() #產生公私鑰地址
  public_key = walletaddress 
  private_key = str(privatekey).replace('\\n','') #過濾私鑰
  private_key = private_key.replace("b'-----BEGIN RSA PRIVATE KEY-----", '')
  private_key = private_key.replace("-----END RSA PRIVATE KEY-----'", '')
  private_key = private_key.replace(' ', '')
  #密碼
  password = "allenHI"
  e_password = Wallet.encryption_password(password,idd) #加密密碼
  e_private_key = Wallet.encryption_privatekey(private_key,password) #加密私鑰
  insert_Information_user(name,sex,birth,email,phone,address,idd,photo_id,walletaddress,public_key,e_private_key,e_password)

def insert_Information_demand(requester_id,applicant_id,Photo_id,productname,amount,details):
    data = {
      'requester_id':requester_id,
      'applicant_id': applicant_id,
      'demand_imfor':{
        'Photo_id': Photo_id,
        'productname': productname,
        'amount': amount,
        'details': details
      }
    }
    col_Information_demand.insert_one(data)

def insert_Photo(length,chunkSize,uploadDate,filename,metadata):
    data = {
      'length':length,
      'chunkSize': chunkSize,
      'uploadDate': uploadDate,
      'filename': filename,
      'metadata': metadata
    }
    col_Photo.insert_one(data)
    
# 檢查有無相同此帳戶資訊
def Check_userinfor(email,phone):
  cursor = col_Information_user.find({"email":str(email)})
  data = [d for d in cursor]
  cursor2 = col_Information_user.find({"phone":str(phone)})
  data2 = [d for d in cursor2]
  if data == [] and data2 == []:
    return True
  else:
    return False

# 檢查有無此帳號
def Check_account(id):
  cursor = col_Information_user.find({"id":str(id)})
  data = [d for d in cursor]
  if data == []: 
    return False
  else:
    return True

# 取此帳號的加密密碼
def Taken_password(id):
  projectionFields = ['e_password']
  cursor = col_Information_user.find({"email":"53mail"}, projection = projectionFields)
  data = [d for d in cursor]
  return data

