import socket
import json, pickle
from bytelib import *
import requests
PLAYERS_COUNT = 0
total_players = 2
def setup():
    global PLAYERS_COUNT
    state = [{"id":i, "forward":False, "backward":False, "mleft":False, "mright":False, "connected":False} for i in range(4)]
    PLAYERS_COUNT = 0

def handle_request(request):
    global state
    global PLAYERS_COUNT
    if request == b"join":
        PLAYERS_COUNT+=1
        print(f"игроков: {PLAYERS_COUNT}, нужно для старта: {total_players}")
        return bytes([PLAYERS_COUNT, total_players])
    elif request == b"restart":
        setup()
    else:
        r = from_bytes(request)
        state[r[0]] =  {"forward":r[1], "backward":r[2], "mleft":r[3], "mright":r[4]}
        return {"id":r[0], "forward":r[1], "backward":r[2], "mleft":r[3], "mright":r[4]}

def start_server(host='127.0.0.1', port=8080):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        setup()
        s.bind((host, port))
        s.listen()
        print(f"Server started on {host}:{port}")
        while True:
            conn, addr = s.accept()
            with conn:
                #print(f"Connected by {addr}")
                data = conn.recv(1024)
                try:
                    response = handle_request(data)
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