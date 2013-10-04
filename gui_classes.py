import pyglet
from pyglet.gl import *
from gui_classes_generic import Spr

class Input(Spr):
	def __init__(self, title='Test', pos=(0,0), width=None, height=None):
		if not title: return False
		super(Input, self).__init__(width=width, height=height, x=pos[0], y=pos[1])

		self.draws = {'1-title' : pyglet.text.Label(title, anchor_x='center', font_size=12, x=self.x+self.width/2, y=self.y+self.height-20)}
		self.input_cmd = pyglet.text.Label("", font_size=12, x=self.x+10, y=self.y+self.height/2-6)

	def type(self, c):
		self.input_cmd.text += c

	def gettext(self):
		return self.input_cmd.text

	def _draw(self):
		self.draw()
		self.draw_header()
		# top and bottom line:
		self.draw_line((self.x, self.y), (self.x+self.width, self.y))
		self.draw_line((self.x, self.y+self.height), (self.x+self.width, self.y+self.height))
		# left and right line:
		self.draw_line((self.x, self.y), (self.x, self.y+self.height))
		self.draw_line((self.x+self.width, self.y), (self.x+self.width, self.y+self.height))
		for obj in sorted(self.draws):
			self.draws[obj].draw()
		self.input_cmd.draw()

class Menu(Spr):
	def __init__(self, main_spr, buttons={}, align='top', x=0, y=0):
		if not main_spr: return False
		x = main_spr.x+x
		y = main_spr.y+y
		if align=='top':
			y += main_spr.height-20
		super(Menu, self).__init__(width=main_spr.width, height=20, x=x, y=y)
		self.draws = {}
		for obj in buttons:
			self.draws['2-' + obj] = pyglet.text.Label(obj, anchor_x='left', font_size=12, x=x, y=y+2)
			x += len(obj)*10

	def _draw(self):
		self.draw_header()
		for obj in sorted(self.draws):
			self.draws[obj].draw()

	def move(self, x, y):
		self.x += x
		self.y += y
		for obj in self.draws:
			self.draws[obj].x += x
			self.draws[obj].y += y