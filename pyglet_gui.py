import pyglet
from pyglet.gl import *
from collections import OrderedDict
from os.path import isfile
from math import *
from time import time
from random import choice

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

class RenderError(Exception):
	def __init__(self, message, errors=None):
		super(RenderError, self).__init__(message)
		self.errors = errors

class gfx():
	colors = {
		#'rasin_black' : '#271F30',
		'umber' : '#6C5A49',
		'vegas_gold' : '#C8AD55',
		'tea_green' : '#D0FCB3',
		'eton_blue' : '#9BC59D'
	}

	def hex_to_colorpair(hex):
		c = hex.lstrip("#")
		c = max(6-len(c),0)*"0" + c
		r = int(c[:2], 16)
		g = int(c[2:4], 16)
		b = int(c[4:], 16)
		return r,g,b

	def distance_between(source, target):
		return (source[0] - target[0], source[1] - target[1])

	def angle_between(source, target):
		source_angle = ((atan2(source[0], source[1])/pi*180)+360)%360
		target_angle = ((atan2(target[0], target[1])/pi*180)+360)%360

		a = target_angle - source_angle
		a = (a + 180) % 360 - 180

		return a

	def create_circle(x, y, radius=25, sides=50, batch=None, texture_group=None, colors=None):
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
			prev = point

		points += x, y
		points += prev
		points += points[2:4]

		if batch:
			if not colors: raise RenderError("Need colors when creating a batch-connected circle. len(vertices)/2 of them!")
			return {
				'blob' : batch.add(int(len(points)/2), pyglet.gl.GL_TRIANGLES, texture_group, ('v2i/stream', points), ('c3B', colors)),
				'x' : x,
				'y' : y
			}
		else:
			return points

class genericShape():
	def __init__(self, *args, **kwargs):
		pass

class ImageObject():
	def __init__(self, image, *args, **kwargs):
		if not image and 'height' in kwargs and 'width' in kwargs:
			self.texture = self.generate_image(*args, **kwargs)
		elif type(image) == str:
			self.texture = pyglet.image.load(image)
		else:
			self.texture = image

		self.updated = False

	def generate_image(self, *args, **kwargs):
		if not 'width' in kwargs or not 'height' in kwargs:
			raise RenderError("Can not create image texture without width and height.")
		if not 'alpha' in kwargs: kwargs['alpha'] = 255
		if not 'color' in kwargs:
			kwargs['color'] = gfx.colors[choice(list(gfx.colors.keys()))]
		c = gfx.hex_to_colorpair(kwargs['color'])
		c = (*c, kwargs['alpha'])
		return pyglet.image.SolidColorImagePattern(c).create_image(kwargs['width'], kwargs['height'])

	def pixel(self, x, y, new_pixel):
		if self.texture:
			width = self.texture.width
			data = self.texture.get_image_data().get_data('RGBA', width*4)

			start = (width*4*y) + (x*4)
			data = data[:start] + new_pixel + data[start+4:]

			self.texture.set_data('RGBA', width*4, data)
			self.image = self.texture
		else:
			raise RenderError("Can not manipulate pixels on a empty ImageObject (initialize with width, height or texture first).")

	def render(self):
		raise RenderError("Image object can't be drawn directly, wrap it in genericSprite()")

class genericSprite(ImageObject, pyglet.sprite.Sprite):
	def __init__(self, texture=None, parent=None, moveable=True, batch=None, *args, **kwargs):
		ImageObject.__init__(self, texture, *args, **kwargs)
		if self.texture:
			sprite_kwargs = kwargs.copy()
			for item in list(sprite_kwargs.keys()):
				# List taken from: https://pyglet.readthedocs.io/en/stable/modules/sprite.html#pyglet.sprite.Sprite
				if item not in ('img', 'x', 'y', 'blend_src', 'blend_dest', 'batch', 'group', 'usage', 'subpixel'):
					del(sprite_kwargs[item])
			pyglet.sprite.Sprite.__init__(self, self.texture, **sprite_kwargs)
		else:
			print(f'{self} has no texture, using dummy_draw()')
			self.draw = self.dummy_draw

	def update(self, *args, **kwargs):
		pass

	def pre_render(self, *args, **kwargs):
		pass

	def dummy_draw(self):
		pass

	def render(self):
		self.draw()

class fps_counter(genericSprite):
	def __init__(self, *args, **kwargs):
		super(fps_counter, self).__init__(*args, **kwargs)
		self.text = '- fps'
		self.fps = 0
		self.last_udpate = time()
		self.lbl = pyglet.text.Label(self.text, x=kwargs['x'], y=kwargs['y'])

	def render(self):
		self.fps += 1

		if time()-self.last_udpate>1:
			self.lbl.text = str(self.fps) + 'fps'
			self.fps = 0
			self.last_udpate = time()
		
		self.lbl.draw()


class windowWrapper(pyglet.window.Window):
	def __init__ (self, width=800, height=600, fps=False, *args, **kwargs):
		super(windowWrapper, self).__init__(width, height, *args, **kwargs)
		self.x, self.y = 0, 0

		self.sprites = OrderedDict()
		self.pages = {'default' : {'batch' : pyglet.graphics.Batch(), 'sprites' : {}}}
		self.active_pages = OrderedDict()
		self.active_pages['default'] = True
		
		self.merge_sprites_dict = {}
		self.t_merge_sprites_dict = {}

		__builtins__['pages'] = self.pages

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

	def post_setup(self):
		pass

	def pre_render(self):
		pass

	def render(self):
		#t = timer()
		self.clear()
		self.pre_render()
		self.merge_sprites()
		#t.stop('merge sprites')

		if len(self.active_pages) <= 0:
			## Fallback in case we've defunked all our pages,
			## lets just print everything we got so the developer
			## knows that he done fuck up somewhere :P
			for sprite_name, sprite in self.sprites.items():
				sprite.render()
		else:
			for page in self.active_pages.keys():
				if not page in self.pages:
					print('[ERROR] {page} does not exists in pages: {pages}'.format(**{'page' : page, 'pages' : self.pages}))
					continue

				#print('Rendering {page}'.format(**{'page' : page}))

				for sprite_name, sprite_obj in self.pages[page]['sprites'].items():
					sprite_obj.update()
					if sprite_obj.batch == None:
						sprite_obj.render()
				self.pages[page]['batch'].draw()
				#t.stop('Updating + rendering sprites')

		self.flip()

	def run(self):
		self.merge_sprites()
		self.post_setup()
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