import socket

CRLF = "\r\n"
SUCCESS_STATUS_LINE = "HTTP/1.1 200 OK"


def main():
    with socket.create_server(("localhost", 4221)) as server_socket:
        while True:
            conn, addr = server_socket.accept()
            response = conn.recv(1024)
            status_line, *headers, response_body = response.decode().split(CRLF)
            method, url_path, protocol = status_line.split()

            headers_dict = {res[0]: res[1] for j in headers[:-1] if (res := j.split(": "))}

            match url_path.split("/"):
                case ["", ""]:
                    conn.sendall((SUCCESS_STATUS_LINE + CRLF + CRLF).encode())
                case ["", "echo", *_]:
                    echo_string = url_path.split("echo/")[-1]
                    prefix = get_response_prefix(echo_string)
                    response = prefix + CRLF + echo_string
                    conn.sendall(response.encode())
                case ["", "user-agent", *_]:
                    user_agent = headers_dict["User-Agent"]
                    prefix = get_response_prefix(user_agent)
                    response = prefix + CRLF + user_agent
                    conn.sendall(response.encode())
                case _:
                    conn.sendall(b"HTTP/1.1 404 Not Found\r\n\r\n")

            conn.close()


def get_response_prefix(content: str) -> str:
    response_headers = {
        "Content-Type": "text/plain",
        "Content-Length": len(content),
    }
    response_prefix = CRLF.join(
        [
            SUCCESS_STATUS_LINE,
            CRLF.join([f"{k}: {v}" for k, v in response_headers.items()]) + CRLF,
        ]
    )
    return response_prefix


if __name__ == "__main__":
    main()
