#from pgui import *
from pyglet.gl import *
from pyglet_gui import *
from random import randint

class circle(genericShape):
	def __init__(self, *args, **kwargs):
		## TODO: Add batch
		super(circle, self).__init__('GL_TRIANGLES', *args, **kwargs)
		self.set_color(gfx.hex_to_colorpair(gfx.colors['tea_green'])*int(len(self.vertices)/2))

	def update(self):
		self.move(randint(-1, 1), randint(-1, 1))

class smilyface(genericSprite):
	def __init__(self, *args, **kwargs):
		super(smilyface, self).__init__(*args, **kwargs)

		self.pixel(5, 15, b'\xff\x00\x00\xff')
		self.pixel(10, 15, b'\xff\x00\x00\xff')
		self.pixel(2, 8, b'\xff\x00\x00\xff')
		self.pixel(2, 7, b'\xff\x00\x00\xff')
		self.pixel(3, 6, b'\xff\x00\x00\xff')
		self.pixel(4, 5, b'\xff\x00\x00\xff')
		self.pixel(5, 5, b'\xff\x00\x00\xff')
		self.pixel(6, 5, b'\xff\x00\x00\xff')
		self.pixel(7, 5, b'\xff\x00\x00\xff')
		self.pixel(8, 5, b'\xff\x00\x00\xff')
		self.pixel(9, 5, b'\xff\x00\x00\xff')
		self.pixel(10, 5, b'\xff\x00\x00\xff')
		self.pixel(11, 5, b'\xff\x00\x00\xff')
		self.pixel(12, 5, b'\xff\x00\x00\xff')
		self.pixel(13, 6, b'\xff\x00\x00\xff')
		self.pixel(14, 7, b'\xff\x00\x00\xff')
		self.pixel(14, 8, b'\xff\x00\x00\xff')

class testButton(genericInteractive):
	def __init__(self, *args, **kwargs):
		if not 'theme' in kwargs: kwargs['theme'] = 'default'
		if not 'debug' in kwargs: kwargs['debug'] = False
		genericInteractive.__init__(self, *args, **kwargs)

	def click(self, *args, **kwargs):
		print('Clicked', self)

class window(windowWrapper):
	def __init__(self):
		super(window, self).__init__(vsync=False, fps=True)

		self.add_sprite('circle', circle(x=int(self.width/2), y=int(self.height/2), alpha=0))
		self.add_sprite('smilyface', smilyface(x=100, y=100, width=20, height=20, alpha=0))
		self.add_sprite('webimage', resources.image_from_url('https://hvornum.se/favicon.ico', x=self.width-64, y=self.height-64))
		self.add_sprite('button', testButton(debug=True, label='Click me', x=64, y=self.height-64))

	def key_W(self, symbol, event, modifiers, *args, **kwargs):
		self.camera.move(0, 1)

	def key_S(self, symbol, event, modifiers, *args, **kwargs):
		self.camera.move(0, -1)

	def key_D(self, symbol, event, modifiers, *args, **kwargs):
		self.camera.move(1, 0)

	def key_A(self, symbol, event, modifiers, *args, **kwargs):
		self.camera.move(-1, 0)

W = window()
W.run()