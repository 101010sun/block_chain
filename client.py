import sys
import socket
import threading
import time
import pickle
from getpass import getpass
import stdiomask

def handle_receive(client):
    transfer_str('user, 2')
    while(True):
        response = client.recv(4096)
        if response:
            print(f"[*] Message from node: {response}")

def transfer_str(client, ts):
    client.send(ts.encode())

# login func.
# return the dict of user's account, password
def login():
    print('------- LOGIN -------')
    user_account = input('帳號      : ')
    user_password = stdiomask.getpass(prompt='密碼      : ', mask='*')
    user_identity = stdiomask.getpass(prompt='身分證號碼: ', mask='*')
    # --去資料庫取資料並比對，對的話回傳帳號和明文密碼
    final_data = {'帳號': user_account, '密碼': user_password}
    print(final_data)
    return final_data

# sign up func.
# return the dict of user's account, password
def signup():
    print('------- SIGNUP (用戶資訊) -------')
    user_name = input('姓名    : ')
    user_sex = input('生理性別: ')
    user_birth = input('生日    : ')
    user_email = input('電子信箱: ')
    user_phone = input('電話    : ')
    user_address = input('地址    : ')
    # --去資料庫取資料檢查用戶是否註冊過，無此用戶資訊才繼續建立帳戶
    print('------- SIGNUP (建立帳戶) -------')
    user_account = input('帳號      : ')
    user_password = stdiomask.getpass(prompt='密碼      : ', mask='*')
    user_identity = stdiomask.getpass(prompt='身分證號碼: ', mask='*')
    # --資料庫建立帳戶，並匯入用戶資訊，註冊後即登入 回傳帳號和明文密碼
    final_data = {'帳號': user_account, '密碼': user_password}
    print(final_data)
    return final_data

if __name__ == "__main__":
    IPserver_host = '127.0.0.1'
    IPserver_port = int(sys.argv[1])

    target_host = ""
    target_port = int(0)
    # user menu dict
    command_dict = {"1": "get_balance", "2": "transaction", "3": "exit"}
    # 與節點端連線使用
    # #open one thread keeping receiving the message sended from socket
    # receive_handler = threading.Thread(target=handle_receive, args=())
    # receive_handler.start()

    # choose login or singup block
    print('LOGIN or SIGN_UP (1/2)?: ', end='')
    choose = int(input())
    if choose == 1:
        user_info = login()
    elif choose == 2:
        user_info = signup()
    
    while(user_info['密碼'] != ''):
        for key, value in command_dict.items():
            print(key,end='')
            print(': ',end='')
            print(value)
        command = input("Command: ")
        if str(command) not in command_dict.keys():
            print("Unknown command.")
            continue
        message = {"identity": "user", "request": command_dict[str(command)]}

        if command_dict[str(command)] == "get_balance": # 查詢錢包總額
            # build the connection with IPserver
            IPclient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            IPclient.connect((IPserver_host, IPserver_port))
            # send the msg. to IPserver
            IPclient.send(pickle.dumps(message))
            # waiting for the IPserver response
            response = IPclient.recv(4096)
            if response:
                try:
                    parsed_message = pickle.loads(response)
                except Exception:
                    print(f"{message} cannot be parsed")
                target_host = parsed_message['IP']
                target_port = parsed_message['Port_number']
                print("[*] target_host: " + target_host)
                print("[*] target_port: " + target_port)

            IPclient.shutdown(2)
            IPclient.close()
            # --聯絡此target節點，跟節點說要查詢，並取得錢包總額資料
            break
        
        elif command_dict[str(command)] == "transaction":
            # build the connection with IPserver
            IPclient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            IPclient.connect((IPserver_host, IPserver_port))

            # send the msg. to IPserver
            IPclient.send(pickle.dumps(message))
            # waiting for the IPserver response
            response = IPclient.recv(4096)
            if response:
                # print(f"[*] Message from node: {response}")
                try:
                    parsed_message = pickle.loads(response)
                except Exception:
                    print(f"{message} cannot be parsed")

                # print(f"[*] Message from node: {parsed_message}")
                target_host = parsed_message['IP']
                target_port = parsed_message['Port_number']
                print("[*] target_host: ", end="")
                print(target_host)
                print("[*] target_port: ", end="")
                print(target_port)

            IPclient.shutdown(2)
            IPclient.close()
            print('connection close')
            break

        elif command_dict[str(command)] == "exit":
            break



    # 與節點端連線使用
    # print('Wait until Thread is terminating')
    # receive_handler.join()
    # print("EXIT __main__")
