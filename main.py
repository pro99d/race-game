import arcade
import arcade.gui
from arcade.experimental.uislider import UISlider
from arcade.gui import UIManager, UIAnchorWidget, UILabel, UIOnClickEvent
from arcade.gui.events import UIOnChangeEvent
import math
import time
import os, sys
import socket
import json
import logging
import os
#
logging.basicConfig(
    level=logging.INFO,  
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",  
    filename="game.log",  
)
# Константы

print(
    f"Разрешение экрана: {arcade.get_display_size()[0]}x{arcade.get_display_size()[1]}, происходит адаптация..."
)
SCREEN_WIDTH = arcade.get_display_size()[0]
SCREEN_HEIGHT = arcade.get_display_size()[1]


def import_variables(filename):
    variables = {}
    if filename in os.listdir("."):
        with open(filename, "r", encoding="utf-8") as file:
            for line in file:
                key, value = line.strip().split(":")
                variables[key] = value

    return variables


MULTIPLAYER_CONFIG_NAME = "multiplayer.json"

if MULTIPLAYER_CONFIG_NAME in os.listdir("."):
    with open(MULTIPLAYER_CONFIG_NAME, "r") as file:
        settings = json.loads(file.read())
else:
    settings = {"host":"localhost", "port":8080}

variables = import_variables("variables.dat")
drift_factor = float(variables["DRIFT_FACTOR"])
SCREEN_TITLE = "Race Game"
MAX_SPEED = int(variables["MAX_SPEED"])
AX = float(variables["AX"])
FRICTION = int(variables["FRICTION"])
g = float(variables["g"])
mu = float(variables["mu"])
fps = int(variables["fps"])
mod_folder = "mods"


click_coordinates = []
for var in variables:
    logging.debug(f"{var}: {variables[var]}")


# функции
def send_request(request_data: dict, host="127.0.0.1", port=8080):
    """
    Отправляет JSON-запрос на сервер и возвращает ответ в виде словаря.
    """
    # В этой функции используется стандартный модуль socket, он уже импортирован
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((host, port))
            # Кодируем словарь в JSON-строку, затем в байты
            s.sendall(json.dumps(request_data).encode("utf-8"))
            
            # Получаем ответ, декодируем байты в строку, затем парсим JSON
            response_bytes = s.recv(4096)
            if not response_bytes:
                logging.warning("Получен пустой ответ от сервера.")
                return {"error": "Empty response from server"}
            
            return json.loads(response_bytes.decode("utf-8"))
            
        except ConnectionRefusedError:
            logging.error(f"Не удалось подключиться к серверу {host}:{port}. В подключении отказано.")
            return {"error": "Connection refused"}
        except Exception as e:
            logging.error(f"Произошла ошибка при отправке запроса: {e}")
            return {"error": str(e)}


logging.debug("функции")


class ModManager:
    def __init__(self, klass, mod_folder="mods"):
        self.mod_folder = mod_folder
        self.mods = []
        self.klass = klass

    def call_func(self, obj, func_name, *args, **kwargs):
        if func_name in dir(obj):
            func = getattr(obj, func_name)
        else:
            return
        if callable(func):
            return func(*args, **kwargs)
        else:
            raise AttributeError(
                f"'{type(obj).__name__}' object has no callable attribute '{func_name}'"
            )

    def load_mod(self, name: str):
        if name.endswith(".py"):
            name = name[:-3]
        mod = __import__(f"{mod_folder}.{name}")
        return getattr(mod, name)

    def load(self):
        modlist = os.listdir(self.mod_folder)
        try:
            modlist.remove("__pycache__")
        except:
            pass

        for i in modlist:
            if i.endswith(".py"):
                i = i[:-3]
            mod = self.load_mod(i)
            name = i
            status = True
            if "name" in dir(mod):
                name = mod.name
            self.mods.append(
                {
                    "name": name,
                    "mod": mod,
                    "active": status,
                }
            )

    def call(self, func_name, *args, **kargs):
        returned = []
        for i in self.mods:
            if i["active"]:
                returned.append(
                    self.call_func(i["mod"], func_name, self.klass, *args, **kargs)
                )
        return returned

    def deactivate(self): ...
class RaceGame(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(
            width, height, title, fullscreen=False, resizable=True, vsync=True
        )
        self.set_update_rate(1 / fps)
        self.ai_list = None
        self.player_list = arcade.SpriteList()
        self.player_list.spatial_hash = True
        self.colors = ["orange", "red", "blue", "green"]
        self.players = []
        points_tr1 = [
            (-101, -249),
            (80, -263),
            (102, -103),
            (102, 79),
            (43, 211),
            (-26, 262),
            (-102, 287),
            (-99, 101),
            (-81, 88),
            (-80, -66),
            (-103, -188),
            (-101, -250),
        ]
        points_tr2 = [
            (239, 19),
            (239, 207),
            (2, 217),
            (-142, 189),
            (-439, -57),
            (-443, -246),
            (-397, -240),
            (-64, 18),
            (38, 36),
            (236, 18),
        ]
        points_tr3 = [
            (-322, -242),
            (-317, 148),
            (-383, 227),
            (-500, 250),
            (-500, 70),
            (-498, -96),
            (-455, -210),
            (-350, -250),
            (-321, -243),
        ]
        points_tr4 = [
            (-408, 117),
            (-409, 298),
            (-538, 280),
            (-602, 223),
            (-633, 120),
            (-652, -215),
            (-640, -288),
            (-453, -268),
            (-475, -175),
            (-449, 1),
            (-451, 112),
            (-407, 116),
        ]
        points_tr5 = [
            (-456, 4),
            (-637, -13),
            (-627, -85),
            (-516, -169),
            (-384, -188),
            (-194, -175),
            (363, -188),
            (549, -171),
            (619, -107),
            (634, -15),
            (266, -2),
            (-27, 13),
            (-456, 6),
        ]
        self.tr1 = arcade.Sprite("sprites/tr1.png")
        self.tr1.set_hit_box(points_tr1)
        self.tr1.center_x = SCREEN_WIDTH / 2 + 522  # стандартно SCREEN_WIDTH/2+522
        self.tr1.center_y = SCREEN_HEIGHT / 2 + 52  # стандартно SCREEN_HEIGHT/2+52
        self.tr2 = arcade.Sprite("sprites/tr2.png")
        self.tr2.set_hit_box(points_tr2)
        self.tr2.center_x = SCREEN_WIDTH / 2 + 184  # стандартно SCREEN_WIDTH/2+184
        self.tr2.center_y = SCREEN_HEIGHT / 2 + 134  # стандартно SCREEN_HEIGHT/2+134
        self.tr3 = arcade.Sprite("sprites/tr3.png")
        self.tr3.set_hit_box(points_tr3)
        self.tr3.center_x = SCREEN_WIDTH / 2 + 61  # стандартно SCREEN_WIDTH/2+61
        self.tr3.center_y = SCREEN_HEIGHT / 2 + 127  # стандартно SCREEN_HEIGHT/2+127
        self.tr4 = arcade.Sprite("sprites/tr4.png")
        self.tr4.set_hit_box(points_tr4)
        self.tr4.center_x = SCREEN_WIDTH / 2 - 31  # стандартно SCREEN_WIDTH/2-31
        self.tr4.center_y = SCREEN_HEIGHT / 2 + 78  # стандартно SCREEN_HEIGHT/2+78
        self.tr5 = arcade.Sprite("sprites/tr5.png")
        self.tr5.set_hit_box(points_tr5)
        self.tr5.center_x = SCREEN_WIDTH / 2 - 30  # стандартно SCREEN_WIDTH/2-30
        self.tr5.center_y = SCREEN_HEIGHT / 2 - 195  # стандартно SCREEN_HEIGHT/2-195
        self.track = arcade.SpriteList()
        self.track.append(self.tr1)
        self.track.append(self.tr2)
        self.track.append(self.tr3)
        self.track.append(self.tr4)
        self.track.append(self.tr5)
        logging.debug("инициализаия трека")
        # меню
        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        arcade.set_background_color((0, 70, 0))
        self.game_settings = False
        self.game = False
        self.menu = True
        self.settings = False
        self.v_box = arcade.gui.UIBoxLayout()
        start_button = arcade.gui.UITextureButton(
            texture=arcade.load_texture(
                ":resources:onscreen_controls/flat_dark/play.png"
            )
        )
        self.v_box.add(start_button.with_space_around(bottom=20))

        settings_button = arcade.gui.UITextureButton(
            texture=arcade.load_texture(
                ":resources:onscreen_controls/flat_dark/gear.png"
            )
        )
        self.v_box.add(settings_button.with_space_around(bottom=20))

        quit_button = arcade.gui.UITextureButton(
            texture=arcade.load_texture(
                ":resources:onscreen_controls/flat_dark/close.png"
            )
        )
        self.v_box.add(quit_button.with_space_around(bottom=20))

        @start_button.event("on_click")
        def wrap(event):
            if self.menu:
                self.on_start(event)

        @quit_button.event("on_click")
        def wrap(event):
            if self.menu:
                print("выход")
                arcade.exit()

        @settings_button.event("on_click")
        def wrap(event):
            if self.menu:
                self.show_start_window(event)

        self.manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x", anchor_y="center_y", child=self.v_box
            )
        )
        self.time_race = 1
        logging.debug("инициализация меню")
        # физика
        self.player_list = None
        self.wall_list = None
        self.player_sprite = None
        self.physics_engine = None
        self.barrier_list = arcade.SpriteList()
        self.barrier_list.spatial_hash = True
        logging.debug("инициализация физики")
        # музыка и эффекты
        self.music = False
        self.start = arcade.load_sound("sounds/click.wav")
        self.explosion = arcade.load_sound("sounds/explosion.wav")
        self.music_in_menu = arcade.load_sound("sounds/menu_music.wav")
        logging.debug("инициализация музыки и эффектов")
        # остальное
        self.plspeed = [0]
        self.cur_player = 0
        self.debug = False
        self.start_time = time.time()
        # print(f"игрок {self.id}")
        self.multiplayer = True
        self.camera = arcade.Camera()
        # повтор
        self.replay_state = {
            "record": False,
            "play": False,
            "name": "test1.repl",
            "replay": [],
        }
        self.frame = 0
        # мультиплеер
        self.controls = [
            {
                arcade.key.W: "forward",
                arcade.key.S: "backward",
                arcade.key.A: "mleft",
                arcade.key.D: "mright",
            },
            {
                arcade.key.UP: "forward",
                arcade.key.DOWN: "backward",
                arcade.key.LEFT: "mleft",
                arcade.key.RIGHT: "mright",
            },
            {
                arcade.key.T: "forward",
                arcade.key.G: "backward",
                arcade.key.F: "mleft",
                arcade.key.H: "mright",
            },
            {
                arcade.key.I: "forward",
                arcade.key.K: "backward",
                arcade.key.J: "mleft",
                arcade.key.L: "mright",
            },
        ]
        self.players_count = 1
        self.id = 0  # int(sys.argv[1])#send_request(request="join")["length"]
        self.multiplayer_controls = [
            {"forward": False, "backward": False, "mleft": False, "mright": False},
            {"forward": False, "backward": False, "mleft": False, "mright": False},
            {"forward": False, "backward": False, "mleft": False, "mright": False},
            {"forward": False, "backward": False, "mleft": False, "mright": False},
        ]
        self.modManager = ModManager(self)
        self.modManager.load()
        self.modManager.call("__init__")
        logging.info(f"мультиплеер: {self.multiplayer}")
        logging.info("инициализация завершена")

    def switch_layout(self, layout):
        pass

    def menu_music(self):
        mus = arcade.play_sound(self.music_in_menu)
        if not self.music:
            arcade.stop_sound(mus)

    def show_start_window(self, event):
        logging.debug("меню настроек")
        arcade.play_sound(self.start)
        self.game_settings = True
        self.menu = False

        self.managers = UIManager()
        self.managers.enable()
        box = arcade.gui.UIBoxLayout()
        ui_slider = UISlider(
            value=self.players_count, width=300, height=50, max_value=4, min_value=1
        )
        label = UILabel(text=f"игроков:{ui_slider.value:1.0f}")

        @ui_slider.event()
        def on_change(event: UIOnChangeEvent):
            if self.game_settings:
                label.text = f"игроков:{ui_slider.value:1.0f}"
                label.fit_content()
                self.players_count = round(ui_slider.value)

        box.add(child=label.with_space_around(left=100, bottom=10))
        box.add(child=ui_slider.with_space_around(left=100, bottom=20))
        debug_mode = arcade.gui.UITextureButton(
            texture=arcade.load_texture(
                ":resources:onscreen_controls/flat_dark/unchecked.png"
            )
        )
        label_d = UILabel(text=f"режим отладки")
        back = arcade.gui.UITextureButton(
            texture=arcade.load_texture(
                ":resources:onscreen_controls/flat_dark/left.png"
            ),
            scale=0.5,
        )
        sound = arcade.gui.UITextureButton(
            texture=arcade.load_texture(
                ":resources:onscreen_controls/flat_dark/music_on.png"
            )
        )

        @sound.event("on_click")
        def on_change(event):
            if self.game_settings:
                self.music = not self.music
                if self.debug:
                    sound.texture = arcade.load_texture(
                        ":resources:onscreen_controls/flat_dark/music_on.png"
                    )
                else:
                    sound.texture = arcade.load_texture(
                        ":resources:onscreen_controls/flat_dark/music_off.png"
                    )

        @back.event("on_click")
        def back_f(event):
            if self.game_settings:
                self.set_menu()

        @debug_mode.event("on_click")
        def on_change(event):
            if self.game_settings:
                self.debug = not self.debug
                if self.debug:
                    debug_mode.texture = arcade.load_texture(
                        ":resources:onscreen_controls/flat_dark/checked.png"
                    )
                else:
                    debug_mode.texture = arcade.load_texture(
                        ":resources:onscreen_controls/flat_dark/unchecked.png"
                    )

        replay_cap = arcade.gui.UITextureButton(
            texture=arcade.load_texture(
                ":resources:onscreen_controls/flat_dark/unchecked.png"
            )
        )

        @replay_cap.event("on_click")
        def on_change(event):
            if self.game_settings:
                self.replay_state["record"] = not self.replay_state["record"]
                if self.replay_state["record"]:
                    replay_cap.texture = arcade.load_texture(
                        ":resources:onscreen_controls/flat_dark/checked.png"
                    )
                else:
                    replay_cap.texture = arcade.load_texture(
                        ":resources:onscreen_controls/flat_dark/unchecked.png"
                    )

        replay_play = arcade.gui.UITextureButton(
            texture=arcade.load_texture(
                ":resources:onscreen_controls/flat_dark/unchecked.png"
            )
        )

        @replay_play.event("on_click")
        def on_change(event):
            if self.game_settings:
                self.replay_state["play"] = not self.replay_state["play"]
                if self.replay_state["play"]:
                    replay_play.texture = arcade.load_texture(
                        ":resources:onscreen_controls/flat_dark/checked.png"
                    )
                else:
                    replay_play.texture = arcade.load_texture(
                        ":resources:onscreen_controls/flat_dark/unchecked.png"
                    )

        # self.managers.add(UIAnchorWidget(child=sound, align_y=90)) #TODO add sound controller
        box.add(child=label_d.with_space_around(left=100, bottom=20))
        box.add(child=debug_mode.with_space_around(left=100, bottom=20))
        box.add(
            child=UILabel(text="запись повтора").with_space_around(left=100, bottom=10)
        )
        box.add(child=replay_cap.with_space_around(left=100, bottom=20))
        box.add(
            child=UILabel(text="просмотр повтора").with_space_around(
                left=100, bottom=10
            )
        )
        box.add(child=replay_play.with_space_around(left=100, bottom=20))
        label_ai = UILabel(text="в этой версии нет ботов")
        box.add(child=label_ai.with_space_around(left=100, bottom=20))
        box.add(child=back.with_space_around(left=100, bottom=20))
        w, h = super().width, super().height
        self.managers.add(
            UIAnchorWidget(anchor_x="center_x", anchor_y="center_y", child=box)
        )
        logging.info("загрузка настроек завершена")

    def on_start(self, event):
        logging.debug("запуск игры")
        self.game_settings = False
        self.frame = 0
        if self.menu:
            self.cur_player = 0
            self.player_list = []
            self.players = []
            self.setup()
            arcade.play_sound(self.start)
            for player in range(len(self.players)):
                id = int(player)
                player = self.players[id]
                player["sprite"].center_x, player["sprite"].center_y = self.coordinates[
                    id
                ]
                player["speed"] = 0
                player["current_angle"] = 90
                logging.debug(f"игрок {id} инициализирован")
            self.game = True
            self.menu = False
            self.start_time = time.time()
        self.modManager.call("start")

    def exit(self, event):
        arcade.play_sound(self.start)
        logging.info("выход")
        if self.menu:
            arcade.close_window()

    def setup(self):
        self.coordinates = [
            (SCREEN_WIDTH / 2 + 517, SCREEN_HEIGHT / 2 - 336),
            (SCREEN_WIDTH / 2 + 547, SCREEN_HEIGHT / 2 - 276),
            (SCREEN_WIDTH / 2 + 517, SCREEN_HEIGHT / 2 - 216),
            (SCREEN_WIDTH / 2 + 547, SCREEN_HEIGHT / 2 - 156),
        ]
        self.coordinates.reverse()
        colors = [(255, 100, 100), (255, 0, 0), (0, 0, 255), (0, 255, 0)]
        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()

        if self.multiplayer:
            logging.info("Попытка подключения к многопользовательской игре...")
            join_response = send_request({"action": "join"}, host=settings.get('host', '127.0.0.1'), port=settings.get('port', 8080))
            
            if "error" in join_response:
                logging.error(f"Не удалось подключиться: {join_response['error']}. Переключение в одиночный режим.")
                self.multiplayer = False # Возвращаемся в одиночный режим
                self.id = 0
                self.players_count = 1
            else:
                self.id = join_response.get("id", 0)
                initial_state = join_response.get("state", [])
                self.players_count = len(initial_state)
                # Сохраняем начальное состояние для дальнейшего использования
                self.multiplayer_controls = initial_state
                logging.info(f"Успешное подключение! Мой ID: {self.id}. Всего игроков в state: {self.players_count}")
        else:
            self.id = 0

        for i in range(self.players_count):
            player_sprite = arcade.Sprite(
                f"sprites/{self.colors[i]}_car.png", scale=2 / 10
            )
            player_sprite.center_x, player_sprite.center_y = self.coordinates[i]
            player_sprite.color = colors[i]
            player_sprite.id = i
            self.player_list.append(player_sprite)
            self.players.append(
                {
                    "id": i,
                    "sprite": player_sprite,
                    "x": player_sprite.center_x,
                    "y": player_sprite.center_y,
                    "speed": 0,
                    "angle_speed": 0,
                    "current_angle": 90,
                    "forward": False,
                    "backward": False,
                    "mleft": False,
                    "mright": False,
                    "collisions_to_explosion": 10,
                    "explosion_time": 0.0,
                    "exploded": False,
                    "laps": 0,
                    "checkpoint": False,
                }
            )
            if i == self.id:
                self.send = {
                    "id": self.id,
                    "speed": 0,
                    "x": player_sprite.center_x,
                    "y": player_sprite.center_y,
                    "angle_speed": 0,
                    "current_angle": 90,
                    "forward": False,
                    "backward": False,
                    "mleft": False,
                    "mright": False,
                    "collisions_to_explosion": 10,
                    "explosion_time": 0.0,
                    "exploded": False,
                    "laps": 0,
                    "checkpoint": False,
                }
        out_points = [
            (1672, 552),
            (1534, 893),
            (1290, 939),
            (986, 938),
            (745, 930),
            (553, 943),
            (434, 943),
            (310, 897),
            (224, 716),
            (189, 373),
            (206, 218),
            (300, 120),
            (576, 89),
            (966, 69),
            (1388, 71),
            (1511, 91),
            (1619, 171),
            (1617, 271),
            (1610, 319),
            (1561, 326),
            (1547, 240),
            (1479, 173),
            (1298, 156),
            (738, 169),
            (551, 154),
            (414, 174),
            (304, 255),
            (276, 388),
            (296, 733),
            (327, 835),
            (392, 897),
            (523, 909),
            (641, 892),
            (703, 817),
            (704, 619),
            (997, 855),
            (1138, 889),
            (1375, 880),
            (1453, 857),
            (1526, 800),
            (1582, 676),
            (1564, 329),
            (1636, 321),
            (1672, 552),
        ]
        in_points = [
            (1383, 343),
            (1378, 407),
            (1404, 522),
            (1400, 685),
            (1190, 708),
            (1080, 692),
            (749, 433),
            (671, 414),
            (559, 455),
            (522, 571),
            (520, 735),
            (478, 726),
            (481, 614),
            (458, 440),
            (476, 351),
            (894, 361),
            (1383, 343),
        ]

        out_wall_sprite = arcade.Sprite()
        out_wall_sprite._points = out_points
        self.wall_list.append(out_wall_sprite)
        in_wall_sprite = arcade.Sprite()
        in_wall_sprite._points = in_points
        self.wall_list.append(in_wall_sprite)

    def set_menu(self):
        self.game = False
        self.menu = True
        self.managers.disable()
        self.manager.enable()
        self.game_settings = False

    def on_draw(self):
        global click_coordinates
        arcade.start_render()
        if self.game_settings:
            self.clear
            self.managers.draw()
            # self.manager.draw()
        elif self.game:
            self.clear
            if self.multiplayer:
                self.camera.use()
            # arcade.draw_line_strip(sprites, (0, 122, 255), 4)
            self.track.draw()
            self.player_list.draw()
            for player in self.players:
                arcade.draw_text(
                    f"игрок {player['sprite'].id + 1}",
                    player["sprite"].center_x,
                    player["sprite"].center_y + 20,
                    player["sprite"].color,
                )
                self.plspeed.append(round(player["speed"]))
        elif self.menu:
            self.clear()
            self.manager.draw()
        if self.debug and self.game:
            if click_coordinates:
                arcade.draw_line_strip(click_coordinates, arcade.color.GREEN, 4)
            self.barrier_list.draw_hit_boxes((255, 0, 0), 3)
            self.track.draw_hit_boxes((255, 0, 0), 3)
            self.player_list.draw_hit_boxes((200, 200, 200), 3)
            # self.wall_list.draw_hit_boxes((200, 100, 200), 4)
            # self.ai_list.draw_hit_boxes((100, 200, 255),1)
            x = self.camera.position[0]
            y = self.camera.position[1]
            arcade.draw_text(
                f"FPS:{self.FPS}",
                start_x=10 + x,
                start_y=SCREEN_HEIGHT - 120 + y,
                color=(255, 255, 255),
                font_size=14,
            )
            arcade.draw_text(
                f"скорость игрока {self.cur_player + 1}:{self.players[self.cur_player]['speed']}",
                start_x=10 + x,
                start_y=SCREEN_HEIGHT - 140 + y,
                color=(255, 255, 255),
                font_size=14,
            )
            arcade.draw_text(
                f"круги игрока {self.cur_player + 1}:{self.players[self.cur_player]['laps']}",
                start_x=10 + x,
                start_y=SCREEN_HEIGHT - 60 + y,
                color=(255, 255, 255),
                font_size=14,
            )
            arcade.draw_text(
                f"столкновейний осталось {self.players[self.cur_player]['collisions_to_explosion']}",
                start_x=10 + x,
                start_y=SCREEN_HEIGHT - 180 + y,
                color=(255, 255, 255),
                font_size=14,
            )
            arcade.draw_text(
                f"lim_k: {30 / self.FPS}",
                start_x=10 + x,
                start_y=SCREEN_HEIGHT - 200 + y,
            )
            arcade.draw_line_strip(
                [
                    (SCREEN_WIDTH / 2 + 436, SCREEN_HEIGHT / 2 + 17 - 100),
                    (SCREEN_WIDTH / 2 + 617, SCREEN_HEIGHT / 2 + 17 + MAX_SPEED - 100),
                ],
                color=(0, 0, 255),
            )
            arcade.draw_line_strip(
                [
                    (SCREEN_WIDTH / 2 - 436, SCREEN_HEIGHT / 2 - 78 + 200),
                    (SCREEN_WIDTH / 2 - 257, SCREEN_HEIGHT / 2 - 78 + MAX_SPEED + 280),
                ],
                color=(0, 0, 255),
            )
        self.modManager.call("draw")
        arcade.finish_render()

    def explode(self, player):
        arcade.play_sound(self.explosion)
        player["explosion_time"] = 0.0

    def calculate_approach_speed(self, v_a, alpha, v_b, beta, c_a: list, c_b: list):
        """
        Рассчитывает скорость сближения двух объектов.

        :param v_a: Скорость объекта A
        :param alpha: Угол движения объекта A в градусах
        :param v_b: Скорость объекта B
        :param beta: Угол движения объекта B в градусах
        :param c_a: координаты объекта A
        :param c_b: координаты объекта B
        :return: Скорость сближения двух объектов
        """
        alpha_rad = math.radians(alpha)
        beta_rad = math.radians(beta)
        #
        r = [c_a[0] - c_b[0], c_a[1] - c_b[1]]
        v_a_vector = (v_a * math.cos(alpha_rad), v_a * math.sin(alpha_rad))
        v_b_vector = (v_b * math.cos(beta_rad), v_b * math.sin(beta_rad))

        v_ab_vector = (v_a_vector[0] - v_b_vector[0], v_a_vector[1] - v_b_vector[1])

        if math.sqrt(r[0] ** 2 + r[1] ** 2) != 0:
            approach_speed = (
                v_ab_vector[0] * r[0] + v_ab_vector[1] * r[1]
            ) / math.sqrt(r[0] ** 2 + r[1] ** 2)
        else:
            return 0
        return approach_speed

    def update_send(self):
        player = self.players[self.id]
        self.send = multiplayer.bytelib.to_bytes(
            self.id,
            player["forward"],
            player["backward"],
            player["mleft"],
            player["mright"],
        )

    def check_for_collision(self):
        for i, player in enumerate(self.players):
            current_sprite = player["sprite"]
            for j, other_player in enumerate(self.players):
                if i == j:
                    continue
                other_sprite = other_player  # ['sprite']
                if arcade.check_for_collision(current_sprite, other_sprite["sprite"]):
                    approach_speed = self.calculate_approach_speed(
                        player["speed"],
                        player["current_angle"],
                        other_sprite["speed"],
                        other_sprite["current_angle"],
                        (current_sprite.center_x, current_sprite.center_y),
                        (
                            other_sprite["sprite"].center_x,
                            other_sprite["sprite"].center_y,
                        ),
                    )

                    player["speed"] = -player["speed"] * 0.5
                    other_player["speed"] = -other_player["speed"] * 0.5

                    if approach_speed <= 0:
                        player["collisions_to_explosion"] += approach_speed
                        other_player["collisions_to_explosion"] += approach_speed
                    else:
                        player["collisions_to_explosion"] -= approach_speed
                        other_player["collisions_to_explosion"] -= approach_speed

    def end_game(self):
        if self.replay_state["record"]:
            with open(self.replay_state["name"], "w") as f:
                json.dump(self.replay_state["replay"], f)
        best_player = max(self.players, key=lambda player: player["laps"])
        message = f"Игрок с наилучшим результатом: {best_player['sprite'].id + 1}, его результат - {best_player['laps']}"
        messagebox = arcade.gui.UIMessageBox(
            width=300,
            height=200,
            message_text=(message),  #
            buttons=["Ok"],
        )
        self.manager.add(messagebox)
        self.set_menu()

    def update_pos(self):
        for player in self.players:
            ID = player["sprite"].id
            # if ID == self.id:
            #   continue
            for control_key, control_value in self.multiplayer_controls[ID].items():
                player[control_key] = self.multiplayer_controls[ID][control_key]

    def get_state(self):
        pass

    def load_replay(self, name):
        with open(name, "r") as f:
            self.replay_state["replay"] = json.load(f)

    def drift_angle(self, angle, speed, dir, angle_speed):
        da = angle_speed * dir
        if da > 180:
            da -= 360
        elif da < -180:
            da += 360
        manuverability = max(0.4, 0.2 + 0.9 - abs(speed) / 1.5)
        max_turn = 5 * (1 - manuverability) * 10  # Максимальный поворот в градусах
        turn_amount = max(-max_turn, min(max_turn, da * (1 - manuverability)))
        angle += turn_amount
        return angle % 360

    def update(self, delta_time, ang_sp=4):
        global AX
        self.menu_music()
        self.FPS = 1 / delta_time
        if self.game:
            spl = self.players[self.id]["sprite"]
            self.camera.move_to(
                (spl.center_x - self.width / 2, spl.center_y - self.height / 2)
            )

            if self.multiplayer:
                my_controls = self.multiplayer_controls[self.id]
                input_data = {
                    "action": "input",
                    "id": self.id,
                    "keys": {
                        "forward": my_controls["forward"],
                        "backward": my_controls["backward"],
                        "mleft": my_controls["mleft"],
                        "mright": my_controls["mright"]
                    }
                }
                
                response = send_request(input_data, host=settings.get('host', '127.0.0.1'), port=settings.get('port', 8080))
                
                if response and response.get("status") == "update":
                    server_state = response.get("state", [])
                    if len(server_state) == len(self.multiplayer_controls):
                        self.multiplayer_controls = server_state
                    self.update_pos()
                elif response and "error" in response:
                    logging.warning(f"Ошибка от сервера: {response['error']}")
            
            if self.replay_state["record"]:
                state = {}
            for i in range(len(self.players)):
                player = self.players[i]
                if self.replay_state["record"]:
                    state[i] = (
                        player["forward"],
                        player["backward"],
                        player["mleft"],
                        player["mright"],
                    )
                if self.replay_state["play"]:
                    if not self.replay_state["replay"]:
                        self.load_replay(self.replay_state["name"])
                    (
                        player["forward"],
                        player["backward"],
                        player["mleft"],
                        player["mright"],
                    ) = self.replay_state["replay"][self.frame][str(i)]
                    self.frame += 1
                self.physics_engine = arcade.PhysicsEngineSimple(
                    player["sprite"], self.player_sprite
                )
                ang_sp = 4
                if player["speed"] != 0:
                    radius = abs(player["speed"]) / ang_sp
                    optimal_speed = math.sqrt(radius * g * mu)
                    if abs(player["speed"]) <= optimal_speed:
                        p = optimal_speed / abs(player["speed"])
                        ang_sp = player["speed"] * p
                    elif optimal_speed != 0:
                        p = abs(player["speed"]) / optimal_speed
                        ang_sp = player["speed"] / p
                else:
                    ang_sp = 0
                self.player = []
                self.player.append(player["sprite"])
                AX = 0.005 * player["speed"] ** 2 + 0.3
                if arcade.check_for_collision_with_list(player["sprite"], self.track):
                    FRICTION = 0.05
                else:
                    FRICTION = 0.8
                if player["mleft"]:
                    player["current_angle"] += self.drift_angle(
                        angle_speed=ang_sp,
                        speed=player["speed"],
                        angle=player["current_angle"],
                        dir=1,
                    )
                elif player["mright"]:
                    player["current_angle"] -= self.drift_angle(
                        angle_speed=ang_sp,
                        speed=player["speed"],
                        angle=player["current_angle"],
                        dir=1,
                    )
                if player["forward"]:
                    if player["speed"] <= MAX_SPEED:
                        player["speed"] += AX
                elif player["backward"]:
                    if player["speed"] > 0:
                        player["speed"] -= AX / 3
                    elif -1 <= player["speed"] < 0:
                        player["speed"] -= AX / 3
                    else:
                        player["speed"] += -1 - player["speed"]
                player["speed"] -= player["speed"] * (FRICTION)
                if player["collisions_to_explosion"] <= 0:
                    player["speed"] = 0
                    if not player["exploded"]:
                        self.explode(player)
                        player["exploded"] = True
                self.check_for_collision()
                player["sprite"].angle = player["current_angle"]
                player["sprite"].change_x = player["speed"] * math.cos(
                    math.radians(player["current_angle"])
                )
                player["sprite"].change_y = player["speed"] * math.sin(
                    math.radians(player["current_angle"])
                )
                player["sprite"].center_x += player["sprite"].change_x
                player["sprite"].center_y += player["sprite"].change_y
                if player["sprite"].left < 0:
                    player["sprite"].left = 0
                elif player["sprite"].right > SCREEN_WIDTH:
                    player["sprite"].right = SCREEN_WIDTH
                if player["sprite"].bottom < 0:
                    player["sprite"].bottom = 0
                elif player["sprite"].top > SCREEN_HEIGHT:
                    player["sprite"].top = SCREEN_HEIGHT
                self.physics_engine.update()
                if (
                    SCREEN_WIDTH / 2 - 436
                    <= player["sprite"].center_x
                    <= SCREEN_WIDTH / 2 - 257
                    and SCREEN_HEIGHT / 2 - 78 + 200
                    <= player["sprite"].center_y
                    <= SCREEN_HEIGHT / 2 - 78 + 280 + MAX_SPEED
                ):
                    player["checkpoint"] = True
                if (
                    SCREEN_WIDTH / 2 + 447
                    <= player["sprite"].center_x
                    <= SCREEN_WIDTH / 2 + 617
                    and SCREEN_HEIGHT / 2 + 17 - 100
                    <= player["sprite"].center_y
                    <= SCREEN_HEIGHT / 2 + 17 + MAX_SPEED - 100
                ) and player["checkpoint"]:
                    player["laps"] += 1
                    player["checkpoint"] = False
                if player["exploded"]:
                    player["explosion_time"] += delta_time
                if player["explosion_time"] >= 10 and player["exploded"]:
                    player["exploded"] = False
                    player["collisions_to_explosion"] = 10
                    player["sprite"].center_x, player["sprite"].center_y = (
                        self.coordinates[player["sprite"].id]
                    )
                    player["current_angle"] = 90
                    player["speed"] = 0
                if self.replay_state["record"]:
                    self.replay_state["replay"].append(state)
            if self.multiplayer:
                self.cor()
        elif self.menu:
            self.camera.move((0, 0))
        if (
            time.time() - self.start_time > self.time_race * 60 and self.game
        ):  # and False:  # TODO добавить ограничение времени
            self.end_game()
        self.modManager.call("update", delta_time)

    def cor(self):
        self.update_send()
        # send_request(host=settings['host'], port=settings["port"],request=self.send)#TODO fix server

    def on_mouse_press(self, x, y, button, modifiers):
        global click_coordinates
        if self.debug:
            if button == arcade.MOUSE_BUTTON_LEFT:
                # Добавление координат левого клика в список
                click_coordinates.append((x, y))
            elif button == arcade.MOUSE_BUTTON_MIDDLE:
                click_coordinates = click_coordinates[:-1]
            elif button == arcade.MOUSE_BUTTON_RIGHT:
                # Вывод списка координат в файл, разделяя точками, и переход на новую строку
                with open("click_coordinates.txt", "a") as file:
                    file.write(
                        "; ".join(
                            f"{coord[0]} {coord[1]}" for coord in click_coordinates
                        )
                        + "\n"
                    )
                click_coordinates = []  # Очистка списка после записи

    def set_menu(self):
        self.game_settings = False
        self.game = False
        self.menu = True

    def on_key_press(self, key, modifiers):
        if key == arcade.key.Q:
            self.exit(None)
        if key == arcade.key.TAB and self.game:
            self.cur_player += 1
            self.cur_player %= len(self.players)
        if key == arcade.key.ESCAPE:
            self.set_menu()
        for player in self.players:
            if player["sprite"].id == self.id and self.multiplayer:
                for control_key, control_value in self.controls[
                    player["sprite"].id
                ].items():
                    if key == control_key:
                        self.multiplayer_controls[player["sprite"].id][
                            control_value
                        ] = True
                        # player[control_value] = True
        self.modManager.call("on_key_press", key, modifiers)

    def on_key_release(self, key, modifiers):
        for player in self.players:
            for control_key, control_value in self.controls[
                player["sprite"].id
            ].items():
                if key == control_key:
                    self.multiplayer_controls[player["sprite"].id][
                        control_value
                    ] = False
                    # player[control_value] = False
        self.modManager.call("on_key_release", key, modifiers)


# Основная функция
def main():
    game = RaceGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nвыполнение завершено пользователем")
    # except Exception as ex:
    #     print(f"произошла ошибка {ex}")
