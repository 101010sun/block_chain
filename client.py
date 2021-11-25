from getpass import getpass
import sys
import socket
import time
import pickle
import stdiomask
from Blockchain import Wallet
from Model import insertData, getData, checkData

# 登入頁面，回傳userinfo
def login():
    print('------- LOGIN -------')
    user_account = input('帳號      : ')
    user_password = stdiomask.getpass(prompt='密碼      : ', mask='*')
    user_id = input('身分證號碼: ')

    check_epass = Wallet.encryption_password(user_password, user_id)
    db_epass = getData.taken_password(user_account)
    if (check_epass == db_epass):
        final_data = {'帳號': user_account, '密碼': user_password, 'ID': user_id}
        return final_data
    else:
        print('登入失敗!')
        return dict({})

# 註冊頁面，回傳userinfo
def signup():
    print('------- SIGNUP (用戶資訊) -------')
    user_name = input('姓名      : ')
    user_id = input('身分證號碼: ')
    user_sex = input('生理性別 : ')
    user_birth = input('生日      : ')
    user_email = input('電子信箱 : ')
    user_phone = input('電話      : ')
    user_address = input('地址      : ')
    e_id = Wallet.encryption_id_card(user_id)
    check_id = checkData.check_id(e_id)
    if check_id:
        while(True):
            print('------- SIGNUP (建立帳戶) -------')
            user_account = input('帳號      : ')
            user_password = stdiomask.getpass(prompt='密碼      : ', mask='*')
            check_account = checkData.check_account(user_account)
            if check_account:
                walletaddress, private_key = Wallet.generate_address() # 產生公私鑰地址
                public_key = walletaddress
                e_password = Wallet.encryption_password(user_password, user_id) # 加密密碼 (明文身分證)
                e_private_key = Wallet.encryption_privatekey(private_key, user_password) # 加密私鑰 (明文密碼)
                insertData.insert_Information_user(user_name, user_sex, e_id, user_birth, user_email, user_phone, user_address, user_account, 'test', walletaddress, public_key, e_private_key, e_password)
                final_data = {'帳號': user_account, '密碼': user_password, 'ID': user_id}
                return final_data
            else:
                print('此帳號以註冊過，請換一個!')
    else:
        print('您已註冊過了!請選擇登入選項!')
        return dict({})

# 平台管理員頁面
def system_manager_page(IPserver_host, IPserver_port, user_info):
    sys_pass = input('請輸入平台密碼: ')
    issyspasscurrent = checkData.check_platform_password(sys_pass)
    if issyspasscurrent == False:
        print('密碼錯誤!')
    elif issyspasscurrent:
        print("1. 查創建社區清單")
        print("2. 查詢平台錢包餘額")
        ans = int(input('Ans: '))
        if ans == 1:
            create_list = getData.take_create_community() # 取創建社區審查清單
            print("審查創建社區清單")
            if create_list != []:
                flag = int(1)
                for c in create_list: # 選擇要處理哪一個
                    print(str(flag) + '. ', end='')
                    print(c)
                    flag += 1
                print('請選擇要處理哪一個申請單: ', end='')
                ans = int(input())
                print('請輸入發行量: ', end='')
                cur_value = int(input())
                com_wallet_addr, com_private_key = Wallet.generate_address() # 建立社區錢包地址
                timestamp = int(time.time()) 
                Wallet.encryption_comm_privatekey(com_private_key, timestamp, create_list[ans-1]['community']) # 加密社區私鑰
                insertData.insert_community(create_list[ans-1]['community'], com_wallet_addr, com_private_key)
                message = {"identity": "user", "request": "issue_money"}
                target_info = get_ip_issue_money(IPserver_host, IPserver_port, message) # 告知索引伺服器 要創建社區貨幣
                record_info = {
                    'currency_name': create_list[ans-1]['currency_name'],
                    'currency_value': float(create_list[ans-1]['currency_value']), 
                    'circulation': float(cur_value), 
                    'community': create_list[ans-1]['community'],
                    'timestamp': timestamp
                    }
                message['request'] = 'issue_money'
                get_issue_money_result(target_info['IP'], target_info['Port_number'], message, record_info) # 告知主節點 要發行社區貨幣
                # -- 移除創建社區清單
                sender = getData.taken_plat_address()
                receiver = getData.taken_community_address(create_list[ans-1]['community'])
                amounts = cur_value
                msg = '創建社區貨幣'
                community = create_list[ans-1]['community']
                transmsg = {'sender': sender, 'receiver': receiver, 'amounts': (amounts-amounts*0.01), 'msg': msg, 'community': community, 'system_password': sys_pass, 'account': user_info['帳號']}
                message = {"identity": "user", "request": "transaction"}
                target_info = get_ip_transaction(IPserver_host, IPserver_port, message, user_info)
                message['request'] = 'system_transaction'
                get_system_transaction_result(target_info['IP'], target_info['Port_number'], message, transmsg) # 轉帳給社區帳戶
                new_com_account = create_list[ans-1]['applicant_account']
                community_address = str('test_addr')
                identity = '管理員'
                insertData.insert_Community_members(new_com_account, community, community_address, identity)
            else:
                print('目前無社區申請')

        elif ans == 2:
            sys_addr = getData.taken_plat_address() # 取平台錢包地址
            message = {"identity": "user", "request": "get_system_balance"}
            target_info = get_ip_getsysbalance(IPserver_host, IPserver_port, message) # 告知索引伺服器 要查詢平台餘額
            print('[*] ', end='')
            print(target_info)
            message['request'] = 'get_system_balance'
            get_sys_balance_result(target_info['IP'], target_info['Port_number'], message, sys_addr) # 告知主節點 要查詢平台餘額

# 社區管理員頁面
def community_manager_page(IPserver_host, IPserver_port, user_info, this_community):
    print("1. 移除社區成員")
    print("2. 審核社區成員申請名單")
    print("3. 基本功能")
    ans = int(input("Ans: "))
    if ans == 1: # 移除社區成員名單
        member_list = getData.take_community_members(this_community)
        if member_list != []:
            flag = 1
            for m in member_list:
                print(flag, end='. ')
                print(m)
            ans = int(input('請輸入欲移除的社區成員: '))
            # -- 移除社區成員
            msg = 'get_balance' # 取用戶帳戶餘額
            target_info = get_ip_getbalance(IPserver_host, IPserver_port, msg)
            user_balance = get_balance_result(target_info['IP'], target_info['Port_number'], msg, user_info)
            if this_community in user_balance.keys(): # 用戶領取帳戶餘額
                msg = 'transaction'
                target_info = get_ip_transaction(IPserver_host, IPserver_port, msg, user_info)
                get_remove_transaction_result(target_info['IP'], target_info['Port_number'], msg, user_info, member_list[ans-1], user_balance[this_community], this_community)
            else:
                print('此欲移除的社區成員錢包無社區貨幣餘額')
    elif ans == 2: # 審核社區成員申請名單
        print('1. 審核社區管理員申請')
        print('2. 審核一般用戶申請')
        ans = int(input('請輸入欲審查的名單: '))
        if ans == 1: # 審核社區管理員審核名單
            apply_list = getData.take_community_manager_apply(this_community)
            if apply_list != []:
                flag = 1
                for a in apply_list:
                    print(flag, end='. ')
                    print(a)
                ans = int(input('請選擇要處理哪一個申請: '))
                # -- 將此申請帳戶身分更新成為管理員
            else:
                print('目前此項目無申請')
        elif ans == 2: # 審核社區一般用戶審核名單
            apply_list = getData.take_community_member_apply(this_community)
            if apply_list != []:
                flag = 1
                for a in apply_list:
                    print(flag, end='. ')
                ans = int(input('請選擇要處理哪一個申請: '))
                insertData.insert_Community_members(apply_list[ans-1]['applicant_account'], this_community, apply_list[ans-1]['apply_address'], '一般用戶')
            else:
                print('目前此項目無申請')
    elif ans == 3: # 基本功能
        print('基本功能頁面')
        community_member_page(IPserver_host, IPserver_port, user_info, this_community)

# 一般用戶頁面
def community_member_page(IPserver_host, IPserver_port, user_info, this_community):
    command_dict = {"1": "get_balance", "2": "transaction", "3": "exit"}
    for key, value in command_dict.items():
        print(key,end='')
        print(': ',end='')
        print(value)
    command = input("Command: ")
    message = {"identity": "user", "request": command_dict[str(command)]}
    if command_dict[str(command)] == "get_balance":
        rec = get_ip_getbalance(IPserver_host, IPserver_port, message)
        if rec != {}:
            target_host = rec['IP']
            target_port = rec['Port_number']
            result = get_balance_result(target_host, target_port, message, user_info)
        else: print('[*] Get Balance Node Fail!')
    
    elif command_dict[str(command)] == "transaction":
        rec = get_ip_transaction(IPserver_host, IPserver_port, message, user_info)
        if rec != {}:
            target_host = rec['IP']
            target_port = rec['Port_number']
            result = get_transaction_result(target_host, target_port, message, user_info)
        else:
            print('[*] Trancation Fail!')

    elif command_dict[str(command)] == "exit":
        print('Bye Bye ~')

# 告知索引伺服器 查詢資料請求
def get_ip_getbalance(IPserver_host, IPserver_port, message):
    indexclient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    indexclient.connect((IPserver_host, IPserver_port))
    indexclient.send(pickle.dumps(message))
    
    response = indexclient.recv(4096)
    if response:
        try:
            parsed_message = pickle.loads(response)
        except Exception:
            print(f"{message} cannot be parsed")
        target_host = parsed_message['IP']
        target_port = int(parsed_message['Port_number'])
        tmp = {'IP': target_host, 'Port_number': target_port}
        indexclient.shutdown(2)
        indexclient.close()
        print('[*] ',end='')
        print(tmp)
        print('connection close')
        return tmp
    return {}

# 向目標主節點發送 查詢資料請求
def get_balance_result(target_host, target_port, message, user_info):
    nodeclient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    nodeclient.connect((target_host, target_port))
    nodeclient.send(pickle.dumps(message))
    time.sleep(0.5)

    user_addr = getData.taken_address(user_info['帳號']) # 取使用者錢包地址
    message = {'account': user_addr}
    nodeclient.send(pickle.dumps(message))

    response = nodeclient.recv(4096)
    if response:
        try:
            parsed_message = pickle.loads(response)
        except Exception:
            print(f"{message} cannot be parsed")
        result = parsed_message['result']
        nodeclient.shutdown(2)
        nodeclient.close()
        print('[*] ',end='')
        print(result)
        print('connection close')
        return result
    return ''

# 告知索引伺服器 發起交易請求
def get_ip_transaction(IPserver_host, IPserver_port, message, user_info):
    IPclient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    IPclient.connect((IPserver_host, IPserver_port))
    IPclient.send(pickle.dumps(message))
    time.sleep(0.5)
    
    response = IPclient.recv(4096)
    if response:
        try:
            parsed_message = pickle.loads(response)
        except Exception:
            print(f"{message} cannot be parsed")
        target_host = parsed_message['IP']
        target_port = int(parsed_message['Port_number'])
        tmp = {'IP': target_host, 'Port_number': target_port}
        IPclient.shutdown(2)
        IPclient.close()
        print('[*] ',end='')
        print(tmp)
        print('connection close')
        return tmp
    return {}

# 向目標主節點發送 發起交易請求
def get_transaction_result(target_host, target_port, message, user_info):
    nodeclient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    nodeclient.connect((target_host, target_port))
    nodeclient.send(pickle.dumps(message))
    time.sleep(0.5)
    
    sender = getData.taken_address(user_info['帳號'])
    tmp_receiver = input('收方帳號: ')
    receiver = getData.taken_address(tmp_receiver)
    amounts = input('交易總額: ')
    msg = input('交易內容: ')
    community = input('社區幣: ')
    message = {'sender': sender, 'receiver': receiver, 'amounts': amounts, 'msg': msg, 'community': community, 'password': user_info['密碼'], 'account': user_info['帳號']}
    nodeclient.send(pickle.dumps(message))

    response = nodeclient.recv(4096)
    if response:
        try:
            parsed_message = pickle.loads(response)
        except Exception:
            print(f"{message} cannot be parsed")
        result = parsed_message['result']
        nodeclient.shutdown(2)
        nodeclient.close()
        print('[*] ',end='')
        print(result)
        print('connection close')
        return result
    return ''

# 向目標主節點發送 發起交易請求
def get_remove_transaction_result(target_host, target_port, message, user_info, rec, amo, commun):
    nodeclient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    nodeclient.connect((target_host, target_port))
    nodeclient.send(pickle.dumps(message))
    time.sleep(0.5)
    
    sender = getData.taken_address(user_info['帳號'])
    tmp_receiver = rec
    receiver = getData.taken_address(tmp_receiver)
    amounts = amo
    msg = '兌現社區貨幣交易'
    community = commun
    message = {'sender': sender, 'receiver': receiver, 'amounts': amounts, 'msg': msg, 'community': community, 'password': user_info['密碼'], 'account': user_info['帳號']}
    nodeclient.send(pickle.dumps(message))

    response = nodeclient.recv(4096)
    if response:
        try:
            parsed_message = pickle.loads(response)
        except Exception:
            print(f"{message} cannot be parsed")
        result = parsed_message['result']
        nodeclient.shutdown(2)
        nodeclient.close()
        print('[*] ',end='')
        print(result)
        print('connection close')
        return result
    return ''

# 告知索引伺服器 發行貨幣請求
def get_ip_issue_money(IPserver_host, IPserver_port, message):
    indexclient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    indexclient.connect((IPserver_host, IPserver_port))
    indexclient.send(pickle.dumps(message))
    
    response = indexclient.recv(4096)
    if response:
        try:
            parsed_message = pickle.loads(response)
        except Exception:
            print(f"{message} cannot be parsed")
        target_host = parsed_message['IP']
        target_port = int(parsed_message['Port_number'])
        tmp = {'IP': target_host, 'Port_number': target_port}
        indexclient.shutdown(2)
        indexclient.close()
        print('[*] ',end='')
        print(tmp)
        print('connection close')
        return tmp
    return {}

# 向目標主節點發送 發行貨幣請求
def get_issue_money_result(target_host, target_port, message, record_info):
    nodeclient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    nodeclient.connect((target_host, target_port))
    nodeclient.send(pickle.dumps(message))
    time.sleep(0.5)

    message = {
            'currency_name': record_info['currency_name'],
            'currency_value': record_info['currency_value'],
            'circulation': record_info['circulation'] ,
            'community': record_info['community'],
            'timestamp': record_info['timestamp']
        }
    nodeclient.send(pickle.dumps(message))

# 告知索引伺服器 查詢平台資料請求
def get_ip_getsysbalance(IPserver_host, IPserver_port, message):
    indexclient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    indexclient.connect((IPserver_host, IPserver_port))
    indexclient.send(pickle.dumps(message))
    
    response = indexclient.recv(4096)
    if response:
        try:
            parsed_message = pickle.loads(response)
        except Exception:
            print(f"{message} cannot be parsed")
        target_host = parsed_message['IP']
        target_port = int(parsed_message['Port_number'])
        tmp = {'IP': target_host, 'Port_number': target_port}
        print('[*] ',end='')
        print(tmp)
        print('connection close')
        indexclient.shutdown(2)
        indexclient.close()
        return tmp
    return {}

# 向目標主節點發送 查詢平台資料請求
def get_sys_balance_result(target_host, target_port, message, sys_wallet_addr):
    nodeclient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    nodeclient.connect((target_host, target_port))
    nodeclient.send(pickle.dumps(message))
    time.sleep(0.5)

    message = {'account': sys_wallet_addr}
    nodeclient.send(pickle.dumps(message))

    response = nodeclient.recv(4096)
    if response:
        try:
            parsed_message = pickle.loads(response)
        except Exception:
            print(f"{message} cannot be parsed")
        result = parsed_message['result']
        nodeclient.shutdown(2)
        nodeclient.close()
        print('[*] ',end='')
        print(result)
        print('connection close')
        return result
    return ''

# 向目標主節點發送 發起交易(轉帳社區貨幣)請求
def get_system_transaction_result(target_host, target_port, message, transmsg):
    nodeclient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    nodeclient.connect((target_host, target_port))
    nodeclient.send(pickle.dumps(message))
    time.sleep(0.5)
    
    nodeclient.send(pickle.dumps(transmsg))

    response = nodeclient.recv(4096)
    if response:
        try:
            parsed_message = pickle.loads(response)
        except Exception:
            print(f"{message} cannot be parsed")
        result = parsed_message['result']
        nodeclient.shutdown(2)
        nodeclient.close()
        print('[*] ',end='')
        print(result)
        print('connection close')
        return result
    return ''

if __name__ == "__main__":
    IPserver_host = '127.0.0.1'
    IPserver_port = int(sys.argv[1])
    target_host = ""
    target_port = int(0)
    user_info = {}
    while(True):
        print('LOGIN or SIGN_UP (1/2)?: ', end='') # 登入或註冊
        choose = int(input())
        if choose == 1:
            user_info = login() # 登入
            if(user_info != dict({})): break
        elif choose == 2:
            user_info = signup() # 註冊
            if(user_info != dict({})): break
    
    issystemmanager = checkData.check_is_system_manage(user_info['帳號']) # 檢查是否為平台管理者
    if issystemmanager == True: # 是否使用平台帳號
        ans = input('使用平台帳號嗎(y/n)?: ')
        if ans == 'y' or ans == 'Y':
            print('平台管理員權限') 
            system_manager_page(IPserver_host, IPserver_port, user_info) # 切換到平台管理者權限
        else:
            issystemmanager = False

    isjoincommunnity = checkData.check_has_community(user_info['帳號']) # 是否已加入社區
    if isjoincommunnity == None and issystemmanager == False: # 無加入社區
        command = input("創建社區 or 加入社區 (1/2)?: ")
        if str(command) == '1': # 創建社區
            community = input('請輸入社區名稱: ')
            currency_name = input('請輸入社區貨幣名稱: ')
            while(True):
                circulation = input('請輸入幣值: ')
                if circulation.isdigit():
                    break
                else:
                    print('幣值請輸入數字!')
            insertData.insert_Check_createcommunity(user_info['帳號'], community, currency_name, float(circulation)) # 申請創建社區
        elif str(command) == '2': # 加入社區
            community_list = getData.take_community() # 取得社區清單
            flag = 1
            for com in community_list:
                print(flag, end='. ')
                print(com)
                flag += 1
            while(True):
                which_community = input("Answer: ")
                if which_community.isdigit():
                    which_community = int(which_community)
                    if int(which_community) > flag or int(which_community) < 1:
                        print("輸入超過大小了!")
                    else:
                        break
                else:
                    print('社區編號請輸入數字!')
            apply_community = community_list[which_community-1]
            apply_address = input("請輸入社區地址: ")
            insertData.insert_Check_community_user(user_info['帳號'], apply_community, apply_address) # 申請加入社區清單
    
    elif isjoincommunnity != None and issystemmanager == False: # 有加入社區
        comlist = getData.taken_comandid(user_info['帳號'])
        flag = 1
        while(True):
            print(flag, end='. ')
            print(comlist[0]['community'][flag-1], end=' ')
            print(comlist[0]['identity'][flag-1])
            flag += 1
            if (flag-1) == len(comlist[0]['community']): break
        ans = int(input('請選擇要進入哪個社區: ')) # 選擇要進入的社區頁面
        if comlist[0]['identity'][ans-1] == '管理員':
            print('社區管理員權限') 
            community_manager_page(IPserver_host, IPserver_port, user_info, comlist[0]['community'][ans-1])
        elif comlist[0]['identity'][ans-1] == '一般用戶':
            print('一般用戶權限')
            community_member_page(IPserver_host, IPserver_port, user_info, comlist[0]['community'][ans-1])

        

