import socket
import pickle


def send_request(host='127.0.0.1', port=8080, request=None):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        if request is not None:
            s.sendall(pickle.dumps(request))
        data = s.recv(1024)
        return pickle.loads(data)
while True:
    print(send_request(request=input(">>> ")))
