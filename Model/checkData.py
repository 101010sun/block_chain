from pymongo import MongoClient
from Blockchain import Wallet
import cryptocode
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
col_Commmunity               = db.Commmunity
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
col_Commmunity.stats

# 檢查_此帳號是否被使用過
def check_account(account):
  cursor = col_Information_user.find({"account":str(account)})
  data = [d for d in cursor]
  if account == 'system':
    return False
  if data == list([]): 
    return True
  else:
    return False

# 檢查此身分證號碼是否被使用過
def check_id(id_card):
  cursor = col_Information_user.find({"id_card":str(id_card)})
  data = [d for d in cursor]
  if data == list([]): 
    return True
  else:
    return False

# 檢查此帳號是否已加入社區
def check_has_community(account):
    myquery = {'account': account}
    cursor = col_Community_members.find(myquery)
    data = [d for d in cursor]
    if data != list([]):
        return data
    else:
        return None

# 檢查此信箱和電話是否被使用過
def check_userinfor(email,phone):
  cursor = col_Information_user.find({"email":str(email)})
  data = [d for d in cursor]
  cursor2 = col_Information_user.find({"phone":str(phone)})
  data2 = [d for d in cursor2]
  if data == list([]) and data2 == list([]):
    return True
  else:
    return False

# 檢查此帳號是否為平台管理員
def check_is_system_manage(account):
  myquery = {'account': account}
  cursor = col_System_members.find(myquery)
  data = [d for d in cursor]
  if data != list([]):
    return True
  else:
    return False

# 檢查平台密碼正確性
def check_platform_password(password):
  projectionFields = ['platform_password']
  cursor = col_System_members.find(projection = projectionFields)
  data = [d for d in cursor]
  platform_password = data[0]['platform_password']
  check = Wallet.encryption_id_card(password)
  if check == platform_password:
    return True
  else:
    return False

# check_platform_password('platform_password')