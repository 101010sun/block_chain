import sys
import socket
import threading
import time
import pickle

# def handle_receive():
#     transfer_str('user, 2')
#     while(True):
#         response = client.recv(4096)
#         if response:
#             print(f"[*] Message from node: {response}")

# def transfer_str(ts):
#     client.send(ts.encode())

if __name__ == "__main__":
    IPserver_host = '127.0.0.1'
    IPserver_port = int(sys.argv[1])

    target_host = ""
    target_port = int(0)

    # 與節點端連線使用
    # #open one thread keeping receiving the message sended from socket
    # receive_handler = threading.Thread(target=handle_receive, args=())
    # receive_handler.start()

    
    command_dict = {
        "1": "generate_address",
        "2": "get_balance",
        "3": "transaction",
        "4": "exit"
    }
    while(True):
        print("Command list:")
        print("1. generate_address")
        print("2. get_balance")
        print("3. transaction")
        print("4. exit")
        command = input("Command: ")
        if str(command) not in command_dict.keys():
            print("Unknown command.")
            continue

        message = {"identity": "user", "request": command_dict[str(command)]}
        if command_dict[str(command)] == "generate_address":
            print("generate_address...")

        elif command_dict[str(command)] == "get_balance":
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
                print("[*] target_host: " + target_host)
                print("[*] target_port: " + target_port)

            IPclient.shutdown(2)
            IPclient.close()
            print('connection close')
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
