# Uncomment this to pass the first stage
import socket


def main():
    with socket.create_server(("localhost", 4221)) as server_socket:
        while True:
            conn, addr = server_socket.accept()
            response = conn.recv(1024)
            url_path = response.decode().split("\r\n")[0].split()[1]
            if url_path == "/":
                conn.sendall(b"HTTP/1.1 200 OK\r\n\r\n")
            else:
                conn.sendall(b"HTTP/1.1 404 Not Found\r\n\r\n")
            conn.close()


if __name__ == "__main__":
    main()
