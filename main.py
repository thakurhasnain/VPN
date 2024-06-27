import socket
import threading
import signal
import sys

# Proxy server configuration
proxy_host = '127.0.0.1'
proxy_port = 8888
# Destination server configuration
destination_host = 'www.example.com'
destination_port = 80


def handle_client(client_socket):
    # Connecting to destination server
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.connect((destination_host, destination_port))
    # Forwarding Data
    try:
        while True:
            # Receive Data From client
            client_data = client_socket.recv(4096)
            if len(client_data) == 0:
                break
            # Forwarding data to the server
            server_socket.send(client_data)
            # Receiving data from the server
            server_data = server_socket.recv(4096)
            if len(server_data) == 0:
                break
            # Forwarding data to the client
            client_socket.send(server_data)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Closing the connection
        client_socket.close()
        server_socket.close()


def start_proxy():
    global proxy
    # Create socket object
    proxy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Bind the socket to the address and port
    proxy.bind((proxy_host, proxy_port))
    # Listen for incoming connections
    proxy.listen(5)
    print(f"Proxy server is listening on {proxy_host}:{proxy_port}")

    while True:
        client_socket, addr = proxy.accept()
        print(f"Accepted connection from {addr[0]}:{addr[1]}")
        # Start a new thread to handle the client connection
        client_handle = threading.Thread(target=handle_client, args=(client_socket,))
        client_handle.start()


def signal_handler(sig, frame):
    print('Shutting down proxy server...')
    proxy.close()
    sys.exit(0)


def test_proxy():
    # Create a socket to connect to the proxy
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((proxy_host, proxy_port))

    # Send an HTTP GET request through the proxy
    request = b"GET / HTTP/1.1\r\nHost: www.example.com\r\n\r\n"
    client_socket.send(request)

    # Receive the response
    response = client_socket.recv(4096)
    print("Response from proxy:")
    print(response.decode())

    # Close the connection
    client_socket.close()


if __name__ == "__main__":
    # Handle graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)

    # Start the proxy server in a separate thread
    proxy_thread = threading.Thread(target=start_proxy)
    proxy_thread.start()

    # Give the proxy server a moment to start up
    import time

    time.sleep(1)

    # Run the test function to check if the proxy server works
    test_proxy()
