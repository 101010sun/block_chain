from pymongo import MongoClient
import gridfs
import numpy as np
import cv2

#local host
conn = MongoClient()
#database
db = conn.localcurrency
name = 'Dog02.jpg'

# 將檔案寫入資料庫
def store_photo(name):
    file_location =  name
    file_data = open(file_location, "rb")
    data = file_data.read() #data--讀取檔案
    fs = gridfs.GridFS(db) #fs--選取資料庫
    fs.put(data, filename = name) #寫入資料庫
    print("upload complete")

# 從資料庫抓照片
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


store_photo(name)
download_photo(name)
