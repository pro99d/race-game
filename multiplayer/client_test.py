import socket
import pickle
from bytelib import *

def send_request(host='127.0.0.1', port=8080, request=None):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        if request is not None:
            s.sendall(request)
        data = s.recv(1024)
        return pickle.loads(data)
n = 1
f, t, i, d, = 1,0,1,1
send_request(request=to_bytes(n, f, t, i, d))
