#!/usr/bin/env python3
# Soubor:  kameny.py
# Datum:   06.11.2018 10:01
# Autor:   Marek Nožka, nozka <@t> spseol <d.t> cz
# Licence: GNU/GPL
############################################################################
import pyglet
import random
from math import sin, cos, radians, pi
import glob

from pyglet.window.key import LEFT, RIGHT, UP, DOWN, LCTRL

# from pyglet.window.mouse import LEFT as MouseLEFT

window = pyglet.window.Window(width=1200, height=950)
batch = pyglet.graphics.Batch()  # pro optimalizované vyreslování objektů
bg_batch = pyglet.graphics.Batch()  # pro optimalizované vyreslování objektů


class SpaceObject:
    def __init__(self, img_file, x=None, y=None):

        # načtu obrázek
        self.image = pyglet.image.load(img_file)
        # střed otáčení dám na střed obrázku
        self.image.anchor_x = self.image.width // 2
        self.image.anchor_y = self.image.height // 2
        # z obrázku vytvořím sprite
        self.sprite = pyglet.sprite.Sprite(self.image, batch=batch)

        # pokud není atribut zadán vytvořím ho náhodně
        self._x = x if x is not None else random.randint(0, window.width)
        self._y = y if y is not None else random.randint(0, window.height)
        # musím správně nastavit polohu sprite
        self.x = self._x
        self.y = self._y

        self.max = max(self.image.height, self.image.width)
        self.min = min(self.image.height, self.image.width)

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, new):
        self._x = self.sprite.x = new

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, new):
        self._y = self.sprite.y = new


class Meteor(SpaceObject):
    def __init__(
        self,
        img_file=None,
        x=None,
        y=None,
        direction=None,
        speed=None,
        rspeed=None,
    ):
        if img_file is None:
            img_file = random.choice(glob.glob("img/meteor*.png"))
        super().__init__(img_file, x, y=window.height + 20)

        self.direction = (
            direction if direction is not None else random.randint(150, 220)
        )
        self.speed = speed if speed is not None else random.randint(100, 300)
        self.rspeed = rspeed if rspeed is not None else random.randint(-50, 50)

    def tick(self, dt):
        # do promenne dt se uloží doba od posledního tiknutí
        self.x += dt * self.speed * cos(pi / 2 - radians(self.direction))
        self.sprite.x = self.x
        self.y += dt * self.speed * sin(pi / 2 - radians(self.direction))
        self.sprite.y = self.y
        self.sprite.rotation += dt * self.rspeed

    def __del__(self):
        print("Mem free!")


class Laser(SpaceObject):
    def __init__(self, img_file="img/laser.png", speed=1000):

        # načtu obrázek
        self.image = pyglet.image.load(img_file)
        # střed otáčení dám na střed obrázku
        self.image.anchor_x = self.image.width // 2
        self.image.anchor_y = self.image.height
        # z obrázku vytvořím sprite
        self.sprite = pyglet.sprite.Sprite(self.image, batch=batch)
        self.sprite.z = 0
        self.direction = 0
        self.speed = speed

        self.x = ship.x
        self.y = ship.y + 70

    def tick(self, dt):
        self.y += dt * self.speed


class SpaceShip(SpaceObject):
    def __init__(self, x=None, y=None, speed=300):

        self.keys = set()

        self.fire1 = pyglet.image.load("img/fire07.png")
        self.fire3 = pyglet.image.load("img/fire12.png")
        self.fire1.anchor_x = self.fire1.width // 2
        self.fire1.anchor_y = self.fire1.height
        self.fire3.anchor_x = self.fire3.width // 2
        self.fire3.anchor_y = 0
        self.fireL = pyglet.sprite.Sprite(self.fire1, batch=batch)
        self.fireR = pyglet.sprite.Sprite(self.fire1, batch=batch)
        self.fireFL = pyglet.sprite.Sprite(self.fire3, batch=batch)
        self.fireFR = pyglet.sprite.Sprite(self.fire3, batch=batch)

        # vzdálenost ohně motorů od lodi...
        self.fire_x_dist = 30
        self.fire_y_dist = 39

        super().__init__("img/ship.png", x=window.width / 2, y=77)

        self.speed = speed
        self.width = self.image.width
        self.height = self.image.height

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, new):
        self._x = self.sprite.x = new
        self.fireL.x = self.x - self.fire_x_dist
        self.fireR.x = self.x + self.fire_x_dist
        self.fireFL.x = self.x - 12
        self.fireFR.x = self.x + 12

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, new):
        self._y = self.sprite.y = new
        self.fireL.y = self.y - self.fire_y_dist
        self.fireR.y = self.y - self.fire_y_dist
        self.fireFL.y = self.y + 20
        self.fireFR.y = self.y + 20
        self.fireL.x = self.x - self.fire_x_dist
        self.fireR.x = self.x + self.fire_x_dist

    def tick(self, dt):
        if LEFT in self.keys and self.x > 0:
            self.fire_x_dist = 26
            self.fire_y_dist = 31
            self.x -= dt * self.speed
            self.sprite.rotation = -5
            self.sprite.scale_x = 0.85
        elif RIGHT in self.keys and self.x < window.width:
            self.fire_x_dist = 26
            self.fire_y_dist = 31
            self.x += dt * self.speed
            self.sprite.rotation = 5
            self.sprite.scale_x = 0.85
        else:
            self.sprite.rotation = 0
            self.sprite.scale_x = 1
            self.fire_x_dist = 30
            self.fire_y_dist = 39
        if DOWN in self.keys and self.y > self.height / 2:
            self.y -= dt * self.speed
            self.fireFL.visible = 1
            self.fireFR.visible = 1
        elif UP in self.keys and self.y < window.height - self.height:
            self.y += dt * self.speed
            self.fireL.visible = 1
            self.fireR.visible = 1
        else:
            self.fireL.visible = 0
            self.fireR.visible = 0
            self.fireFL.visible = 0
            self.fireFR.visible = 0


class Meet:
    meteors = list()
    lasers = list()

    def add_meteor(self, dt=None):
        self.meteors.append(Meteor())

    def add_laser(self, dt=None):
        self.lasers.append(Laser())

    def tick(self, dt):
        # pohnu kamenama
        for meteor in self.meteors:
            meteor.tick(dt)
            # vymažu ty, co nejsou vidět
            if (
                meteor.y < 0 - meteor.max
                or meteor.x < 0 - meteor.max
                or meteor.x > window.width + meteor.max
            ):
                meteor.sprite.delete()
                self.meteors.remove(meteor)
            distance = (
                (meteor.x - ship.x) ** 2 + (meteor.y - ship.y) ** 2
            ) ** 0.5
            if distance - meteor.min / 2 - 32 <= 0:
                self.remove = meteor  # schovám si ho abych ho pak vymazal
                self.hit()
                continue
            for laser in self.lasers:
                if (
                    laser.y >= meteor.y
                    and laser.x >= (meteor.x - meteor.min / 3)
                    and laser.x <= (meteor.x + meteor.min / 3)
                ):
                    self.lasers.remove(laser)
                    self.meteors.remove(meteor)
        # pohnu laserama
        for laser in self.lasers:
            laser.tick(dt)
            if laser.y > window.height + laser.sprite.height:
                laser.sprite.delete()
                self.lasers.remove(laser)

    def hit(self):
        pyglet.clock.unschedule(ticktack)
        pyglet.clock.unschedule(meet.add_meteor)
        pyglet.clock.schedule_once(self.renew, 3)

    def renew(self, dt):
        self.remove.sprite.delete()
        self.meteors.remove(self.remove)
        pyglet.clock.schedule_interval(ticktack, 1 / 30)
        pyglet.clock.schedule_interval(meet.add_meteor, 1 / 3)


@window.event
def on_draw():
    window.clear()
    bg_batch.draw()
    batch.draw()


@window.event
def on_key_press(sym, mod):
    # print(sym, mod)
    if sym == LCTRL:
        meet.add_laser()
    else:
        ship.keys |= {
            sym,
        }


@window.event
def on_key_release(sym, mod):
    ship.keys -= {
        sym,
    }


def ticktack(dt):
    meet.tick(dt)
    ship.tick(dt)


# pozadí...
bg = pyglet.image.load("img/bg.img")
x = 0
bg_sprites = ()
while x < window.width:
    y = 0
    while y < window.height:
        bg_sprites += (pyglet.sprite.Sprite(bg, x=x, y=y, batch=bg_batch),)
        y += bg.height
    x += bg.width


ship = SpaceShip()
# print(ship.width)
# print(ship.height)
meet = Meet()
meet.add_meteor()
meet.add_meteor()
meet.add_meteor()
meet.add_meteor()
meet.add_meteor()
pyglet.clock.schedule_interval(ticktack, 1 / 30)
pyglet.clock.schedule_interval(meet.add_meteor, 10 / 3)
pyglet.app.run()
