import socket
import json


def send_request(host='127.0.0.1', port=65432, request=None):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        if request is not None:
            s.sendall(json.dumps(request).encode('utf-8'))
        data = s.recv(1024).decode('utf-8')
        return json.loads(data)
state = {
        'id':1,
        'sprite': "player_sprite",
        'speed': 0,
        'angle_speed': 0,
        'current_angle': 90,
        'forward': False,
        'backward': False,
        'mleft': False,
        'mright': False,
        'collisions_to_explosion': 10,
        'explosion_time': 0.0,
        'exploded': False,
        'laps': 0,
        'checkpoint': False
    }

if __name__ == "__main__":
    # Примеры запросов

    response = send_request(request="join")
    state["id"] = response["length"]+1
    # Запрос состояния
    # Обновление состояния
    response = send_request(request=state)
    print("Update State:", response)

    response = send_request(request="request")
    print("Request State:", response)
