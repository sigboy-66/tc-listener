import subprocess
import time
import os
import pytest
from datetime import datetime

receiver_exe = "receiver.py"
sender_exe = "sender.py"


def kill_processes(sender, receiver):
    """Kill the sender and receiver"""
    sender.terminate()
    sender.wait(timeout=5)
    receiver.terminate()
    receiver.wait(timeout=5)

def get_time_stamp(receiver_log_line):
    """
    :param sender_log_line: log line from the senders log
    :return: iso time stamp of when the the client send the heartbeat
    """
    index = receiver_log_line.find("at ")
    time_stamp_index = index + 3
    time_stamp = receiver_log_line[time_stamp_index:].replace("\n", "")
    return time_stamp

def get_correct_pyhthon():
    """select python 2 if not windows"""
    if os.name != "nt":
        return "python3"
    else:
        return "python"

def test_heartbeat_logging():
    """Test basic heartbeat logging to file."""
    log_file = "listener1.log"
    server = subprocess.Popen(
        [get_correct_pyhthon(), receiver_exe, log_file],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # Wait for server to be ready
    time.sleep(2.5)
    print(f"Server.poll() is {server.poll()}")
    client = subprocess.Popen(
        [get_correct_pyhthon(), sender_exe],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    time.sleep(6)  # Let at least one heartbeat be sent

    kill_processes(client, server)

    with open(log_file) as f:
        contents = f.read()
        assert "HEARTBEAT" in contents
        assert "T" in contents  # ISO timestamp format
    print(f"Server.poll() is {server.poll()}")
    os.remove(log_file)

def test_sender_receives_all_heartbeats():
    """Send 5 heart beats see if 5 are logged"""
    log_file = "listener2.log"
    server = subprocess.Popen(
        [get_correct_pyhthon(), receiver_exe, log_file],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    print("sleep 2.5 sec for receiver to be up")
    time.sleep(2.5)
    client = subprocess.Popen(
        [get_correct_pyhthon(), sender_exe, "5"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    print("Waiting for sender to stop!!!")
    # wait for the sender to terminate
    while client.poll() is None:
        print("Sender is still running")
        time.sleep(5.0)
    print("Analyzing log file")
    count = 0
    # validate getting the packets in order
    with open(log_file, 'r') as file:
        for line in file:
            assert f"HEARTBEAT {count}" in line
            count += 1

    assert count == 5

    # make sure sender receiver dead before moving on
    kill_processes(client, server)

    os.remove(log_file)


def test_receiver_heartbeats_received_timestamped_every_5_seconds_from_sender():
    """Validate a heart beat was received was time stamped every 5 seconds from the sender"""
    log_file = "listener3.log"

    server = subprocess.Popen(
        [get_correct_pyhthon(), receiver_exe, log_file],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    time.sleep(2.5)
    client = subprocess.Popen(
        [get_correct_pyhthon(), sender_exe, "5"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    print("Waiting for sender to stop!!!")
    # wait for the sender to terminate
    while client.poll() is None:
        print("Sender is still running")
        time.sleep(5.0)
    print("Analyzing log file")
    count = 0
    # Validate that the consecutive timestamps sent from the sender are 5 seconds apart
    with open(log_file, 'r') as file:
        for line in file:
            if count == 0:
                prev_timestamp = get_time_stamp(line)
            else:
                # calculate the time difference between timestamps send from the sender to 5 seconds
                curr_timestamp = get_time_stamp(line) # fetch the senders timestamp out of the receivers log
                time_delta = datetime.fromisoformat(curr_timestamp) - datetime.fromisoformat(prev_timestamp)
                print(f"Time dela is {time_delta.total_seconds()}")
                assert round(time_delta.total_seconds()) == 5
                prev_timestamp = curr_timestamp
            count += 1

    # make sure sender receiver dead before moving on
    kill_processes(client, server)

    os.remove(log_file)

def test_missing_log_path_to_reciever():
    """Test server fails if log path is missing."""
    result = subprocess.run(
        [get_correct_pyhthon(), receiver_exe],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    assert "Usage" in result.stdout or "Usage" in result.stderr


def test_sender_no_reciever():
    """Sender should fail to connect if server is down."""
    result = subprocess.run(
        [get_correct_pyhthon(), sender_exe],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=5
       )
    assert "Connection refused" in result.stderr or "Failed to connect" in result.stderr or "ConnectionResetError" in result.stderr or result.returncode != 0

def test_log_permission_error():
    """Test server exits if it cannot write to log path."""
    if os.name != "nt":
        restricted_path = "/root/forbidden_log.txt"
    else:
        restricted_path = "C:\\Windows\\System32\\forbidden_log.txt"

    server = subprocess.Popen(
        [get_correct_pyhthon(), receiver_exe, restricted_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    time.sleep(1)
    return_code = server.poll()
    assert return_code is not None, "receiver did not exit as expected"
    out, err = server.communicate()
    assert "Permission" in err or "denied" in err or server.returncode != 0
    server.terminate()
    server.wait(timeout=5)

