"""
Mock exit nodes for testing rotation and cooldown logic locally.

Each mock node listens on a local port and responds to the ipify.org
IP-echo request with a fake IP address. No real VPN or internet proxy needed.

Run this FIRST, then run run_prototype.py in a second terminal.

    python mock_nodes.py
"""
import json
import socket
import struct
import threading

# (port, fake_exit_ip) — one per simulated node
MOCK_NODES = [
    (1080, "203.0.113.10"),   # fake "US" exit
    (1081, "203.0.113.20"),   # fake "UK" exit
    (1082, "203.0.113.30"),   # fake "DE" exit
]

IPIFY_RESPONSE = b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n"


def handle_socks5(conn: socket.socket, fake_ip: str) -> None:
    try:
        # SOCKS5 handshake
        conn.recv(2)           # version + nmethods
        conn.recv(1)           # methods byte
        conn.sendall(b"\x05\x00")  # no auth

        # SOCKS5 request
        header = conn.recv(4)
        if len(header) < 4:
            return
        atyp = header[3]
        if atyp == 0x01:       # IPv4
            conn.recv(4)
        elif atyp == 0x03:     # domain
            length = conn.recv(1)[0]
            conn.recv(length)
        conn.recv(2)           # port

        # Reply: success, bound to 0.0.0.0:0
        conn.sendall(b"\x05\x00\x00\x01\x00\x00\x00\x00\x00\x00")

        # Read the HTTP request (we don't care what it is)
        data = b""
        while b"\r\n\r\n" not in data:
            chunk = conn.recv(4096)
            if not chunk:
                break
            data += chunk

        # Always reply with the fake IP for this node
        body = json.dumps({"ip": fake_ip}).encode()
        response = (
            b"HTTP/1.1 200 OK\r\n"
            b"Content-Type: application/json\r\n"
            b"Content-Length: " + str(len(body)).encode() + b"\r\n"
            b"\r\n" + body
        )
        conn.sendall(response)
    except Exception:
        pass
    finally:
        conn.close()


def serve(port: int, fake_ip: str) -> None:
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("127.0.0.1", port))
    srv.listen(10)
    print(f"Mock node on 127.0.0.1:{port}  →  fake exit IP {fake_ip}")
    while True:
        conn, _ = srv.accept()
        threading.Thread(target=handle_socks5, args=(conn, fake_ip), daemon=True).start()


if __name__ == "__main__":
    threads = []
    for port, fake_ip in MOCK_NODES:
        t = threading.Thread(target=serve, args=(port, fake_ip), daemon=True)
        t.start()
        threads.append(t)

    print("\nAll mock nodes running. Press Ctrl+C to stop.")
    print("Now run in a second terminal:  python run_prototype.py\n")

    try:
        for t in threads:
            t.join()
    except KeyboardInterrupt:
        print("Stopped.")
