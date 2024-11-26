import arcade
import arcade.gui
from arcade.experimental.uislider import UISlider
from arcade.gui import UIManager, UIAnchorWidget, UILabel
from arcade.gui.events import UIOnChangeEvent
import math
import time
import os, sys


# Константы

print(f"Разрешение экрана: {arcade.get_display_size()[0]}x{arcade.get_display_size()[1]}, происходит адаптация...")
SCREEN_WIDTH = arcade.get_display_size()[0]
SCREEN_HEIGHT = arcade.get_display_size()[1]


def import_variables(filename):
    variables = {}
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            key, value = line.strip().split(':')
            variables[key] = value

    return variables

variables = import_variables('variables.txt')
DRIFT_FACTOR = float(variables["DRIFT_FACTOR"])
SCREEN_TITLE = "Race Game"
MAX_SPEED = int(variables['MAX_SPEED'])
AX = float(variables['AX'])
FRICTION = int(variables['FRICTION'])
g = float(variables['g'])
mu = float(variables['mu'])
fps = int(variables['fps'])


click_coordinates = []
# функции





class RaceGame(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title, fullscreen=False)
        self.set_update_rate(1 / fps)
        self.ai_list = None
        self.player_list = arcade.SpriteList()
        self.colors = ["orange", "red", "blue", "green"]
        self.players = []
        points_tr1 = [(-101, -249), (80, -263), (102, -103), (102, 79), (43, 211), (-26, 262), (-102, 287), (-99, 101),
                      (-81, 88), (-80, -66), (-103, -188), (-101, -250)]
        points_tr2 = [(239, 19), (239, 207), (2, 217), (-142, 189), (-439, -57), (-443, -246), (-397, -240), (-64, 18),
                      (38, 36), (236, 18)]
        points_tr3 = [(-322, -242), (-317, 148), (-383, 227), (-500, 250), (-500, 70), (-498, -96), (-455, -210),
                      (-350, -250), (-321, -243)]
        points_tr4 = [(-408, 117), (-409, 298), (-538, 280), (-602, 223), (-633, 120), (-652, -215), (-640, -288),
                      (-453, -268), (-475, -175), (-449, 1), (-451, 112), (-407, 116)]
        points_tr5 = [(-456, 4), (-637, -13), (-627, -85), (-516, -169), (-384, -188), (-194, -175), (363, -188),
                      (549, -171), (619, -107), (634, -15), (266, -2), (-27, 13), (-456, 6)]
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
        # меню
        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        arcade.set_background_color((0, 70, 0))
        self.game_settings = False
        self.game = False
        self.menu = True
        self.settings = False
        self.v_box = arcade.gui.UIBoxLayout()
        start_button = arcade.gui.UIFlatButton(text="Играть", width=200)
        self.v_box.add(start_button.with_space_around(bottom=20))

        settings_button = arcade.gui.UIFlatButton(text="Настройки", width=200)
        self.v_box.add(settings_button.with_space_around(bottom=20))

        quit_button = arcade.gui.UIFlatButton(text="выход", width=200)
        self.v_box.add(quit_button.with_space_around(bottom=20))

        start_button.on_click = self.on_start
        quit_button.on_click = self.exit
        settings_button.on_click = self.show_start_window
        self.manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x",
                anchor_y="center_y",
                child=self.v_box)
        )
        self.time_race = 1
        # физика
        self.player_list = None
        self.wall_list = None
        self.player_sprite = None
        self.physics_engine = None
        self.barrier_list = arcade.SpriteList()

        # музыка и эффекты
        self.music = True
        self.start = arcade.load_sound("sounds/click.wav")
        self.explosion = arcade.load_sound("sounds/explosion.wav")
        self.music_in_menu = arcade.load_sound("sounds/menu_music.wav")
        # остальное
        self.plspeed = [0]
        self.cur_player = 0
        self.debug = False
        self.start_time = time.time()
        self.players_count = 1

    def menu_music(self):
        if self.menu:
            if self.music:
                arcade.schedule(arcade.play_sound(self.music_in_menu), self.music_in_menu.get_length())

    def show_start_window(self, event):
        arcade.play_sound(self.start)
        self.game_settings = True
        self.menu = False
        self.managers = UIManager()
        self.managers.enable()
        ui_slider = UISlider(value=self.players_count, width=300, height=50, max_value=4, min_value=1)
        label = UILabel(text=f"игроков:{ui_slider.value:1.0f}")

        @ui_slider.event()
        def on_change(event: UIOnChangeEvent):
            label.text = f"игроков:{ui_slider.value:1.0f}"
            label.fit_content()
            self.players_count = round(ui_slider.value)

        self.managers.add(UIAnchorWidget(child=ui_slider))
        self.managers.add(UIAnchorWidget(child=label, align_y=70))
        debug_mode = UISlider(value=0, width=75, height=50, max_value=1, min_value=0)
        label_d = UILabel(text=f"режим отлаки выключен")

        @debug_mode.event()
        def on_change(event: UIOnChangeEvent):
            if debug_mode.value:
                label_d.text = f'режим отладки включен'
                self.debug = True
            else:
                label_d.text = f"режим отладки выключен"
                self.debug = False

        self.managers.add(UIAnchorWidget(child=debug_mode, align_y=-100))
        self.managers.add(UIAnchorWidget(child=label_d, align_y=-30))
        label_ai = UILabel(text="данное устройство не поддерживает ботов")
        self.managers.add(UIAnchorWidget(child=label_ai, align_y=-130))

    def on_start(self, event):
        self.game_settings = False
        if self.menu:
            self.cur_player = 0
            self.player_list = []
            self.players = []
            self.setup()
            arcade.play_sound(self.start)
            for player in self.players:
                player['sprite'].center_x, player['sprite'].center_y = self.coordinates[player['sprite'].id]
                player['speed'] = 0
                player['current_angle'] = 90
            self.game = True
            self.menu = False
            self.start_time = time.time()

    def exit(self, event):
        arcade.play_sound(self.start)
        if self.menu:
            arcade.close_window()

    def setup(self, ):
        self.coordinates = [
            (SCREEN_WIDTH / 2 + 517, SCREEN_HEIGHT / 2 - 336),
            (SCREEN_WIDTH / 2 + 547, SCREEN_HEIGHT / 2 - 276),
            (SCREEN_WIDTH / 2 + 517, SCREEN_HEIGHT / 2 - 216),
            (SCREEN_WIDTH / 2 + 547, SCREEN_HEIGHT / 2 - 156)
        ]
        self.coordinates.reverse()
        colors = [(255, 100, 100), (255, 0, 0), (0, 0, 255), (0, 255, 0)]
        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()
        for i in range(self.players_count):
            player_sprite = arcade.Sprite(f"sprites/{self.colors[i]}_car.png", scale=2 / 10)
            player_sprite.center_x, player_sprite.center_y = self.coordinates[i]
            player_sprite.color = colors[i]
            player_sprite.id = i
            self.player_list.append(player_sprite)
            self.players.append({
                'sprite': player_sprite,
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
            })

    def set_menu(self):
        self.game = False
        self.menu = True

    def on_draw(self):
        arcade.start_render()
        if self.game_settings:
            self.clear
            self.managers.draw()
        elif self.game:
            self.clear
            #arcade.draw_line_strip(sprites, (0, 122, 255), 4)
            self.track.draw()
            self.player_list.draw()
            for player in self.players:
                arcade.draw_text(f"игрок {player['sprite'].id + 1}", player['sprite'].center_x,
                                 player['sprite'].center_y + 20, player['sprite'].color)
                self.plspeed.append(round(player['speed']))
        elif self.menu:
            self.clear()
            self.manager.draw()
        if self.debug and self.game:
            self.barrier_list.draw_hit_boxes((255, 0, 0), 3)
            self.track.draw_hit_boxes((255, 0, 0), 3)
            self.player_list.draw_hit_boxes((200, 200, 200), 3)
            # self.ai_list.draw_hit_boxes((100, 200, 255),1)
            arcade.draw_text(f'FPS:{self.FPS}', start_x=10, start_y=SCREEN_HEIGHT - 20, color=(255, 255, 255),
                             font_size=14)
            arcade.draw_text(f'скорость игрока {self.cur_player + 1}:{self.players[self.cur_player]["speed"]}',
                             start_x=10, start_y=SCREEN_HEIGHT - 40, color=(255, 255, 255), font_size=14)
            arcade.draw_text(f'круги игрока {self.cur_player + 1}:{self.players[self.cur_player]["laps"]}', start_x=10,
                             start_y=SCREEN_HEIGHT - 60, color=(255, 255, 255), font_size=14)
            arcade.draw_text(f'столкновейний осталось {self.players[self.cur_player]["collisions_to_explosion"]}',
                             start_x=10, start_y=SCREEN_HEIGHT - 80, color=(255, 255, 255), font_size=14)
            arcade.draw_line_strip([(SCREEN_WIDTH / 2 + 436, SCREEN_HEIGHT / 2 + 17 - 100),
                                    (SCREEN_WIDTH / 2 + 617, SCREEN_HEIGHT / 2 + 17 + MAX_SPEED - 100)],
                                   color=(0, 0, 255))
            arcade.draw_line_strip([(SCREEN_WIDTH / 2 - 436, SCREEN_HEIGHT / 2 - 78 + 200),
                                    (SCREEN_WIDTH / 2 - 257, SCREEN_HEIGHT / 2 - 78 + MAX_SPEED + 280)],
                                   color=(0, 0, 255))

    def explode(self, player):
        arcade.play_sound(self.explosion)
        player['explosion_time'] = 0.0

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
            approach_speed = (v_ab_vector[0] * r[0] + v_ab_vector[1] * r[1]) / math.sqrt(r[0] ** 2 + r[1] ** 2)
        else:
            return 0
        return approach_speed

    def check_for_collision(self):
        # Проверка столкновений между игроками
        for i, player in enumerate(self.players):
            current_sprite = player['sprite']
            for j, other_player in enumerate(self.players):
                if i == j:  # пропуск сравнения с самим собой
                    continue
                other_sprite = other_player#['sprite']
                if arcade.check_for_collision(current_sprite, other_sprite["sprite"]):
                    approach_speed = self.calculate_approach_speed(
                        player['speed'], player['current_angle'],
                        other_sprite['speed'], other_sprite['current_angle'],
                        (current_sprite.center_x, current_sprite.center_y),
                        (other_sprite["sprite"].center_x, other_sprite["sprite"].center_y)
                    )

                    player['speed'] = -player['speed'] * 0.5
                    other_player['speed'] = -other_player['speed'] * 0.5


                    if approach_speed <= 0:
                        player['collisions_to_explosion'] += approach_speed
                        other_player['collisions_to_explosion'] += approach_speed
                    else:
                        player['collisions_to_explosion'] -= approach_speed
                        other_player['collisions_to_explosion'] -= approach_speed

    def end_game(self):
        best_player = max(self.players, key=lambda player: player['laps'])
        message = f"Игрок с наилучшим результатом: {best_player['sprite'].id + 1}, его результат - {best_player['laps']}"
        messagebox = arcade.gui.UIMessageBox(
            width=300,
            height=200,
            message_text=(
                message
            ),
            buttons=["Ok"]
        )
        self.manager.add(messagebox)
        self.set_menu()

    def update(self, delta_time, ang_sp=4):
        global AX
        self.menu_music()
        self.FPS = 1 / delta_time
        if self.game:
            for player in self.players:
                self.physics_engine = arcade.PhysicsEngineSimple(player['sprite'], self.player_sprite)
                ang_sp = 4
                if player['speed'] != 0:
                    radius = abs(player['speed']) / ang_sp
                    optimal_speed = math.sqrt(radius * g * mu)
                    if abs(player['speed']) <= optimal_speed:
                        p = optimal_speed / abs(player['speed'])
                        ang_sp = player['speed'] * p
                    elif optimal_speed != 0:
                        p = abs(player['speed']) / optimal_speed
                        ang_sp = player['speed'] / p
                else:
                    ang_sp = 0
                self.player = []
                self.player.append(player['sprite'])
                if arcade.check_for_collision_with_list(player['sprite'], self.track):
                    FRICTION = 0.05
                else:
                    FRICTION = 0.8
                if player['mleft']:
                    player['current_angle'] += ang_sp
                elif player['mright']:
                    player['current_angle'] -= ang_sp
                if player['forward']:
                    if player['speed'] <= MAX_SPEED:
                        player['speed'] += AX
                elif player['backward']:
                    if player['speed'] > 0:
                        player['speed'] -= AX / 3
                    elif -1 <= player['speed'] < 0:
                        player['speed'] -= AX / 3
                    else:
                        player['speed'] += -1 - player['speed']
                if 3.7999 <= player['speed'] <= 7.59:
                    AX = 0.4
                elif 7.59 < player['speed'] < MAX_SPEED:
                    AX = 0.6
                player['speed'] -= player['speed'] * FRICTION
                if player['collisions_to_explosion'] <= 0:
                    player['speed'] = 0
                    if not player['exploded']:
                        self.explode(player)
                        player['exploded'] = True
                self.check_for_collision()
                player['sprite'].angle = player['current_angle']
                player['sprite'].change_x = player['speed'] * math.cos(math.radians(player['current_angle']))
                player['sprite'].change_y = player['speed'] * math.sin(math.radians(player['current_angle']))
                player['sprite'].center_x += player['sprite'].change_x
                player['sprite'].center_y += player['sprite'].change_y
                if player['sprite'].left < 0:
                    player['sprite'].left = 0
                elif player['sprite'].right > SCREEN_WIDTH:
                    player['sprite'].right = SCREEN_WIDTH
                if player['sprite'].bottom < 0:
                    player['sprite'].bottom = 0
                elif player['sprite'].top > SCREEN_HEIGHT:
                    player['sprite'].top = SCREEN_HEIGHT
                self.physics_engine.update()
                if (SCREEN_WIDTH / 2 - 436 <= player['sprite'].center_x <= SCREEN_WIDTH / 2 - 257 and
                        SCREEN_HEIGHT / 2 - 78 + 200 <= player[
                            'sprite'].center_y <= SCREEN_HEIGHT / 2 - 78 + 280 + MAX_SPEED):
                    player['checkpoint'] = True
                if (SCREEN_WIDTH / 2 + 447 <= player['sprite'].center_x <= SCREEN_WIDTH / 2 + 617 and
                    SCREEN_HEIGHT / 2 + 17 - 100 <= player[
                        'sprite'].center_y <= SCREEN_HEIGHT / 2 + 17 + MAX_SPEED - 100) and player['checkpoint']:
                    player['laps'] += 1
                    player['checkpoint'] = False
                if player['exploded']:
                    player['explosion_time'] += delta_time
                if player['explosion_time'] >= 10 and player['exploded']:
                    player['exploded'] = False
                    player['collisions_to_explosion'] = 10
                    player['sprite'].center_x, player['sprite'].center_y = self.coordinates[player['sprite'].id]
                    player['current_angle'] = 90
                    player['speed'] = 0
        if time.time() - self.start_time > self.time_race * 60 and self.game:
            self.end_game()

    def on_mouse_press(self, x, y, button, modifiers):
        global click_coordinates
        if self.debug:
            if button == arcade.MOUSE_BUTTON_LEFT:
                # Добавление координат левого клика в список
                click_coordinates.append((x, y))
            elif button == arcade.MOUSE_BUTTON_RIGHT:
                # Вывод списка координат в файл, разделяя точками, и переход на новую строку
                with open('click_coordinates.txt', 'a') as file:
                    file.write('; '.join(f"{coord[0]} {coord[1]}" for coord in click_coordinates) + "\n")
                click_coordinates = []  # Очистка списка после записи

    def set_menu(self):
        self.game_settings = False
        self.game = False
        self.menu = True

    def on_key_press(self, key, modifiers):
        controls = [
            {arcade.key.W: 'forward', arcade.key.S: 'backward', arcade.key.A: 'mleft', arcade.key.D: 'mright'},
            {arcade.key.UP: 'forward', arcade.key.DOWN: 'backward', arcade.key.LEFT: 'mleft',
             arcade.key.RIGHT: 'mright'},
            {arcade.key.T: 'forward', arcade.key.G: 'backward', arcade.key.F: 'mleft', arcade.key.H: 'mright'},
            {arcade.key.I: 'forward', arcade.key.K: 'backward', arcade.key.J: 'mleft', arcade.key.L: 'mright'}
        ]
        if key == arcade.key.Q:
            self.exit(None)
        if key == arcade.key.TAB and self.game:
            self.cur_player += 1
            self.cur_player %= len(self.players)
        if key == arcade.key.ESCAPE:
            self.set_menu()
        for player in self.players:
            for control_key, control_value in controls[player['sprite'].id].items():
                if key == control_key:
                    player[control_value] = True

    def on_key_release(self, key, modifiers):
        controls = [
            {arcade.key.W: 'forward', arcade.key.S: 'backward', arcade.key.A: 'mleft', arcade.key.D: 'mright'},
            {arcade.key.UP: 'forward', arcade.key.DOWN: 'backward', arcade.key.LEFT: 'mleft',
             arcade.key.RIGHT: 'mright'},
            {arcade.key.T: 'forward', arcade.key.G: 'backward', arcade.key.F: 'mleft', arcade.key.H: 'mright'},
            {arcade.key.I: 'forward', arcade.key.K: 'backward', arcade.key.J: 'mleft', arcade.key.L: 'mright'}
        ]
        for player in self.players:
            for control_key, control_value in controls[player['sprite'].id].items():
                if key == control_key:
                    player[control_value] = False


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
