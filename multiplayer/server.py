import socket
import json, pickle
from bytelib import *
# Состояние сервера (словарь с ID пользователей)
state = {}

def handle_request(request):
    global state
    r = request
    return {"id":r[0], "forward":r[1], "backward":r[2], "mleft":r[3], "mright":r[4]}

def start_server(host='127.0.0.1', port=8080):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        print(f"Server started on {host}:{port}")
        while True:
            conn, addr = s.accept()
            with conn:
                #print(f"Connected by {addr}")
                data = conn.recv(1024)
                try:
                    request = from_bytes(data) 
                    response = handle_request(request)
                    state[response["id"]] = response
                    r = [to_bytes(i["id"], i["forward"], i["backward"], i["mleft"], i["mright"]) for i in state.values()]
                    #print(response)
                    conn.sendall(pickle.dumps(response))
                except json.JSONDecodeError:
                    conn.sendall(pickle.dumps({"error": "Invalid JSON"}).encode('utf-8'))
                except KeyboardInterrupt:
                    break
                #finally:
                    #print(len(state))
if __name__ == "__main__":
    start_server()