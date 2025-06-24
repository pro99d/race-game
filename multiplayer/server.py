import socket
import json

# --- Глобальные переменные ---
PLAYERS_COUNT = 0
TOTAL_PLAYERS = 4 # Можно изменить, если нужно
state = {}


# --- Функции ---

def setup():
    """Инициализирует или сбрасывает состояние игры."""
    global PLAYERS_COUNT
    global state
    # Создаем "слоты" для каждого возможного игрока
    state = [
        {
            "id": i,
            "Connected": False,
            "forward": False,
            "backward": False,
            "mleft": False,
            "mright": False,
        }
        for i in range(TOTAL_PLAYERS)
    ]
    PLAYERS_COUNT = 0
    print("--- Server state reset and initialized ---")


def handle_request(request_data):
    """Обрабатывает один запрос от клиента (в формате словаря Python)."""
    global state
    global PLAYERS_COUNT

    action = request_data.get("action")

    if action == "join":
        player_id = -1
        # Ищем первый свободный слот для нового игрока
        for i in range(len(state)):
            if not state[i]["Connected"]:
                player_id = i
                break
        
        if player_id != -1:
            state[player_id]["Connected"] = True
            PLAYERS_COUNT += 1
            print(f"Player {player_id} joined. Total connected: {PLAYERS_COUNT}")
            # Возвращаем новому игроку его ID и текущее состояние всех игроков
            return {"status": "joined", "id": player_id, "state": state}
        else:
            print("A player tried to join, but the server is full.")
            return {"error": "Server is full"}

    elif action == "input":
        player_id = request_data.get("id")
        keys = request_data.get("keys")

        # Проверяем, что ID и клавиши пришли и ID корректен
        if player_id is not None and keys is not None and 0 <= player_id < len(state):
            # Обновляем только состояние клавиш для данного игрока
            state[player_id].update(keys)
            # В ответ отправляем всем обновленное полное состояние игры
            return {"status": "update", "state": state}
        else:
            return {"error": "Invalid input data"}

    elif action == "restart":
        setup()
        return {"status": "restarted"}
        
    else:
        return {"error": "Unknown action"}


def start_server(host="0.0.0.0", port=8080):
    """Главная функция запуска сервера."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        setup()
        s.bind((host, port))
        s.listen()
        print(f"Server started on {host}:{port}. Waiting for connections...")

        while True:
            try:
                conn, addr = s.accept()
                with conn:
                    # print(f"Connected by {addr}")
                    data = conn.recv(1024)
                    if not data:
                        continue # Пропускаем пустые запросы

                    # Декодируем байты в строку, затем парсим JSON в словарь
                    request_dict = json.loads(data.decode("utf-8"))
                    
                    # Обрабатываем запрос
                    response_dict = handle_request(request_dict)
                    
                    # Кодируем ответный словарь в JSON-строку, затем в байты
                    response_bytes = json.dumps(response_dict).encode("utf-8")
                    
                    conn.sendall(response_bytes)

            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                print(f"Error decoding request from {addr}: {e}")
                # Можно отправить ошибку клиенту, если это необходимо
            except ConnectionResetError:
                print(f"Connection with {addr} was forcibly closed.")
                # Здесь можно добавить логику для отключения игрока
            except KeyboardInterrupt:
                print("\nServer is shutting down.")
                break
            except Exception as e:
                print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    start_server() 
