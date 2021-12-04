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

# 更新_社區成員身分
def modify_Community_members(account,community):
    projectionFields = ['community'] #取社區資料
    cursor = col_Community_members.find({"account": str(account)}, projection = projectionFields)
    data = [d for d in cursor]
    communitylist = data[0]['community']
    commindex = communitylist.index(community)
    projectionFields = ['identity'] #取身分資料
    cursor = col_Community_members.find({"account": str(account)}, projection = projectionFields)
    data3 = [d for d in cursor]
    idlist = list(data3[0]['identity'])
    for iddata in idlist:
        col_Community_members.update_one({"account": account},{'$pull': {"identity": iddata}})
    newidlist = (idlist[commindex]).split(',')
    newidlist.append('管理員')
    print(newidlist)
    i = 0
    for iddata in idlist:
        i = i + 1
        if(i == commindex):
            col_Community_members.update_one({"account": account},{'$push': {"identity": newidlist}})
        else:
            col_Community_members.update_one({"account": account},{'$push': {"identity": iddata}})
        
    return True
   

# 移除_創建社區審核
def remove_Check_createcommunity(community):
    col_Check_createcommunity.delete_many({"community" : community})
  
# 移除_社區用戶審核
def remove_Check_community_user(account,community):
    col_Check_community_user.delete_many({"applicant_account" : account,"apply_community" : community})

# 移除_社區管理員審核
def remove_Check_community_manager(account,community):
    col_Check_community_manager.delete_many({"applicant_account" : account,"apply_community" : community})

# 移除_社區成員
def remove_Community_members(account,community):
    projectionFields = ['community'] #取社區資料
    cursor = col_Community_members.find({"account": str(account)}, projection = projectionFields)
    data = [d for d in cursor]
    communitylist = data[0]['community']
    commindex = communitylist.index(community)
    projectionFields = ['community_address'] #取社區地址資料
    cursor = col_Community_members.find({"account": str(account)}, projection = projectionFields)
    data2 = [d for d in cursor]
    commadrlist = data2[0]['community_address']
    projectionFields = ['identity'] #取身分資料
    cursor = col_Community_members.find({"account": str(account)}, projection = projectionFields)
    data3 = [d for d in cursor]
    idlist = list(data3[0]['identity'])
    community_address = commadrlist[commindex] #要移除的社區地址
    for iddata in idlist:
        col_Community_members.update_one({"account": account},{'$pull': {"identity": iddata}})
    del idlist[commindex]
    for iddata in idlist:
        col_Community_members.update_one({"account": account},{'$push': {"identity": iddata}})
    col_Community_members.update_many({"account" : account},{'$pull': {'community': community }})
    col_Community_members.update_one({"account" : account},{'$pull': {'community_address': community_address }})
   
    

# ----test----
#col.update_many({"name": "bob"}, {'$set': {"name":"BOB","id": "con_xxx_bob-iP-xxx"}}, upsert=True)
