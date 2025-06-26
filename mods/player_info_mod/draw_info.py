import arcade

def draw_player_info(player, params):
    """
    отрисовывает информацию о игроке
    """
    x = player['sprite'].center_x
    y = player['sprite'].center_y + 40
    color = player['sprite'].color
    text = f"Скорость: {params['speed']:.1f}\nУгол: {params['angle']:.1f}\nКруг: {params['lap']}"
    arcade.draw_text(text, x, y, color, 12, anchor_x="center") 
