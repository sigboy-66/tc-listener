import subprocess
import tempfile
import time
import os
import socket
import pytest

receiver_exe = "receiver.py"
sender_exe = "sender.py"
HOST = "127.0.0.1"
PORT = 5000

def wait_for_log_file(path, timeout=10):
    """Wait for log file to be created and contain data."""
    start = time.time()
    while time.time() - start < timeout:
        if os.path.exists(path) and os.path.getsize(path) > 0:
            return True
        time.sleep(0.5)
    return False


def is_port_open(host, port):
    """Check if a TCP port is open."""
    try:
        with socket.create_connection((host, port), timeout=1):
            return True
    except Exception:
        return False


def test_heartbeat_logging():
    """Test basic heartbeat logging to file."""
  #  with tempfile.NamedTemporaryFile(delete=False) as tmp:
  #      log_path = tmp.name
    log_file = "listener.log"
    server = subprocess.Popen(
        ["python", receiver_exe, log_file],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # Wait for server to be ready
    time.sleep(2.5)

    client = subprocess.Popen(
        ["python", sender_exe],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    time.sleep(6)  # Let at least one heartbeat be sent

    client.terminate()
    client.wait(timeout=5)

    server.terminate()
    server.wait(timeout=5)

    assert wait_for_log_file(log_file), "Log file was not created or remained empty"

    with open(log_file) as f:
        contents = f.read()
        assert "HEARTBEAT" in contents
        assert "T" in contents  # ISO timestamp format

    os.remove(log_file)

def test_sender_receives_all_heartbeats():
    """Send 5 heart beats see if 5 are logged"""
    log_file = "listener.log"
    result = subprocess.run(
        ["python", receiver_exe, log_file],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    time.sleep(2.5)
    client = subprocess.Popen(
        ["python", sender_exe, 5],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    time.sleep(27.0)

    count = 0
    with open(log_file, 'r') as file:
        for line in file:
            print{line}
            assert f"HEARTBEAT {count}" in line
            count += 1

    assert count == 5
    os.remove(log_file)

#def test_missing_log_path():
#    """Test server fails if log path is missing."""
#    result = subprocess.run(
#        ["python", SERVER_SCRIPT],
#        stdout=subprocess.PIPE,
#        stderr=subprocess.PIPE,
#        text=True
#    )
#    assert "Usage" in result.stdout or "Usage" in result.stderr


#def test_client_no_server():
#    """Client should fail to connect if server is down."""
#    result = subprocess.run(
#        ["python", sender_exe],
#        stdout=subprocess.PIPE,
#        stderr=subprocess.PIPE,
#        text=True,
#        timeout=5
 #   )
 #   assert "Connection refused" in result.stderr or "Failed to connect" in result.stderr or "ConnectionResetError" in result.stderr or result.returncode != 0

#def test_log_permission_error():
#    """Test server exits if it cannot write to log path."""
#    restricted_path = "/root/forbidden_log.txt" if os.name != "nt" else "C:\\Windows\\System32\\forbidden_log.txt"

 #   server = subprocess.Popen(
#        ["python", receiver_exe, restricted_path],
#        stdout=subprocess.PIPE,
 #       stderr=subprocess.PIPE,
 #       text=True
 #   )
 #   time.sleep(1)
  #  server.poll()
  #  assert server.returncode is not None, "Server did not exit as expected"
  #  out, err = server.communicate()
  #  assert "Permission" in err or "denied" in err or server.returncode != 0
