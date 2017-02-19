import pyglet
from pyglet.gl import *
from collections import OrderedDict
#from threading import *

from PygletGui.gui_classes import *

# REQUIRES: AVBin
pyglet.options['audio'] = ('alsa', 'openal', 'silent')
key = pyglet.window.key
# xfce4-notifyd 
debug = True

class main(pyglet.window.Window):
	def __init__ (self, demo=False):
		super(main, self).__init__(800, 800, fullscreen = False)
		self.x, self.y = 0, 0

		self.sprites = OrderedDict()
		self.pages = {'_active_' : None}
		self.lines = {}
		self.merge_sprites_dict = {}

		## == Demo sprites:
		if demo:
			self.sprites['1-bg'] = Spr('background.jpg')
			self.sprites['2-test'] = Spr(x=0, y=0, height=self.height, moveable=False)
			self.sprites['3-menu'] = Menu(self, {'Main' : {}, 'Preferences' : {}})

			test_list = {}#{'test' : 'value of test', 'something' : 'has a value'}
			for i in range(0, 45):
				test_list['List item ' + str(i)] = i
			self.sprites['4-test-list'] = List(self.sprites['2-test'], test_list, height=self.height-20)

			self.pages['main'] = ('1-bg', '2-test', '3-menu', '4-test-list')

		self.drag = False
		self.active = None, None
		self.alive = 1
		self.multiselect = False

	def on_draw(self):
		self.render()

	def on_close(self):
		self.alive = 0

	def add_page(self, name, sprites):
		self.pages[name] = sprites

	def swap_page(self, name):
		if name in self.pages:
			self.pages['_active_'] = name

	def add_merge_sprites(self, sprites):
		for key, val in sprites.items():
			self.sprites[key] = val

	def merge_sprites(self):
		## We're using self.merge_sprites_dict here so that sub-items
		## can add back new graphical content but not in the active
		## pool of rendered objects, instead we'll lift them in for
		## the subitems so they don't have to worry about cycles
		## or how to deal with them.

		if len(self.merge_sprites_dict) > 0:
			merge_sprite = self.merge_sprites_dict.popitem()
			#if merge_sprite[0] == 'input':
			#	self.requested_input = merge_sprite[1][0]
			#	self.sprites[merge_sprite[0]] = merge_sprite[1][1]
			#else:
			self.sprites[merge_sprite[0]] = merge_sprite[1]

	def on_mouse_motion(self, x, y, dx, dy):
		for sprite_name, sprite in self.sprites.items():
			if sprite:
				sprite_obj = sprite.click_check(x, y)
				if sprite_obj:
					sprite_obj.hover(x, y)
				else:
					sprite.hover_out(x, y)

	def link_objects(self, start, end):
		start_obj, end_obj = None, None
		for sprite_name, sprite in self.sprites.items():
			if sprite and sprite_name not in ('2-loading'):
				if sprite.click_check(start[0], start[1]):
					start_obj = sprite_name, sprite
				if sprite.click_check(end[0], end[1]):
					end_obj = sprite_name, sprite

		del(self.lines['link'])
		if start_obj and end_obj and end_obj[0] != start_obj[0]:
			start_obj[1].link(end_obj[1])

	def on_mouse_release(self, x, y, button, modifiers):
		if button == 1:
			if self.active[1] and not self.drag and self.multiselect == False:
				if debug:
					print('[DEBUG] Clicking inside ' + self.active[0] +'\'s object',self.active[1])

				self.active[1].click(x, y, self.merge_sprites_dict)
				#if self.active[0] == 'menu':
				#	del(self.sprites['menu'])
			self.drag = False
			if 'link' in self.lines:
				##   link_objects( lines == ((x, y), (x, y)) )
				self.link_objects(self.lines['link'][0], self.lines['link'][1])
		elif button == 4:
			if not self.active[0]:
				pass #Do something on empty spaces?
			else:
				self.active[1].right_click(x, y, self.merge_sprites_dict)
			#self.sprites['temp_vm'] = virtualMachine(pos=(x-48, y-48))
			#self.requested_input = self.sprites['temp_vm'].draws['1-title']
			#self.sprites['input'] = Input("Enter the name of your virtual machine", pos=(int(self.width/2-128), int(self.height/2-60)), height=120)

		if type(self.active[1]) != Input:
			self.active = None, None
	
	def on_mouse_press(self, x, y, button, modifiers):
		if button == 1 or button == 4:
			for sprite_name, sprite in self.sprites.items():
				if sprite:
					sprite_obj = sprite.click_check(x, y)
					if sprite_obj:
						if debug:
							print('[DEBUG] Activating ' + sprite_name + '\'s object',sprite_obj)
						self.active = sprite_name, sprite_obj
						if button == 1:
							if self.multiselect != False:
								if sprite_name not in self.multiselect:
										self.multiselect.append(sprite_name)

	def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
		self.drag = True
		if self.active[1] and self.multiselect == False and hasattr(self.active[1], 'link'):
			self.lines['link'] = ((self.active[1].x+(self.active[1].width/2), self.active[1].y+(self.active[1].height/2)), (x,y))
		elif self.multiselect:
			for obj in self.multiselect:
				self.sprites[obj].move(dx, dy)

	def on_key_release(self, symbol, modifiers):
		if symbol == key.LCTRL:
			self.multiselect = False

	def on_key_press(self, symbol, modifiers):
		if symbol == 65307: # [ESC]
			self.alive = 0
		elif symbol == key.LCTRL:
			self.multiselect = []
		if self.active[1] and type(self.active[1]) == Input:
			if symbol == key.SPACE:
				self.active[1].draws['input'].type(' ')
			elif symbol == key.F11:
				pass #window.set_fullscreen(not window.fullscreen)
			elif symbol == key.ENTER:
				self.sprites[self.active[0]].input = self.active[1].gettext()
				self.active = None, None
			else:
				try:
					self.active[1].type(chr(symbol))
				except:
					pass

	def draw_line(self, xy, dxy):
		glColor4f(0.2, 0.2, 0.2, 1)
		glBegin(GL_LINES)
		glVertex2f(xy[0], xy[1])
		glVertex2f(dxy[0], dxy[1])
		glEnd()

	def render(self):
		self.clear()
		#self.bg.draw()

		for group_name in self.lines:
			if group_name == 'link':
				xy = self.lines[group_name][0]
				dxy = self.lines[group_name][1]
			else:
				xy = self.lines[group_name][0].x+self.lines[group_name][0].width/2, self.lines[group_name][0].y+self.lines[group_name][0].height/2
				dxy = self.lines[group_name][1].x+self.lines[group_name][1].width/2, self.lines[group_name][1].y+self.lines[group_name][1].height/2

			self.draw_line(xy, dxy)

		self.merge_sprites()


		## Some special code for creating the "header",
		## I'f prefer to put that into a Spr() class with a width and stuff.
		#glPointSize(25)
		#glColor4f(0.2, 0.2, 0.2, 0.5)	
		#glEnable(GL_BLEND)
		#glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
		#glBegin(GL_POINTS)
		#for x in range(0,self.width+25,25):
		#	for y in range(0-64-15,0,25):
		#		glVertex3f(x, self.height+y, 0)
		#glEnd()
		#self.draw_line((0, self.height-64-26), (self.width, self.height-64-26))
		
		if self.pages['_active_'] is None:
			for sprite_name, sprite in self.sprites.items():
				if sprite and sprite_name not in ('msgbox', 'input', 'menu'):
					sprite._draw()

			if self.multiselect != False:
				for sprite_name in self.multiselect:
					sprite = self.sprites[sprite_name]
					if sprite.moveable:
						sprite.draw_border(color=(0.2, 1.0, 0.2, 0.5))

			if 'menu' in self.sprites:
				self.sprites['menu']._draw()

			if 'input' in self.sprites:
				self.sprites['input']._draw()
		else:
			for sprite_name in self.pages[self.pages['_active_']]:
				self.sprites[sprite_name]._draw()

		#if 'msgbox' in self.sprites:
		#	if self.sprites['msgbox']:
		#		self.sprites['msgbox']._draw()

		#	if self.sprites['msgbox'] and self.sprites['msgbox'].Answer != None:
		#		print('None')

		self.flip()

	def run(self):
		while self.alive == 1:
			self.render()

			# -----------> This is key <----------
			# This is what replaces pyglet.app.run()
			# but is required for the GUI to not freeze
			#
			event = self.dispatch_events()

if __name__ == '__main__':
	x = main()
	x.run()