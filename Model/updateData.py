from pymongo import MongoClient
from Blockchain import Wallet
import gridfs
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

# 更新_用戶資訊
def modify_userinfo(account,newname,newsex,newbirth,newemail,newphone):
    col_Information_user.update_many({"account": account}, {'$set': {"name":newname,"sex": newsex,"birth": newbirth,"email": newemail,"phone": newphone}}, upsert=True)
    return True

# ----test----
#col.update_many({"name": "bob"}, {'$set': {"name":"BOB","id": "con_xxx_bob-iP-xxx"}}, upsert=True)