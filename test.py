import json

multiplayer_data = {
    "ip":"127.0.0.1",
    "port":8080,
    "players_count":2
}
with open("multiplayer.json", "w") as js:
    js.write(json.dumps(multiplayer_data))
with open("multiplayer.json", "r") as js:
    print(json.loads(js.read()))