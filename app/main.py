import socket

CRLF = "\r\n"


def main():
    with socket.create_server(("localhost", 4221)) as server_socket:
        while True:
            conn, addr = server_socket.accept()
            response = conn.recv(1024)
            status_line, *headers, response_body = response.decode().split(CRLF)
            method, url_path, protocol = status_line.split()

            success_status_line = "HTTP/1.1 200 OK"

            if url_path == "/":
                conn.sendall((success_status_line + CRLF + CRLF).encode())
            elif url_path.startswith("/echo"):
                url_string = url_path.split("echo/")[-1]
                response_headers = {
                    "Content-Type": "text/plain",
                    "Content-Length": len(url_string),
                }
                response = CRLF.join(
                    [
                        success_status_line,
                        CRLF.join([f"{k}: {v}" for k, v in response_headers.items()]) + CRLF,
                        url_string
                    ]
                )
                conn.sendall(response.encode())
            else:
                conn.sendall(b"HTTP/1.1 404 Not Found\r\n\r\n")

            conn.close()


if __name__ == "__main__":
    main()
