import sys
import socket
import threading
import time

def handle_receive():
    transfer_str('user, 2')
    while(True):
        response = client.recv(4096)
        if response:
            print(f"[*] Message from node: {response}")
            break

def transfer_str(ts):
    client.send(ts.encode())

if __name__ == "__main__":
    target_host = '127.0.0.1'
    target_port = int(sys.argv[1])
    # build the connection with node
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((target_host, target_port))
    #open one thread keeping receiving the message sended from socket
    receive_handler = threading.Thread(target=handle_receive, args=())
    receive_handler.start()

    time.sleep(1)

    print('Wait until Thread is terminating')
    receive_handler.join()
    print("EXIT __main__")
