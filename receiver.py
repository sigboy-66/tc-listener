import socket
import sys
from datetime import datetime

if len(sys.argv) != 2:
    print("Usage: python receiver.py <log_file_path>")
    sys.exit(1)

log_file_path = sys.argv[1]
ip = '0.0.0.0'
port = 4445

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.bind((ip, port))
    server_socket.listen()
    print(f"Server listening on {ip}:{port}")

    connection, address = server_socket.accept()
    with connection, open(log_file_path, 'a') as log_file:
        print(f"Connected by {address}")
        while True:
            heartbeat = connection.recv(1024)
            if not heartbeat:
                print("Connection closed by the sender.")
                break
            message = heartbeat.decode()
            timestamp = datetime.now().isoformat()
            log_heartbeat = f"{timestamp} - {address[0]}:{address[1]} - {message}\n"
            print(log_heartbeat.strip())
            log_file.write(log_heartbeat)
            log_file.flush()