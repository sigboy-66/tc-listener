import socket
import sys
from datetime import datetime

if len(sys.argv) != 2:
    print("Usage: python receiver.py <log_file>")
    sys.exit(1)

log_file = sys.argv[1]
ip = '0.0.0.0'
port = 4446

try:
    heartbeat_log = open(log_file, 'a')
except(IOError) as error:
    print(f"Error: Can't write to {log_file}: {error}")
    sys.exit(1)

with heartbeat_log, socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.bind((ip, port))
    server_socket.listen()
    print(f"Listening on {ip}:{port}")

    connection, address = server_socket.accept()
    with connection:
        print(f"Connected by {address}")
        # Loop until sender breaks connection
        while True:
            heartbeat = connection.recv(1024)
            if not heartbeat:
                print("Connection closed by the sender.")
                break
            message = heartbeat.decode()
            timestamp = datetime.now().isoformat()
            log_heartbeat = f"{timestamp} - {address[0]}:{address[1]} - {message}\n"
            print(log_heartbeat.strip())
            heartbeat_log.write(log_heartbeat)
            heartbeat_log.flush()