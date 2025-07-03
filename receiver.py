import socket
import sys
from datetime import datetime


def receiver():
    if len(sys.argv) != 2:
        print("Usage: python receiver.py <log_file_path>")
        sys.exit(1)

    log_file_path = sys.argv[1]
    HOST = '0.0.0.0'
    PORT = 4444

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        print(f"Server listening on {HOST}:{PORT}")

        connection, address = server_socket.accept()
        with connection, open(log_file_path, 'a') as log_file:
            print(f"Connected by {address}")
            while True:
                data = connection.recv(1024)
                if not data:
                    print("Connection closed by client.")
                    break
                message = data.decode()
                timestamp = datetime.now().isoformat()
                log_entry = f"{timestamp} - {address[0]}:{address[1]} - {message}\n"
                print(log_entry.strip())
                log_file.write(log_entry)
                log_file.flush()


if __name__ == "__main__":
    receiver()