import socket
import os
import sys
import threading

print("Welcome to SChat!")

# schat_username = input("Choose a username: ")
schat_username = "fiver"
os.environ["SCHAT_USERNAME"] = schat_username


def get_host_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]


host_ip_address = get_host_ip_address()


def ipv4_address(address):
    try:
        socket.inet_pton(socket.AF_INET, address)
    except socket.error:
        return False
    return True


if not ipv4_address(host_ip_address):
    print("Host ip address [{host_ip_address}] is not an ipv4 address, SChat is terminated!")
    sys.exit()

host_ipv4_address = host_ip_address

print("HOST_IPV4_ADDRESS", host_ipv4_address)

os.environ["SCHAT_IPV4_ADDRESS"] = host_ipv4_address

schat_port = 12345

os.environ["SCHAT_PORT"] = str(schat_port)


def handle_connection(conn, addr):
    with conn:
        print('Connected by', addr)
        while True:
            data = conn.recv(1024).decode("ascii")
            if not data:
                break
            conn.sendall(data.encode("ascii"))


def start_listening(host_ipv4_address, schat_port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host_ipv4_address, schat_port))
        s.listen()
        while True:
            conn, addr = s.accept()
            threading.Thread(target=handle_connection, args=(conn, addr)).start()


threading.Thread(target=start_listening, args=(host_ipv4_address, schat_port)).start()


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((host_ipv4_address, schat_port))
    while True:
        message = input(":")
        if message == "exit":
            break
        s.sendall(message.encode("ascii"))
        data = s.recv(1024).decode("ascii")
        print('Received', repr(data))