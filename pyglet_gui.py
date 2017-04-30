import pyglet
from pyglet.gl import *
from collections import OrderedDict
from os.path import isfile
from math import *
from time import time

import traceback
import sys

#from PygletGui.gui_classes import *

# REQUIRES: AVBin for .mp3 etc
pyglet.options['audio'] = ('alsa', 'openal', 'silent')
key = pyglet.window.key
# xfce4-notifyd 
debug = True

class timer():
	def __init__(self):
		print('')
		self.start = time()

	def stop(self, text):
		print('{text} took {time} to finish.'.format(**{'time' : time()-self.start, 'text' : text}))
		self.start = time()


class gfx_manipulation():
	def rotate(sprite_obj, rotation, anchor='center'):
		sprite_obj.image.anchor_x = sprite_obj.image.width / 2
		sprite_obj.image.anchor_y = sprite_obj.image.height / 2
		sprite_obj.rotation = (sprite_obj.rotation+rotation) % 360
		if anchor != 'center':
			sprite_obj.image.anchor_x = 0
			sprite_obj.image.anchor_y = 0
		return True

class gfx_helpers():
	def distance_between(source, target):
		pass

	def angle_between(source, target):
		source_angle = ((atan2(source[0], source[1])/pi*180)+360)%360
		target_angle = ((atan2(target[0], target[1])/pi*180)+360)%360

		a = target_angle - source_angle
		a = (a + 180) % 360 - 180

		return a

	def create_circle(x, y, radius=25, sides=50, batch=None, texture_group=None):
		colors = ()#255,0,0

		# calculate at what degrees each point will be.
		deg = 360/sides

		points = ()#x, y # Starting point is x, y?
		
		prev = None
		for i in range(sides):
			#points += x, y

			
			n = ((deg*i)/180)*pi # Convert degrees to radians
			point = int(radius * cos(n)) + x, int(radius * sin(n)) + y

			if prev:
				points += x, y
				points += prev
				points += point
				colors += (255, i*int(255/sides), 0)*3

			#if prev:
			#	points += int(radius * cos(n)) + x, int(radius * sin(n)) + y

			#colors += (255, i*int(255/sides), 0)
			#self.offsets[i] = int(radius * cos(n)), int(radius * sin(n))
		
			prev = point

		points += x, y
		points += prev
		points += points[2:4]
		colors += (255, 0, 255)*3

		if batch:
			return {
				'blob' : batch.add(int(len(points)/2), pyglet.gl.GL_TRIANGLES, texture_group, ('v2i/stream', points), ('c3B', colors)),
				'x' : x,
				'y' : y
			}
		else:
			return points

	def clean_vertexes(*args):
		clean_list = []
		for pair in args:
			clean_list.append((int(pair[0]), int(pair[1])))
		return clean_list

	def create_lines(source, target):
		pass # Some how take a previous line object and append to it.
		# glColor4f(color[0], color[1], color[2], color[3])
		# glBegin(GL_LINES)
		# glVertex2f(xy[0], xy[1])
		# glVertex2f(dxy[0], dxy[1])
		# glEnd()

	def create_square(bottom_left, top_left, top_right, bottom_right, color=(0.2, 0.2, 0.2, 0.5)):
		## TODO: Does not return a vertex blob.

		#glColor4f(0.2, 0.2, 0.2, 1)
		#glBegin(GL_LINES)

		bottom_left, top_left, top_right, bottom_right = self.clean_vertexes(bottom_left, top_left, top_right, bottom_right)

		c = (255, 255, 255, 128)

		window_corners = [
			(bottom_left[0],bottom_left[1],c),	# bottom left
			(top_left[0],top_left[1],c),	# top left
			(top_right[0],top_right[1],c),	# top right
			(bottom_right[0],bottom_right[1],c)		# bottom right
		]

		box_vl = self.pixels_to_vertexlist(window_corners)
		box_vl.draw(pyglet.gl.GL_QUADS)
		#glEnd()

	def gen_solid_image(width, height, color='#FF0000', alpha=255):
		if type(color) == str:
			c = color.lstrip("#")
			c = max(6-len(c),0)*"0" + c
			r = int(c[:2], 16)
			g = int(c[2:4], 16)
			b = int(c[4:], 16)
		else:
			r,g,b = color
		
		c = (r,g,b,alpha)
		return pyglet.image.SolidColorImagePattern(c).create_image(width, height)

	def pixels_to_vertexlist(pixels):
		# Outdated pixel conversion code
		vertex_pixels = []
		vertex_colors = []

		for pixel in pixels:
			vertex = list(pixel)
			vertex_pixels += vertex[:-1]
			vertex_colors += list(vertex[-1])

		# Old pyglet versions (including 1.1.4, not including 1.2
		# alpha1) throw an exception if vertex_list() is called with
		# zero vertices. Therefore the length must be checked before
		# calling vertex_list().
		#
		# TODO: Remove support for pyglet 1.1.4 in favor of pyglet 1.2.
		if len(pixels):
			return pyglet.graphics.vertex_list(
				len(pixels),
				('v2i', tuple(vertex_pixels)),
				('c4B', tuple(vertex_colors)))
		else:
			return None

class generic_sprite(pyglet.sprite.Sprite):
	def __init__(self, texture=None, width=None, height=None, color="#C2C2C2", alpha=int(255), x=None, y=None, parent=None, anchor=None, moveable=True, batch=None):
		if not texture or not isfile(texture):
			#print('No texutre could be loaded for sprite, generating a blank one.')
			## If no texture was supplied, we will create one
			if not width:
				width = 10
			if not height:
				height = 10
			self.texture = gfx_helpers.gen_solid_image(width, height, color, alpha)
		else:
			self.texture = pyglet.image.load(texture)

		if not batch:
			#print('Sprite defaults to default page')
			batch = pages['default']['batch']
			#batch = __builtins__['pages']['default']
		

		super(generic_sprite, self).__init__(self.texture, batch=batch)
		self.batch = batch

		self.anchor = anchor
		if anchor == 'center':
			self.image.anchor_x = self.image.width / 2
			self.image.anchor_y = self.image.height / 2

		if x:
			self.x = x
		if y:
			self.y = y

		self.parent = parent
		self.moveable = moveable
		self.sprites = {}
		self.updated = True # First render is always a updated

	def draw_border(self, color=(0.2, 0.2, 0.2, 0.5)):
		pass # use the create_lines() function instead.
		# self.draw_line((self.x, self.y), (self.x, self.y+self.height), color)
		# self.draw_line((self.x, self.y+self.height), (self.x+self.width, self.y+self.height), color)
		# self.draw_line((self.x+self.width, self.y+self.height), (self.x+self.width, self.y), color)
		# self.draw_line((self.x+self.width, self.y), (self.x, self.y), color)

	def draw_header(self):
		pass # Is this a function we want to keep?

		#self.draw_square((self.x, self.y), (self.x, self.y+self.height), (self.x+self.width, self.y+self.height), (self.x+self.width, self.y))

	def rotate(self, deg):
		gfx_manipulation.rotate(self, deg)

	def fade_in(self):
		self.opacity += 10
		if self.opacity > 255:
			self.opacity = 255

	def fade_out(self):
		self.opacity -= 2.5
		if self.opacity < 0:
			self.opacity = 0

	def mouse_inside(self, x, y, button=None):
		"""
		When called, we first iterate our sprites.
		If none of those returned a click, we'll
		check if we're inside ourselves.
		This is because some internal sprites might go
		outside of the object boundaries.
		"""
		for sname, sobj in self.sprites.items():
			check_sobj = sobj.mouse_inside(x, y, button)
			if check_sobj:
				return check_sobj

		if x > self.x and x < (self.x + self.width):
			if y > self.y and y < (self.y + self.height):
				return self

	def click(self, x, y):
		"""
		Usually click_check() is called followed up
		with a call to this function.
		Basically what this is, is that a click
		should occur within the object.
		Normally a class who inherits Spr() will create
		their own click() function but if none exists
		a default must be present.
		"""
		return True

	def right_click(self, x, y):
		"""
		See click(), same basic concept
		"""
		return True

	def hover(self, x, y):
		"""
		See click(), same basic concept
		"""
		return True

	def hover_out(self, x, y):
		"""
		See click(), same basic concept
		"""
		return True

	def type(self, what):
		"""
		Type() is called from main() whenever a key-press
		has occured that is type-able.
		Meaning whenever a keystroke is made and it was
		of a character eg. A-Z it will be passed as a str()
		representation to type() that will handle the character
		in a given manner.
		This function doesn't process anything but will need
		to be here in case a class that inherits Spr() doesn't
		have their own function for it (which, they should...) 
		"""
		return True

	def gettext(self):
		return ''

	def move_to(self, x, y):
		"""
		Since we're moving the parent to a specific cordinate,
		we've got to traverse through all children and update their
		position as well. But before we do that we gotta meassure
		the offset from the parents X,Y cordinates so that when we
		place the child, it will retain the same offset.
		"""
		for sprite in self.sprites:
			xlat = max(self.x, self.sprites[sprite].x) - min(self.x, self.sprites[sprite].x)
			ylat = max(self.y, self.sprites[sprite].y) - min(self.y, self.sprites[sprite].y)
			self.sprites[sprite].x = x+xlat
			self.sprites[sprite].y = y+ylat
		self.x = x
		self.y = y

	def move(self, x, y):
		if self.moveable:
			self.x += x
			self.y += y
			for sprite in self.sprites:
				self.sprites[sprite].x += x
				self.sprites[sprite].y += y

	def _draw(self):
		if self.updated:
			self.draw()

	def update(self):
		"""
		Called each render iteration, if you don't have anything to update?
		Then simply call return False/None and be done with it. This is taxing!

		"""
		return False

class fps_counter(generic_sprite):
	def __init__(self, *args, **kwargs):
		super(fps_counter, self).__init__(*args, **kwargs)
		self.text = '- fps'
		self.fps = 0
		self.last_udpate = time()
		self.lbl = pyglet.text.Label(self.text, x=kwargs['x'], y=kwargs['y'])

	def update(self):
		self.fps += 1

		if time()-self.last_udpate>1:
			self.lbl.text = str(self.fps) + 'fps'
			self.fps = 0
			self.last_udpate = time()
		
		self.lbl.draw()


class main(pyglet.window.Window):
	def __init__ (self, width=800, height=600, fps=False, *args, **kwargs):
		super(main, self).__init__(width, height, *args, **kwargs)
		self.x, self.y = 0, 0

		self.sprites = OrderedDict()
		self.pages = {'default' : {'batch' : pyglet.graphics.Batch(), 'sprites' : {}}}
		self.active_pages = OrderedDict()
		self.active_pages['default'] = True
		
		self.merge_sprites_dict = {}
		self.t_merge_sprites_dict = {}

		__builtins__['pages'] = self.pages

		## == Demo sprites:
		# if demo:
		# 	self.sprites['1-bg'] = Spr('background.jpg')
		# 	self.sprites['2-test'] = Spr(x=0, y=0, height=self.height, moveable=False)
		# 	self.sprites['3-menu'] = Menu(self, {'Main' : {}, 'Preferences' : {}})

		# 	test_list = {}#{'test' : 'value of test', 'something' : 'has a value'}
		# 	for i in range(0, 45):
		# 		test_list['List item ' + str(i)] = i
		# 	self.sprites['4-test-list'] = List(self.sprites['2-test'], test_list, height=self.height-20)

		# 	self.pages['main'] = ('1-bg', '2-test', '3-menu', '4-test-list')

		if fps:
			self.add_sprite('fps_label', fps_counter(x=self.width/2-30, y=30, alpha=0, width=120))

		self.drag = False
		self.active = OrderedDict()

		self.keys = OrderedDict()
		
		self.mouse_x = 0
		self.mouse_y = 0

		self.alive = 1

	def on_draw(self):
		self.render()

	def on_close(self):
		self.alive = 0

	def add_page(self, name, batch):
		self.pages[name] = {'batch' : batch, 'sprites' : {}}

	def swap_page(self, name):
		if name in self.pages:
			self.active_pages = OrderedDict()
			self.active_pages[name] = True

	def add_layer(self, name):
		self.active_pages[name] = True

	def remove_layer(self, name):
		del self.active_pages[name]

	def t_add_sprite(self, name, sprite_obj, sprite_parameters):
		""" A version of add_sprite() that's thread friendly.
		You can pass the intended sprite object, but we'll set it
		up from here so we don't cause a invalid GL operation"""

		self.t_merge_sprites_dict[name] = {'sprite_obj' : sprite_obj, 'conf' : sprite_parameters}

	def add_sprite(self, name, sprite_obj):
		self.merge_sprites_dict[name] = sprite_obj

	def merge_sprites(self):
		## We're using self.merge_sprites_dict here so that sub-items
		## can add back new graphical content but not in the active
		## pool of rendered objects, instead we'll lift them in for
		## the subitems so they don't have to worry about cycles
		## or how to deal with them.

		while len(self.merge_sprites_dict) > 0:
			name, sprite = self.merge_sprites_dict.popitem()
			if name in self.sprites:
				print('[WARNING] Sprite {name} already exists, replaceing!'.format(**{'name' : name}))

			self.sprites[name] = sprite

			self.pages[ list(page for page in self.active_pages.keys())[-1] ]['sprites'][name] = sprite

		while len(self.t_merge_sprites_dict) > 0:
			name, values = self.t_merge_sprites_dict.popitem()
			if name in self.sprites:
				print('[WARNING] Sprite {name} already exists, replaceing!'.format(**{'name' : name}))

			last_page = list(page for page in self.active_pages.keys())[-1]

			self.sprites[name] = values['sprite_obj'](**values['conf'])
			self.pages[last_page]['sprites'][name] = self.sprites[name]
			#self.pages[page]['sprites']

	def on_mouse_motion(self, x, y, dx, dy):
		self.mouse_x = x
		self.mouse_y = y
		for sprite_name, sprite in self.sprites.items():
			if sprite:
				sprite_obj = sprite.mouse_inside(x, y)
				if sprite_obj:
					sprite_obj.hover(x, y)
				else:
					#TODO: Check why not sprite_obj?
					sprite.hover_out(x, y)

	def link_objects(self, start, end):
		pass # Connect them so that when one does move, the other one does too.
			# ergo, not just a graphical link/bond.

	def on_mouse_release(self, x, y, button, modifiers):
		if button == 1:
			if not key.LCTRL in self.keys:
				self.active = OrderedDict()
		elif button == 4:
			for sprite_name, sprite in self.sprites.items():
				if sprite:
					#print('Clickchecking:', sprite, 'with button', button)
					sprite_obj = sprite.mouse_inside(x, y, button)
					if sprite_obj:
						print('[DEBUG] Right clicking inside {name}\'s object: {obj}'.format(**{'name' : sprite_name, 'obj' : sprite_obj}))
						sprite_obj.right_click(x, y)
			

	def on_mouse_press(self, x, y, button, modifiers):
		if button == 1:
			for sprite_name, sprite in self.sprites.items():
				if sprite:
					#print('Clickchecking:', sprite, 'with button', button)
					sprite_obj = sprite.mouse_inside(x, y, button)
					if sprite_obj:
						print('[DEBUG] Activating {name}\'s object: {obj}'.format(**{'name' : sprite_name, 'obj' : sprite_obj}))
						self.active[sprite_name] = sprite_obj


	def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
		self.drag = True

		# Drag the sprites if possible:
		for name, obj in self.active.items():
			obj.move(dx, dy)

		#if None not in self.active:
		#	self.active[1].move(dx, dy)

	def on_key_release(self, symbol, modifiers):
		if symbol == key.LCTRL:
			self.active = OrderedDict()

		try:
			del self.keys[symbol]
		except:
			pass

	def on_key_press(self, symbol, modifiers):
		if symbol == key.ESCAPE: # [ESC]
			self.alive = 0
		#elif symbol == key.LCTRL:
		self.keys[symbol] = True

	def pre_render(self):
		pass

	def render(self):
		#t = timer()
		self.clear()
		#t.stop('clear')
		#self.bg.draw()
		self.pre_render()
		self.merge_sprites()
		#t.stop('merge sprites')

		if len(self.active_pages) <= 0:
			## Fallback in case we've defunked all our pages,
			## lets just print everything we got so the developer
			## knows that he done fuck up somewhere :P
			for sprite_name, sprite in self.sprites.items():
				sprite._draw()
		else:
			for page in self.active_pages.keys():
				if not page in self.pages:
					print('[ERROR] {page} does not exists in pages: {pages}'.format(**{'page' : page, 'pages' : self.pages}))
					continue

				#print('Rendering {page}'.format(**{'page' : page}))

				# Updating the sprites if need be.

				for sprite_name, sprite_obj in self.pages[page]['sprites'].items():
					sprite_obj.update()
				self.pages[page]['batch'].draw()
				#t.stop('Updating + rendering sprites')

				#try:

				# Rendering 6 sprites in a batch took 0.3506476879119873 to finish.
				# Rendering 8 sprites in a batch took 0.46350693702697754 to finish.
				# Rendering 8 sprites in a batch took 0.4786257743835449 to finish.
				# Rendering 9 sprites in a batch took 0.4889793395996094 to finish.
				# Rendering 11 sprites in a batch took 0.580765962600708 to finish.
				# Rendering 14 sprites in a batch took 0.7689478397369385 to finish.
				# Rendering 21 sprites in a batch took 1.0327515602111816 to finish.
				#self.pages[page]['batch'].draw()

				#t.stop('Rendering ' + str(len(self.pages[page]['sprites'])) + ' sprites in a batch')
				#except:
				#	exc_info = sys.exc_info()
				#	print('[ERROR] Could not render page "{name}"'.format(**{'name' : page}))
				#	traceback.print_exception(*exc_info)
				#	del exc_info
				#	exit(1)

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