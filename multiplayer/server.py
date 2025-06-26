import socket
import json
import threading

# Глобальное состояние игры
players_state = []
MAX_PLAYERS = 4
running = True

def setup_state():
    """Инициализирует или сбрасывает состояние игры."""
    global players_state
    players_state = [
        {
            "id": i,
            "connected": False,
            "forward": False,
            "backward": False,
            "mleft": False,
            "mright": False,
        }
        for i in range(MAX_PLAYERS)
    ]
    print("Состояние сервера сброшено.", flush=True)

def handle_game_request(data: dict) -> dict:
    """Обрабатывает игровые запросы (присоединение, ввод)."""
    global players_state
    action = data.get("action")

    if action == "join":
        for player in players_state:
            if not player["connected"]:
                player["connected"] = True
                print(f"Игрок {player['id']} присоединился.", flush=True)
                return {"id": player["id"], "state": players_state}
        return {"error": "Сервер полон."}

    elif action == "input":
        player_id = data.get("id")
        keys = data.get("keys")
        if player_id is not None and keys is not None and 0 <= player_id < MAX_PLAYERS:
            players_state[player_id].update(keys)
            return {"status": "update", "state": players_state}
        return {"error": "Неверные данные для 'input'."}

    return {"error": "Неизвестное действие."}

def handle_command_request(command: str) -> str:
    """Обрабатывает команды управления сервером."""
    global running, total_players
    
    if command.startswith("/"):
        cmd_parts = command[1:].split()
        main_cmd = cmd_parts[0]

        if main_cmd == "stop":
            running = False
            return "Сервер остановлен." 
        elif main_cmd == "set" and len(cmd_parts) > 2 and cmd_parts[1] == "players":
            try:
                num = int(cmd_parts[2])
                if 1 <= num <= MAX_PLAYERS:
                    return f"Количество игроков установлено на {num} (требуется перезапуск для применения)."
                return "Ошибка: количество игроков должно быть от 1 до 4."
            except ValueError:
                return "Ошибка: неверное число игроков."
        
        elif main_cmd == "help":
            return """
            /stop - остановить сервер
            /set players <1-4> - установить кол-во игроков
            /help - это сообщение
            """
    else:
        return "Неизвестная команда. Используйте /help."
    return "Команда должна начинаться с /"


# --- Потоки для серверов ---

def command_server_thread():
    """Поток для обработки команд от лаунчера."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("127.0.0.1", 9090))
        s.listen()
        print("Командный сокет запущен на 127.0.0.1:9090", flush=True)
        while running:
            try:
                conn, addr = s.accept()
                with conn:
                    data = conn.recv(1024).decode().strip()
                    if data:
                        response = handle_command_request(data)
                        conn.sendall(response.encode())
            except OSError:
                break # Сокет был закрыт

def game_server_thread():
    """Поток для обработки игровых данных от клиентов."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("0.0.0.0", 8080))
        s.listen()
        print("Игровой сервер запущен на 0.0.0.0:8080", flush=True)
        while running:
            conn, addr = s.accept()
            with conn:
                data = conn.recv(4096)
                if not data:
                    continue
                try:
                    request_dict = json.loads(data.decode())
                    response_dict = handle_game_request(request_dict)
                except (json.JSONDecodeError, UnicodeDecodeError):
                    response_dict = {"error": "Неверный формат запроса (не JSON)."}
                    conn.sendall(json.dumps(response_dict).encode())
                except OSError:
                    break # Сокет был закрыт

def main():
    """
    основная функция запуска сервера
    """
    global running
    setup_state()
    
    cmd_thread = threading.Thread(target=command_server_thread, daemon=True)
    game_thread = threading.Thread(target=game_server_thread, daemon=True)
    
    cmd_thread.start()
    game_thread.start()

    # Ждем, пока сервер не будет остановлен командой /stop
    while running:
        try:
            # Даем потокам работать
            cmd_thread.join(0.1)
            game_thread.join(0.1)
        except KeyboardInterrupt:
            running = False
            
    print("Завершение работы сервера...", flush=True)
    # Потоки-демоны завершатся автоматически


if __name__ == "__main__":
    main()
