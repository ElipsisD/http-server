import socket
import sys
import os
import gzip

CRLF = "\r\n"
SUCCESS_STATUS_LINE = "HTTP/1.1 200 OK"
NOT_FOUND = b"HTTP/1.1 404 Not Found\r\n\r\n"
CREATED_RESPONSE = b"HTTP/1.1 201 Created\r\n\r\n"
ALLOWABLE_ENCODING = "gzip"


def main():
    with socket.create_server(("localhost", 4221)) as server_socket:
        while True:
            conn, addr = server_socket.accept()
            handle_request(conn)


def handle_request(conn):
    response = conn.recv(1024)
    status_line, *headers, response_body = response.decode().split(CRLF)
    method, url_path, protocol = status_line.split()
    headers_dict = {res[0]: res[1] for j in headers[:-1] if (res := j.split(": "))}
    match url_path.split("/"):
        case ["", ""]:
            conn.sendall((SUCCESS_STATUS_LINE + CRLF + CRLF).encode())
        case ["", "echo", echo_string]:
            encoding = (
                resolve_encoding_mode(encoding_mode) if (encoding_mode := headers_dict.get("Accept-Encoding")) else None
            )
            if encoding == "gzip":
                echo_string = gzip.compress(echo_string.encode())
            else:
                echo_string = echo_string.encode()
            prefix = get_response_prefix(echo_string, encoding=encoding)
            response = (prefix + CRLF).encode() + echo_string
            conn.sendall(response)
        case ["", "user-agent", *_]:
            user_agent = headers_dict["User-Agent"]
            prefix = get_response_prefix(user_agent)
            response = prefix + CRLF + user_agent
            conn.sendall(response.encode())
        case ["", "files", filename]:
            handle_file_request(conn, filename, method, response_body)
        case _:
            conn.sendall(NOT_FOUND)
    conn.close()


def handle_file_request(conn, filename, method, response_body):
    directory = sys.argv[2]
    match method:
        case "GET":
            if os.path.exists(directory + filename):
                with open(directory + filename) as f:
                    file_data = f.read()
                    prefix = get_response_prefix(file_data, content_type="application/octet-stream")
                response = prefix + CRLF + file_data
                conn.sendall(response.encode())
            else:
                conn.sendall(NOT_FOUND)
        case "POST":
            with open(directory + filename, "w") as f:
                f.write(response_body)
                conn.sendall(CREATED_RESPONSE)


def get_response_prefix(content: str, *, content_type: str | None = None, encoding: str | None = None) -> str:
    if content_type is None:
        content_type = "text/plain"
    response_headers = {
        "Content-Type": content_type,
        "Content-Length": len(content),
    }
    if encoding:
        response_headers["Content-Encoding"] = encoding
    response_prefix = CRLF.join(
        [
            SUCCESS_STATUS_LINE,
            CRLF.join([f"{k}: {v}" for k, v in response_headers.items()]) + CRLF,
        ]
    )
    return response_prefix


def resolve_encoding_mode(encoding_data: str) -> str | None:
    encodings = encoding_data.split(", ")
    for encoding in encodings:
        if encoding == ALLOWABLE_ENCODING:
            return encoding
    return None


if __name__ == "__main__":
    main()
