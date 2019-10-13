import socket
import sys
import threading
import datetime

seperator = ","

print("Welcome to SChat!")

online_users = {}

schat_username = input("Choose a username: ")

print("SCHAT_USERNAME", schat_username)


def get_host_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    host_ip_address = s.getsockname()[0]
    s.close()
    return host_ip_address


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

schat_port = 12345


def handle(conn, addr):
    package = ""
    while True:
        data = conn.recv(1024).decode("ascii")
        if not data:
            break
        package += data

    if not package:
        conn.close()
        return

    first_seperator_index = package.find(seperator)

    name = package[1: first_seperator_index]

    second_seperator_index = package.find(seperator, first_seperator_index + 1)

    ipv4_address = package[first_seperator_index + 2: second_seperator_index]

    third_seperator_index = package.find(seperator, second_seperator_index + 2)

    if third_seperator_index == -1:
        command = package[second_seperator_index + 2: -1]

        if command == "announce":
            online_users[name] = ipv4_address
            threading.Thread(target=response, args=(ipv4_address,)).start()
            print(f"{name} is online!")
        elif command == "response":
            online_users[name] = ipv4_address
            print(f"{name} is online!")
    else:
        command = package[second_seperator_index + 2: third_seperator_index]
        if command == "message":
            message = package[third_seperator_index + 2: -1]
            print(f"{name}:{message}")
    conn.close()


def listen():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host_ipv4_address, schat_port))
        s.listen(10)
        while True:
            conn, addr = s.accept()
            threading.Thread(target=handle, args=(conn, addr)).start()


threading.Thread(target=listen).start()

def announce(target_ipv4_address):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)
        try:
            s.connect((target_ipv4_address, int(schat_port)))
            package = f"[{schat_username}, {host_ipv4_address}, announce]"
            s.sendall(package.encode("ascii"))
        except socket.timeout:
            pass
        except socket.error:
            pass


def response(target_ipv4_address):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)
        try:
            s.connect((target_ipv4_address, int(schat_port)))
            package = f"[{schat_username}, {host_ipv4_address}, response]"
            s.sendall(package.encode("ascii"))
        except socket.timeout:
            pass
        except socket.error:
            pass


def announce_all():
    host_ipv4_network_address = host_ipv4_address[:host_ipv4_address.rfind(".") + 1]
    host_identifier = int(host_ipv4_address[host_ipv4_address.rfind(".") + 1:])

    for i in range(254):
        if i == host_identifier:
            continue
        target_ipv4_address = host_ipv4_network_address + str(i)
        threading.Thread(target=announce, args=(target_ipv4_address,)).start()


threading.Thread(target=announce_all).start()

last_announcement_time = datetime.datetime.now()

print("announce/online/message/exit")

while True:
    command = input().strip()

    if command == "exit":
        sys.exit()
    elif command == "announce":
        if datetime.datetime.now() - last_announcement_time > datetime.timedelta(minutes=1):
            last_announcement_time = datetime.datetime.now()
            threading.Thread(target=announce_all).start()
        else:
            print("Rate Limited!")
    elif command == "online":
        print(online_users)
    elif command.startswith("message"):
        first_seperator_index = command.find(" ")
        second_seperator_index = command.find(" ", first_seperator_index + 1)
        target_username = command[first_seperator_index + 1: second_seperator_index]
        message = command[second_seperator_index + 1:]

        if target_username in online_users:
            target_ipv4_address = online_users[target_username]
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((target_ipv4_address, schat_port))
                package = f"[{schat_username}, {host_ipv4_address}, message, {message}]"
                s.sendall(package.encode("ascii"))
        else:
            print("No such user exists!")