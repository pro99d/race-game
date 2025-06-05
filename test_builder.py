import arcade
from arcade import  key




class Rect:
    def __init__(self, x, y, width, height, color, angle=0):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.angle = angle
    def draw(self):
        arcade.draw_rectangle_filled(self.x, self.y, self.width, self.height, self.color, self.angle)
    def move(self, dx, dy):
        self.x+= dx
        self.y+= dy
class Window(arcade.Window):
    def __init__(self):
        super().__init__(
            width=800,
            height=600,
            title='Test',
            fullscreen= False,
            resizable=False,
            visible=True,
            vsync=True
        )
        self.camera = arcade.Camera()
        self.rect = Rect(200, 200, 200, 200, (23, 255, 100))
        self.keys = []
        self.velocity = [0, 0]
        self.G = (0, -9.8)
        self.resolution = 100 # pix/meter 
    def on_draw(self):
        self.clear()
        self.camera.use()
        self.rect.draw()
    def on_update(self, dt):
        """
        dt: delta time
        """
        self.velocity[0]+=self.G[0]*dt**2*self.resolution
        self.velocity[1]+=self.G[1]*dt**2*self.resolution
        # if key.W in self.keys:
        #     ds[1] = self.speed*dt
        # elif key.S in self.keys:
        #     ds[1] = -self.speed*dt
        # if key.A in self.keys:
        #     ds[0] = -self.speed*dt
        # elif key.D in self.keys:
        #     ds[0] = self.speed*dt
        self.rect.move(self.velocity[0], self.velocity[1])
    def on_key_press(self, key, modifiers):
        self.keys.append(key)
    def on_key_release(self, key, modifiers):
        self.keys.remove(key)

if __name__ == "__main__":
    game = Window()
    arcade.run()
