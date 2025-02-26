import arcade, pickle
sprite = arcade.Sprite()
ar = {"sprite":sprite}
print(pickle.dumps(ar))

