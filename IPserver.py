import sys
import socket
import threading
import time

class IPServer:
    def __init__(self):
        # for P2P connection
        self.socket_host = "127.0.0.1"
        self.socket_port = int(sys.argv[1])
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

    # messages receiving from server handle
    def receive_socket_message(self, connection ,address):
        with connection:
            print(f'Connected by: {address}')
            while True:
                message = connection.recv(1024)
                print(f"[*] Received: {message}")
                time.sleep(1)
                response_bytes = str('node IP and Port number').encode('utf8')
                connection.sendall(response_bytes)
                break



if __name__ == "__main__":
    server = IPServer()