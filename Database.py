from pymongo import MongoClient
import cryptocode
import Wallet
from bson.objectid import ObjectId


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


# 新增使用者資訊
def insert_Information_user(name,sex,id_card,birth,email,phone,address,account,photo_id,walletaddress,public_key,e_private_key,e_password): #加入帳戶資訊
    data = {
      'name': name,
      'sex': sex,
      'id_card': id_card,
      'birth': birth,
      'email': email,
      'phone': phone,
      'address': address,
      'account': account,
      'photo_id': photo_id,
      'walletaddress': walletaddress,
      'public_key': public_key,
      'private_key': e_private_key,
      'e_password': e_password
    }
    info = col_Information_user.insert_one(data)
    return(info)


def register():
  name = "葉清偉"
  sex = "男"
  id_card = "F274234929"
  birth = "1999-08-13"
  #database-date
  #birth = datetime.datetime.strptime("2017-10-13T10:53:53.000Z", "%Y-%m-%dT%H:%M:%S.000Z")
  email = "fewffw"
  phone = "0974613264"
  address = ["桃園"]
  account = "rgrwgN"
  e_id_card = Wallet.encryption_id_card(id_card,account)
  photo_id = "wfwfwfefwr"
  walletaddress,private_key = Wallet.generate_address() #產生公私鑰地址
  public_key = walletaddress 
  #密碼
  password = "GFGwfwfe3"
  e_password = Wallet.encryption_password(password,e_id_card) #加密密碼
  e_private_key = Wallet.encryption_privatekey(private_key,password) #加密私鑰
  insert_Information_user(name,sex,e_id_card,birth,email,phone,address,account,photo_id,walletaddress,public_key,e_private_key,e_password)


# 加入_需求資訊
def insert_Information_demand(requester_id,applicant_id,Photo_id,productname,amount,details):
    data = {
      'requester_id': requester_id,
      'applicant_id': applicant_id,
      'demand_imfor':{
        'Photo_id': Photo_id,
        'productname': productname,
        'amount': amount,
        'details': details
      }
    }
    col_Information_demand.insert_one(data)


# 加入_圖檔
def insert_Photo(length,chunkSize,uploadDate,filename,metadata):
    data = {
      'length': length,
      'chunkSize': chunkSize,
      'uploadDate': uploadDate,
      'filename': filename,
      'metadata': metadata
    }
    col_Photo.insert_one(data)


# 加入_社區管理員審核名單
def insert_Check_community_manager(applicant_id,reason):
    data = {
      'applicant_id': applicant_id,
      'reason': reason
    }
    col_Check_community_manager.insert_one(data)


"""applicant_id = ObjectId("6107205294c0b981697f05b3")
applicant_id2 = ObjectId("6107209da0032317f9ae9cb0")
applicant_id3 = ObjectId("6107129617d3c57cdf4aad38")
applicant_id4 = ObjectId("6107125a7391e668b8407511")
applicant_id5 = ObjectId("61071198a38e42fb9e4b4a24")"""


# 加入_社區用戶審核名單
def insert_Check_community_user(applicant_id,applyaddress):
    data = {
      'applicant_id': applicant_id,
      'applyaddress': applyaddress
    }
    col_Check_community_user.insert_one(data)


# 加入_創建社區審核清單
def insert_Check_createcommunity(applicant_id,communityname,communityaddress):
    data = {
      'applicant_id': applicant_id,
      'communityname': communityname,
      'communityaddress': communityaddress
    }
    col_Check_createcommunity.insert_one(data)   


# 加入_社區用戶名單
def insert_Communitymembers(user_id,communityaddress,identity):
    data = {
      'user_id':user_id, ###改Validation 取名
      'communityaddress': communityaddress,
      'identity': identity
    }
    col_Communitymembers.insert_one(data)   


# 檢查此信箱和電話是否被使用過
def Check_userinfor(email,phone):
  cursor = col_Information_user.find({"email":str(email)})
  data = [d for d in cursor]
  cursor2 = col_Information_user.find({"phone":str(phone)})
  data2 = [d for d in cursor2]
  if data == list([]) and data2 == list([]):
    return True
  else:
    return False


# 檢查此身分證號碼是否被使用過
def Check_account(id_card):
  cursor = col_Information_user.find({"id_card":str(id_card)})
  data = [d for d in cursor]
  if data == list([]): 
    return True
  else:
    return False


# 取此帳號的加密密碼
def Taken_password(account):
  projectionFields = ['e_password']
  cursor = col_Information_user.find({"account": str(account)}, projection = projectionFields)
  data = [d for d in cursor]
  if data != list([]):
    return data[0]['e_password']
  else:
    return None

