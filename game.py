#from pgui import *
from pyglet.gl import *
from time import time
from pyglet_gui import *
from random import randint

class bullet(genericShape):
	def __init__(self, *args, **kwargs):
		super(bullet, self).__init__('GL_TRIANGLES', radius=5, *args, **kwargs)
		self.set_color(gfx.hex_to_colorpair(gfx.colors['barbie pink'])*int(len(self.vertices.vertices)/2))

		self.acceleration = 500
		self.direction = 0
		self.last = time()

	def update(self):
		dy = (time()-self.last) * self.acceleration
		self.last = time()
		self.move(0, dy)

		if 0 < self.x > window.width or 0 < self.y > window.height:
			self.delete()
			return True

class player(genericShape):
	def __init__(self, *args, **kwargs):
		## TODO: Add batch
		super(player, self).__init__('GL_TRIANGLES', *args, **kwargs)
		self.set_color(gfx.hex_to_colorpair(gfx.colors['tea_green'])*int(len(self.points)/2))
		self.last_fire = time()-2
		self.fire_rate = 1 / 10
		self.god_mode = False

	def fire(self):
		if self.god_mode or time()-self.last_fire > self.fire_rate:
			add_sprite(f'bullet_{time()}', bullet(x=self.x, y=self.y))
			self.last_fire = time()

	def update(self):
		self.move(randint(-1, 1), randint(-1, 1))

class startButton(genericInteractive):
	def __init__(self, *args, **kwargs):
		if not 'theme' in kwargs: kwargs['theme'] = 'default'
		if not 'debug' in kwargs: kwargs['debug'] = False
		genericInteractive.__init__(self, label="Start!", dragable=False, *args, **kwargs)

	def click(self, *args, **kwargs):
		#self.delete()
		add_sprite('player', player(x=int(window.width/2), y=int(window.height/2), alpha=0))

class _window(windowWrapper):
	def __init__(self):
		super(_window, self).__init__(vsync=False, stats=True, debug=True, log=True, fps=True)

		#self.add_sprite('player', player(x=int(self.width/2), y=int(self.height/2), alpha=0))
		self.add_sprite('webimage', resources.image_from_url('https://hvornum.se/favicon.ico', x=self.width-64, y=self.height-64, dragable=False))
		self.add_sprite('startButton', startButton(x=64, y=self.height-64))

	def key_SPACE(self, *args, **kwargs):
		if 'player' in self.sprites:
			self.sprites['player'].fire()
		
	def key_W(self, symbol, event, modifiers, *args, **kwargs):
		self.camera.move(0, 1)

	def key_S(self, symbol, event, modifiers, *args, **kwargs):
		self.camera.move(0, -1)

	def key_D(self, symbol, event, modifiers, *args, **kwargs):
		self.camera.move(1, 0)

	def key_A(self, symbol, event, modifiers, *args, **kwargs):
		self.camera.move(-1, 0)

	def key_LCTRL(self, symbol, event, *args, **kwargs):
		if 'player' in self.sprites:
			self.sprites['player'].god_mode = True if event == 'press' else False

W = _window()
W.run()