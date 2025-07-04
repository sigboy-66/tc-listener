import socket
import time
import sys
from datetime import datetime
from time import thread_time_ns


loop_count = 1000
if len(sys.argv) > 1:
    loop_count = int(sys.argv[1])


receiver_ip = '127.0.0.1'  # Change to server's IP if needed
receiver_port = 4446

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
    client_socket.connect((receiver_ip, receiver_port))
    print(f"Connected to server at {receiver_ip}:{receiver_port}")

    try:
        for heartbeat_num in range(loop_count):
            timestamp = datetime.now().isoformat()
            heartbeat = f"HEARTBEAT {heartbeat_num} at {timestamp}"
            client_socket.sendall(heartbeat.encode())
            print(f"Sent: {heartbeat}")
            time.sleep(5)
    except KeyboardInterrupt:
        print("Client stopped.")