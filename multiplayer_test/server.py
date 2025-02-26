import socket
import json, pickle

from fontTools.ttLib.ttGlyphSet import LerpGlyph

# Состояние сервера (словарь с ID пользователей)
state = {}

def handle_request(request):
    global state
    if isinstance(request, dict):
        user_id = request.get("id")
        if user_id is None:
            return {"error": "ID is required"}

        # Обновление состояния при получении словаря
        state[user_id] = request
        return {"status": "State updated", "state": state}

    elif request == "request":
        # Отправка текущего состояния
        return {"status": "State requested", "state": state}

    elif request == "join":
        # Отправка длины состояния
        return {"status": "Join requested", "length": len(state)}
    else:
        return {"error": "Invalid request"}


def start_server(host='127.0.0.1', port=8080):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        print(f"Server started on {host}:{port}")
        while True:
            conn, addr = s.accept()
            with conn:
                print(f"Connected by {addr}")
                data = conn.recv(1024)
                try:
                    request = pickle.loads(data)
                    response = handle_request(request)
                    print(response)
                    conn.sendall(pickle.dumps(response))
                except json.JSONDecodeError:
                    conn.sendall(pickle.dumps({"error": "Invalid JSON"}).encode('utf-8'))
                except KeyboardInterrupt:
                    break
                #finally:
                    #print(len(state))


if __name__ == "__main__":
    start_server()
