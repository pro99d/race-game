def get_player_params(player):
    """
    возвращает информацию о игроке
    """
    return {
        'speed': abs(player['speed']),
        'angle': player['current_angle'],
        'lap': player.get('laps', 0)
    } 
