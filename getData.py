from pymongo import MongoClient
import cryptocode
import Wallet
from bson.objectid import ObjectId
import gridfs
import numpy as np
import cv2

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
col_Community_members        = db.Community_members
col_Community_bulletin       = db.Community_bulletin
col_System_bulletin          = db.System_bulletin
col_System_members           = db.System_members
col_Community                = db.Community
#connect error or not
col_Information_user.stats
col_Information_demand.stats
col_Photo.stats
col_Check_community_manager.stats
col_Check_community_user.stats
col_Check_createcommunity.stats
col_Community_members.stats
col_Community_bulletin.stats
col_System_bulletin.stats
col_Community.stats

# 取得_此帳號的加密密碼
def Taken_password(account):
  projectionFields = ['e_password']
  cursor = col_Information_user.find({"account": str(account)}, projection = projectionFields)
  data = [d for d in cursor]
  if data != list([]):
    return data[0]['e_password']
  else:
    return None

# 取得_此帳號的私鑰
def Taken_privatekey(account,password):
  projectionFields = ['private_key']
  cursor = col_Information_user.find({"account": str(account)}, projection = projectionFields)
  data = [d for d in cursor]
  e_private_key = data[0]['private_key']
  privatekey = Wallet.decryption_privatekey(e_private_key, password)
  if data != list([]):
    return privatekey
  else:
    return None

# 取得_照片檔案
def download_photo(name):
    data = db.fs.files.find_one({'filename':name})
    my_id = data['_id']
    fs = gridfs.GridFS(db) #fs--選取資料庫
    outputdata = fs.get(my_id).read()
    download_location = "C:/Users/USER/block_chain/Pic/" + name
    output = open(download_location, "wb")
    output.write(outputdata)
    output.close()
    print("download complete")

    #圖片顯示
    img = cv2.imread(name)
    cv2.imshow('My Profile', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# 取得_此帳號錢包地址
def Taken_address(account):
  projectionFields = ['wallet_address']
  cursor = col_Information_user.find({"account": str(account)}, projection = projectionFields)
  data = [d for d in cursor]
  walletaddress = data[0]['wallet_address']
  if data != list([]):
    return walletaddress
  else:
    return None

# 取得_社區名單
def get_community():
    cursor = col_Community.find()
    data = [d for d in cursor]
    return data
