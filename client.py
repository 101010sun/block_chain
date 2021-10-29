from getpass import getpass
import sys
import socket
import time
import pickle
import stdiomask
import Wallet
import Database
import Checkdata

def handle_receive(client):
    transfer_str('user, 2')
    while(True):
        response = client.recv(4096)
        if response:
            print(f"[*] Message from node: {response}")

def transfer_str(client, ts):
    client.send(ts.encode())

# return the dict of user's account, password or {}
def login():
    print('------- LOGIN -------')
    user_account = input('帳號      : ')
    user_password = stdiomask.getpass(prompt='密碼      : ', mask='*')
    user_id = input('身分證號碼: ')

    check_epass = Wallet.encryption_password(user_password, user_id)
    db_epass = Database.Taken_password(user_account)
    if (check_epass == db_epass):
        final_data = {'帳號': user_account, '密碼': user_password, 'ID': user_id}
        return final_data
    else:
        print('登入失敗!')
        return dict({})

# return the dict of user's account, password or {}
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
    check_id = Database.Check_id(e_id)
    if check_id:
        while(True):
            print('------- SIGNUP (建立帳戶) -------')
            user_account = input('帳號      : ')
            user_password = stdiomask.getpass(prompt='密碼      : ', mask='*')
            check_account = Database.Check_account(user_account)
            if check_account:
                walletaddress, private_key = Wallet.generate_address() # 產生公私鑰地址
                public_key = walletaddress
                e_password = Wallet.encryption_password(user_password, user_id) # 加密密碼 (明文身分證)
                e_private_key = Wallet.encryption_privatekey(private_key, user_password) # 加密私鑰 (明文密碼)
                Database.insert_Information_user(user_name, user_sex, e_id, user_birth, user_email, user_phone, user_address, user_account, 'test', walletaddress, public_key, e_private_key, e_password)
                final_data = {'帳號': user_account, '密碼': user_password, 'ID': user_id}
                return final_data
            else:
                print('此帳號以註冊過，請換一個!')
    else:
        print('您已註冊過了!請選擇登入選項!')
        return dict({})

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

# 向目標主節點發送查詢資料請求
def get_balance_result(target_host, target_port, message, user_info):
    nodeclient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    nodeclient.connect((target_host, target_port))
    nodeclient.send(pickle.dumps(message))
    time.sleep(0.5)
    user_addr = Database.Taken_address(user_info['帳號']) # 取使用者錢包地址
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

# 向目標主節點發送發起交易請求
def get_transaction_result(target_host, target_port, message, user_info):
    nodeclient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    nodeclient.connect((target_host, target_port))
    nodeclient.send(pickle.dumps(message))
    time.sleep(0.5)
    
    sender = Database.Taken_address(user_info['帳號'])
    tmp_receiver = input('收方帳號: ')
    receiver = Database.Taken_address(tmp_receiver)
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


if __name__ == "__main__":
    IPserver_host = '127.0.0.1'
    IPserver_port = int(sys.argv[1])
    target_host = ""
    target_port = int(0)
    command_dict = {"1": "get_balance", "2": "transaction", "3": "exit"}
    user_info = {}
    while(True):
        # choose login or singup block
        print('LOGIN or SIGN_UP (1/2)?: ', end='')
        choose = int(input())
        if choose == 1:
            user_info = login()
            if(user_info != dict({})): break
        elif choose == 2:
            user_info = signup()
            if(user_info != dict({})): break
    
    isjoincommunnity = Checkdata.check_has_community(user_info['帳號'])
    if isjoincommunnity == None:
        print("創建社區 or 加入社區 (1/2)?: ", end='')
        command = input("Command: ")
        if str(command) == '1':
            community = input('請輸入社區名稱: ')
            # --申請加入社區清單
        elif str(command) == '2':
            community_list = Database.get_community() # 取得社區清單
            flag = 0
            for com in community_list:
                print(flag + '. ' + com)
                flag += 1
            which_community = input("Command: ")
            
            # --申請加入社區清單
    else:
        while(True):
            
            for key, value in command_dict.items():
                print(key,end='')
                print(': ',end='')
                print(value)
            command = input("Command: ")
            if str(command) not in command_dict.keys():
                print("Unknown command.")
                continue
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
                break

