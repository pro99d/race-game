# Modding API для Race Game

## Введение

Race Game поддерживает систему модов, которая позволяет расширять функциональность игры без изменения основного кода. Моды могут добавлять новые возможности, изменять физику, добавлять графические эффекты и многое другое.

## Структура мода

Каждый мод должен быть размещен в отдельном Python-файле в директории `mods/`. Файл мода должен содержать определенные функции, которые будут вызываться игровым движком в соответствующие моменты.

### Основные функции

```python
def __init__(self, *argvs, **kwargs):
    """
    Инициализация мода. Вызывается при загрузке.
    
    Параметры:
    - self: экземпляр основного класса игры (RaceGame)
    - argvs, kwargs: дополнительные параметры
    """
    pass

def update(self, dt):
    """
    Обновление состояния мода.
    
    Параметры:
    - self: экземпляр основного класса игры
    - dt: время, прошедшее с последнего обновления (в секундах)
    """
    pass

def draw(self):
    """
    Отрисовка дополнительных элементов.
    
    Параметры:
    - self: экземпляр основного класса игры
    """
    pass

def handle_event(self, event_type, *argvs, **kwargs):
    """
    Обработка событий (нажатия клавиш, движения мыши и т.д.)
    
    Параметры:
    - self: экземпляр основного класса игры
    - event_type: тип события
    - argvs, kwargs: дополнительные параметры события
    """
    pass
```

## Доступные события

События, которые может обрабатывать мод через функцию `handle_event`:

- `key_press`: нажатие клавиши
- `key_release`: отпускание клавиши
- `mouse_press`: нажатие кнопки мыши
- `mouse_release`: отпускание кнопки мыши
- `mouse_motion`: движение мыши
- `setup`: инициализация игры
- `collision`: столкновение автомобилей
- `lap_complete`: завершение круга
- `game_over`: окончание игры

## Доступ к игровым объектам

Через параметр `self` в функциях мода доступны следующие объекты и свойства:

```python
# Списки спрайтов
self.player_list      # список всех игроков
self.track           # список элементов трассы
self.barrier_list    # список барьеров

# Информация об игроках
self.players         # список словарей с данными игроков
# Пример данных игрока:
{
    'sprite': player_sprite,      # спрайт игрока
    'speed': 0,                   # текущая скорость
    'angle_speed': 0,             # скорость поворота
    'current_angle': 90,          # текущий угол
    'forward': False,             # движение вперед
    'backward': False,            # движение назад
    'mleft': False,               # поворот влево
    'mright': False,              # поворот вправо
    'collisions_to_explosion': 10, # количество столкновений до взрыва
    'explosion_time': 0.0,        # время взрыва
    'exploded': False,            # состояние взрыва
    'laps': 0,                    # количество кругов
    'checkpoint': False           # прохождение чекпоинта
}

# Настройки физики (из variables.dat)
MAX_SPEED            # максимальная скорость
AX                   # ускорение
FRICTION             # трение
g                    # гравитация
mu                   # коэффициент сцепления
fps                  # кадров в секунду
DRIFT_FACTOR         # коэффициент дрифта

# Состояние игры
self.game            # игра активна
self.menu           # меню активно
self.settings       # настройки активны
self.debug          # режим отладки
```

## Пример мода

Вот пример простого мода, который добавляет отображение скорости для каждого игрока:

```python
import arcade

def __init__(self, *argvs, **kwargs):
    print('Speed Display Mod loaded')

def draw(self):
    if not self.game:
        return
        
    for player in self.players:
        # Отображаем скорость над автомобилем
        speed_text = f"Speed: {abs(player['speed']):.1f}"
        arcade.draw_text(
            speed_text,
            player['sprite'].center_x,
            player['sprite'].center_y + 40,
            player['sprite'].color,
            12,
            anchor_x="center"
        )

def update(self, dt):
    pass

def handle_event(self, event_type, *argvs, **kwargs):
    pass
```

## Советы по разработке модов

1. **Производительность**:
   - Старайтесь минимизировать вычисления в функции `update`
   - Используйте `arcade.SpriteList` для групп спрайтов
   - Кэшируйте значения, которые используются часто

2. **Совместимость**:
   - Проверяйте наличие необходимых атрибутов перед их использованием
   - Не изменяйте критические параметры игры напрямую
   - Используйте `try-except` для обработки потенциальных ошибок

3. **Отладка**:
   - Используйте `self.debug` для отображения отладочной информации
   - Добавляйте логирование важных событий
   - Тестируйте мод в разных игровых ситуациях

## Тестирование модов

Для тестирования мода используйте скрипт `test.py`:

```bash
python test.py
```

Это позволит проверить загрузку мода и базовую функциональность.

## Ограничения

1. Моды не могут:
   - Изменять системные файлы
   - Напрямую взаимодействовать с сетевым кодом
   - Модифицировать другие моды

2. Рекомендации по безопасности:
   - Не выполняйте непроверенный код
   - Ограничивайте доступ к файловой системе
   - Проверяйте входные данные

## Отладка и решение проблем

1. **Логирование**:
   ```python
   import logging
   
   def __init__(self, *argvs, **kwargs):
       logging.info('Mod initialized')
       logging.debug('Debug information')
   ```

2. **Проверка ошибок**:
   ```python
   def update(self, dt):
       try:
           # ваш код
           pass
       except Exception as e:
           logging.error(f'Error in mod update: {e}')
   ```

3. **Отладочный режим**:
   ```python
   def draw(self):
       if self.debug:
           # отображение отладочной информации
           pass
   ```

## Функция info

Каждый мод может (и рекомендуется) реализовать функцию `info`, возвращающую информацию о моде в формате JSON:

```python
def info():
    return {
        "name": "Название мода",
        "author": "Автор",
        "desc": "Описание мода",
        "version": "1.0"
    }
```

Эта информация может использоваться лаунчером или самой игрой для отображения сведений о модах.

## Пример многофайлового мода

Рассмотрим пример мода, который отображает различные параметры (скорость, угол, номер круга) над каждым игроком. Мод состоит из нескольких файлов:

```
mods/
  player_info_mod/
    __init__.py
    draw_info.py
    utils.py
```

### `mods/player_info_mod/__init__.py`

```python
from .draw_info import draw_player_info
from .utils import get_player_params

def info():
    return {
        "name": "Player Info Mod",
        "author": "Your Name",
        "desc": "Показывает скорость, угол и круг над каждым игроком.",
        "version": "1.0"
    }

def __init__(self, *argvs, **kwargs):
    print("Player Info Mod loaded")

def draw(self):
    for player in self.players:
        params = get_player_params(player)
        draw_player_info(player, params)

def update(self, dt):
    pass

def handle_event(self, event_type, *argvs, **kwargs):
    pass
```

### `mods/player_info_mod/draw_info.py`

```python
import arcade

def draw_player_info(player, params):
    x = player['sprite'].center_x
    y = player['sprite'].center_y + 40
    color = player['sprite'].color
    text = f"Скорость: {params['speed']:.1f}\nУгол: {params['angle']:.1f}\nКруг: {params['lap']}"
    arcade.draw_text(text, x, y, color, 12, anchor_x="center")
```

### `mods/player_info_mod/utils.py`

```python
def get_player_params(player):
    return {
        'speed': abs(player['speed']),
        'angle': player['current_angle'],
        'lap': player.get('laps', 0)
    }
```

---
