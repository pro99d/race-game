from .draw_info import draw_player_info
from .utils import get_player_params

def info():
    """
    возвращает информацию о моде
    """
    return {
        "name": "Player Info Mod",
        "author": "Your Name",
        "desc": "Показывает скорость, угол и круг над каждым игроком.",
        "version": "1.0"
    }

def __init__(self, *argvs, **kwargs):
    """
    вызывается при инициализации
    """
    print("Player Info Mod loaded")

def draw(self):
    """
    вызывается при отрисовке
    """
    for player in self.players:
        params = get_player_params(player)
        draw_player_info(player, params)

def update(self, dt):
    """
    вызывается каждый кадр 
    """

def handle_event(self, event_type, *argvs, **kwargs):
    """
    обрабатывает события
    """
