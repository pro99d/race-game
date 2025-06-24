import flet as ft
import subprocess
import threading
import socket
import time

def send_command_to_server(cmd):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(("127.0.0.1", 9090))
            s.sendall(cmd.encode())
            s.settimeout(2)
            response = s.recv(4096).decode(errors="ignore")
            return response
    except Exception as e:
        return f"Ошибка отправки команды на сервер: {e}\n"

def process_terminal(label, command, is_server=False):
    # Основное текстовое поле для вывода
    output = ft.TextField(
        multiline=True, read_only=True, expand=True, height=350, label=f"Лог {label.lower()}"
    )
    # Поле для ввода команд
    input_field = ft.TextField(label="Введите команду", expand=True)
    # Кнопки
    send_btn = ft.ElevatedButton("Отправить", height=50, width=120)
    # Кнопка будет менять текст и действие
    start_stop_btn = ft.ElevatedButton(f"Запустить {label}", height=60, width=250, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12)))

    proc = {"p": None}  # Используем словарь для замыкания

    def update_btn():
        if proc["p"] is not None and proc["p"].poll() is None:
            start_stop_btn.text = f"Остановить {label}"
        else:
            start_stop_btn.text = f"Запустить {label}"
        start_stop_btn.update()

    def start_process(e=None):
        if proc["p"] is not None and proc["p"].poll() is None:
            # Остановить процесс
            proc["p"].terminate()
            output.value += f"{label} остановлен!\n"
            output.update()
            update_btn()
            return
        # Запустить процесс
        # -u для отключения буфера
        cmd = command.copy()
        if cmd[0].startswith("python"):
            cmd.insert(1, "-u")
        proc["p"] = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            stdin=subprocess.PIPE if not is_server else None,
            text=True,
            bufsize=1,
        )
        output.value += f"{label} запущен!\n"
        output.update()
        update_btn()
        threading.Thread(target=read_stdout, daemon=True).start()
        threading.Thread(target=monitor_proc, daemon=True).start()

    def read_stdout():
        # Чтение по строкам (работает с -u и flush=True)
        for line in proc["p"].stdout:
            output.value += line
            output.update()
        update_btn()

    def monitor_proc():
        # Следим за внешним завершением процесса
        while proc["p"] is not None and proc["p"].poll() is None:
            time.sleep(0.5)
        update_btn()

    def send_command(e=None):
        cmd = input_field.value.strip()
        if not cmd:
            return
        if is_server:
            response = send_command_to_server(cmd)
            if response:
                output.value += f"> {cmd}\n{response}\n"
                output.update()
        elif proc["p"] and proc["p"].poll() is None:
            try:
                proc["p"].stdin.write(cmd + "\n")
                proc["p"].stdin.flush()
            except Exception as ex:
                output.value += f"Ошибка отправки команды: {ex}\n"
                output.update()
        input_field.value = ""
        input_field.update()

    start_stop_btn.on_click = start_process
    send_btn.on_click = send_command
    input_field.on_submit = send_command

    return ft.Column([
        ft.Row([
            start_stop_btn
        ], alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.CENTER),
        output,
        ft.Row([input_field, send_btn], alignment=ft.MainAxisAlignment.CENTER)
    ], expand=True)


def main(page: ft.Page):
    page.title = "Race Game Launcher"
    page.window_width = 1000
    page.window_height = 600
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = (255, 255, 255)#ft.colors.WHITE

    # Терминалы для сервера и клиента
    server_terminal = process_terminal("Сервер", ["python3", "multiplayer/server.py"], is_server=True)
    client_terminal = process_terminal("Клиент", ["python3", "main.py"], is_server=False)

    # Вкладки
    tabs = ft.Tabs(
        selected_index=0,
        tabs=[
            ft.Tab(text="Сервер", content=server_terminal),
            ft.Tab(text="Клиент", content=client_terminal),
        ],
        expand=True,
        indicator_color=(0, 0, 255),#ft.colors.BLUE,
        label_color=(0, 0, 0),#ft.colors.BLACK,
    )

    # Заголовок и оформление
    page.add(
        ft.Column([
            ft.Text("RACE GAME LAUNCHER", size=32, weight=ft.FontWeight.BOLD, color=(0, 0, 255), text_align=ft.TextAlign.CENTER),
            tabs
        ], expand=True, alignment=ft.MainAxisAlignment.START)
    )

if __name__ == "__main__":
    ft.app(target=main)
