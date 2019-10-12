from pyglet_gui import *
from random import randint

class circle(genericSprite):
	def __init__(self, *args, **kwargs):
		super(circle, self).__init__(*args, **kwargs)
		## TODO: Add batch
		self.circle = gfx.create_circle(kwargs['x'], kwargs['y'], batch=self.batch)
		if self.batch:
			self.vertices = self.circle['blob'].vertices
		else:
			self.vertices = self.circle

	def update(self):
		## == Iterate through the vertices and move their
		##    x and y coordinates accordingly.
		##
		new_vertices = []
		x, y = randint(-1, 1), randint(-1, 1)
		for index in range(0, len(self.vertices),2):
			old_x, old_y = self.vertices[index:index+2]
			new_vertices += [old_x+x, old_y+y]

		self.vertices = new_vertices

	def render(self):
		colors = gfx.hex_to_colorpair(gfx.colors['tea_green'])*int(len(self.vertices)/2)
		pyglet.graphics.draw(int(len(self.vertices)/2), pyglet.gl.GL_TRIANGLES,
			('v2i/stream', self.vertices),
			('c3B', colors)
		)

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

class window(windowWrapper):
	def __init__(self):
		super(window, self).__init__(vsync=True, fps=True)

		## == Create 100 random circles that will float around in space.

		#for i in range(100):
		#	self.add_sprite('circle'+str(i), circle(x=int(self.width/2), y=int(self.height/2), alpha=0))

		self.add_sprite('circle', circle(x=int(self.width/2), y=int(self.height/2), alpha=0))
		self.add_sprite('smilyface', smilyface(x=100, y=100, width=20, height=20, alpha=0))

W = window()
W.run()