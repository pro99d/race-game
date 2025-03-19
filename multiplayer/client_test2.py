import socket
from pickle import dumps

# Создаем сокет
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Подключаемся к серверу
server_address = ('localhost', 8080)
client_socket.connect(server_address)

# Отправляем данные
data_to_send = {"id": 1, "name": "Client 1"}
client_socket.sendall(dumps(data_to_send))

# Получаем ответ от сервера
response = client_socket.recv(4096)
print("Ответ сервера:", response)

# Закрываем соединение
client_socket.close()