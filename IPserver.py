import sys
import socket
import threading
import time
import pickle

class IPServer:
    def __init__(self):
        # for P2P connection
        self.socket_host = "127.0.0.1"
        self.socket_port = int(sys.argv[1])
        self.target_host = ''
        self.target_port = int(0)
        self.start_socket_server()

    # open thread
    def start_socket_server(self):
        t = threading.Thread(target=self.wait_for_socket_connection)
        t.start()


    # waiting for the connection by keeping listening
    def wait_for_socket_connection(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.socket_host, self.socket_port))
            s.listen()
            while True:
                # accept this connection
                conn, address = s.accept()
                # open one thread to handle the mission
                client_handler = threading.Thread(target=self.receive_socket_message, args=(conn, address))
                client_handler.start()

                client_handler.join()
                print('end client_handler thread')


    # messages receiving from server handle
    def receive_socket_message(self, connection ,address):
        with connection:
            print(f'Connected by: {address}')

            message = connection.recv(1024)
            try:
                parsed_message = pickle.loads(message)
            except Exception:
                print(f"{message} cannot be parsed")
            print(f"[*] Received: {parsed_message}")

            if message:
                # check the identity msg. is user and want to get balance information
                # send one appropriate node's IP and Port number
                if parsed_message["identity"] == "user" and parsed_message["request"] == "get_balance":
                    # --find node's IP and Port number--
                    response = {"IP": "127.0.0.1", "Port_number": "1112"}
                    connection.send(pickle.dumps(response))

                # check the identity msg. is user and want to send a transaction
                # send all node's IP and Port number which are in the same community
                elif parsed_message["identity"] == "user" and parsed_message["request"] == "transaction":
                    # --find all community nodes' IP and Port number--
                    response = {"IP": ["127.0.0.1", "127.0.0.1", "127.0.0.1"], "Port_number": ["1112", "1113", "1114"]}
                    connection.send(pickle.dumps(response))

                # check the identity msg. is node
                # send one appropriate node's IP and Port number, and then
                # send all node's IP and Port number which are in the same community
                elif parsed_message["identity"] == "node" and parsed_message["request"] == "synchronize_chain":
                    # --find node's IP and Port number--
                    response = {"IP": "127.0.0.1", "Port_number": "1112"}
                    connection.send(pickle.dumps(response))

                    message = connection.recv(1024)
                    try:
                        parsed_message = pickle.loads(message)
                    except Exception:
                        print(f"{message} cannot be parsed")
                    print(f"[*] Received: {parsed_message}")
                    
                    # store the new node's ip and port number
                    self.target_port = parsed_message['IP']
                    self.target_host = int(parsed_message['Port_number'])

                    # --find all community nodes' IP and Port number--
                    response = {"IP": ["127.0.0.1", "127.0.0.1", "127.0.0.1"], "Port_number": ["1112", "1113", "1114"]}
                    connection.send(pickle.dumps(response))

                    # --broadcast the new node's ip and port number to every nodes in the same community--


if __name__ == "__main__":
    server = IPServer()