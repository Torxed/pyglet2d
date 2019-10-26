import pyglet
import urllib.request, io
from pyglet.gl import *
from collections import OrderedDict
from os.path import isfile, basename
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

class resources():
	def image_from_url(url, *args, **kwargs):
		with urllib.request.urlopen(url) as response:
			data = response.read()
		return genericSprite(ImageObject(io.BytesIO(data), path=url), *args, **kwargs)
		# return genericSprite(io.BytesIO(data), path=url, debug=True, *args, **kwargs)

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

class dummyTexture():
	def __init__(self, width, height, *args, **kwargs):
		if not 'debug' in kwargs: kwargs['debug'] = False
		self.debug = kwargs['debug']

		if self.debug:
			print('Initiating dummyTexture()')
		self.width = 0
		self.height = 0
		self.anchor_x = 0
		self.anchor_y = 0
		#self.tex_coords = (0.0, 0.0, 0.0, 0.9375, 0.0, 0.0, 0.9375, 0.9375, 0.0, 0.0, 0.9375, 0.0)
		self.tex_coords = (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
		self.id = 1
		self.target = 3553

	def get_texture(self, *args, **kwargs):
		return self

class ImageObject():
	def __init__(self, image, *args, **kwargs):
		if not 'batch' in kwargs: kwargs['batch'] = pyglet.graphics.Batch()
		if not 'debug' in kwargs: kwargs['debug'] = False
		self.updated = False
		self.debug = kwargs['debug']

		if not image and 'height' in kwargs and 'width' in kwargs and ('_noBackdrop' not in kwargs or kwargs['_noBackdrop'] == False):
			if self.debug:
				print(self, 'Generating image', kwargs)
			self.texture = self.generate_image(*args, **kwargs)
			#self._texture = self.texture.get_texture()
		elif type(image) == str:
			if self.debug:
				print(self, 'Loading file')
			self.texture = pyglet.image.load(image)
			#self._texture = self.texture.get_texture()
		elif type(image) == io.BytesIO:
			if self.debug:
				print(self, 'Loading bytes stream io.bytes')
			self.texture = pyglet.image.load(basename(kwargs['path']), file=image)
			#self._texture = self.texture.get_texture()
		elif type(image) == bytes:
			if self.debug:
				print(self, 'Loading bytes stream from bytes')
			tmp = io.BytesIO(image)
			self.texture = pyglet.image.load(basename(kwargs['path']), file=tmp)
		elif type(image) == ImageObject:
			if self.debug:
				print(self, 'Merging ImageObject')
			self.texture = image.texture
		else:
			if self.debug:
				print(self, 'Dummy ImageObject')

			self._x = kwargs['x']
			self._y = kwargs['y']
			self.texture = dummyTexture(*args, **kwargs)
			self._texture = self.texture.get_texture()
			self.batch = kwargs['batch']


	def generate_image(self, *args, **kwargs):
		if not 'width' in kwargs or not 'height' in kwargs:
			raise RenderError("Can not create image texture without width and height.")
		if not 'alpha' in kwargs: kwargs['alpha'] = 255
		if not 'color' in kwargs: kwargs['color'] = gfx.colors[choice(list(gfx.colors.keys()))]
		if 'debug' in kwargs and kwargs['debug']:
			print(f'{self}: generate_image({kwargs})')
		
		c = gfx.hex_to_colorpair(kwargs['color'])
		
		return pyglet.image.SolidColorImagePattern((*c, kwargs['alpha'])).create_image(kwargs['width'], kwargs['height'])

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

	def update(self):
		pass

	def pre_render(self):
		pass

	def render(self):
		raise RenderError("Image object can't be drawn directly, wrap it in genericSprite()")

#class tiles():
#	def __init__(self, texture, width, height, batch=None):
#		if not batch: batch = pages['default']['batch']
#
#class animation():
#	def __init__(self, texture, frames, batch=None):
#		if not batch: batch = pages['default']['batch']
#
#class collision():
#	def __init__(self, texture, frames, batch=None):
#		if not batch: batch = pages['default']['batch']

class genericSprite(ImageObject, pyglet.sprite.Sprite):
	def __init__(self, texture=None, parent=None, moveable=True, *args, **kwargs):
		if not 'x' in kwargs: kwargs['x'] = 0
		if not 'y' in kwargs: kwargs['y'] = 0
		if not 'debug' in kwargs: kwargs['debug'] = False
		if not 'batch' in kwargs: kwargs['batch'] = pyglet.graphics.Batch()
		self.debug = kwargs['debug']

		ImageObject.__init__(self, texture, *args, **kwargs)

		#self.batch = kwargs['batch']
		self.sprites = {}

		if self.texture:
			sprite_kwargs = kwargs.copy()
			for item in list(sprite_kwargs.keys()):
				# List taken from: https://pyglet.readthedocs.io/en/stable/modules/sprite.html#pyglet.sprite.Sprite
				if item not in ('img', 'x', 'y', 'blend_src', 'blend_dest', 'batch', 'group', 'usage', 'subpixel'):
					del(sprite_kwargs[item])
			if self.debug:
				print(f'{self}: Creating a Sprite({sprite_kwargs})')
			pyglet.sprite.Sprite.__init__(self, self.texture, **sprite_kwargs)
			if 'width' in kwargs: self.resize(width=kwargs['width'])
			if 'height' in kwargs: self.resize(height=kwargs['height'])
		else:
			if self.debug:
				print(f'{self}: Creating a dummy Sprite({kwargs})')
			self.draw = self.dummy_draw
			self._x = kwargs['x']
			self._y = kwargs['y']
			self._texture = dummyTexture(kwargs['width'], kwargs['height'], *args, **kwargs)
			#moo = pyglet.sprite.Sprite(self.generate_image(*args, **kwargs))
			self.batch = kwargs['batch']
			#self.render = self.dummy_draw
			#self.x = kwargs['x']
			#self.y = kwargs['y']

		self._rot = 0

	def resize(self, width=None, height=None, *args, **kwargs):
		if width:
			self._texture.width = width
		if height:
			self._texture.height = height

	def update(self, *args, **kwargs):
		pass

	def pre_render(self, *args, **kwargs):
		pass

	def dummy_draw(self):
		pass

	def rotate(self, deg, adjust_anchor=True):
		anchors = self._texture.anchor_x, self._texture.anchor_y
		if(anchors == (0, 0) and adjust_anchor):
			x,y = self.x, self.y
			self.x = x + (self.width/2)
			self.y = y + (self.height/2)

		if adjust_anchor:
			self._texture.anchor_x = self.width / 2
			self._texture.anchor_y = self.height / 2

		self._rot = (self._rot + deg) % 360
		self.rotation = self._rot

		#self._texture.anchor_x, self._texture.anchor_y = anchors
		

	def move(self, dx, dy):
		print('Moving:', self)
		self.x += dx
		self.y += dy
		for sprite in self.sprites:
			self.sprites[sprite].x += dx
			self.sprites[sprite].y += dy

	def hover(self, x, y):
		pass

	def hover_out(self, x, y):
		pass

	def mouse_inside(self, x, y, mouse_button=None):
		if self.debug:
			print(f'Inside: {self}, {x, y} | {self.x,self.y}, {self.width, self.height}')
			print(f' {x >= self.x} and {y >= self.y}')
			print(f'   {x <= self.x+self.width} and {y <= self.y+self.height}')
		if x >= self.x and y >= self.y:
			if x <= self.x+self.width and y <= self.y+self.height:
				if self.debug:
					print('   yes')
				return self

	def render(self):
		self.batch.draw()
#		self.draw()

class themedObject():
	def __init__(self, test, *args, **kwargs):
		if not 'theme' in kwargs: kwargs['theme'] = 'default'
		if not 'width' in kwargs: raise RenderError("No width to the theme engine.")
		if not 'height' in kwargs: raise RenderError("No height to the theme engine.")

		if not 'style' in kwargs: kwargs['style'] = {
			'padding' : 0
		}
		if not 'themes' in kwargs: kwargs['themes'] = {
			'default' : {
				'padding' : 10
			}
		}

		if kwargs['theme'] in kwargs['themes']:
			for key, val in kwargs['themes'][kwargs['theme']].items():
				kwargs['style'][key] = val

		#if 'border' in kwargs['style']:


		border = (
			self.x-kwargs['style']['padding'], self.y-kwargs['style']['padding'],
			(self.x-kwargs['style']['padding'])+kwargs['width']+(kwargs['style']['padding']*2), self.y-kwargs['style']['padding'],

			(self.x-kwargs['style']['padding'])+kwargs['width']+(kwargs['style']['padding']*2), self.y-kwargs['style']['padding'],
			(self.x-kwargs['style']['padding'])+kwargs['width']+(kwargs['style']['padding']*2), self.y+kwargs['height'],
			
			(self.x-kwargs['style']['padding'])+kwargs['width']+(kwargs['style']['padding']*2), self.y+kwargs['height'],
			self.x-kwargs['style']['padding'], self.y+kwargs['height'],

			self.x-kwargs['style']['padding'], self.y+kwargs['height'],
			self.x-kwargs['style']['padding'], self.y-kwargs['style']['padding']
		)

		colors = (255,255,255,255) * int(len(border)/2)

		self._list = self.batch.add(int(len(border)/2), gl.GL_LINES, None, 
			('v2f/stream', border), ('c4B', colors)
		)

class genericInteractive(genericSprite, themedObject):
	def __init__(self, *args, **kwargs):
		if not 'label' in kwargs: kwargs['label'] = ''
		if not 'height' in kwargs: kwargs['height'] = 20
		if not 'width' in kwargs: kwargs['width'] = len(kwargs['label'])*8
		if not '_noBackdrop' in kwargs: kwargs['_noBackdrop'] = True
		genericSprite.__init__(self, *args, **kwargs)
		if 'theme' in kwargs:
			themedObject.__init__(self, kwargs, *args, **kwargs)
		self.sprites['label'] = pyglet.text.Label(kwargs['label'], x=kwargs['x'], y=kwargs['y'], batch=self.batch)

	def move(self, dx, dy):
		print(self._list)

#	def render(self):
#		self.label.draw()

class simplified_GL_TRIANGLES():
	def __init__(self, *args, **kwargs):
		self.colors = None
		## TODO: Investigate why `def render()` won't trigger if `self.render` already set...
		## Apparently: https://docs.python.org/3/reference/datamodel.html#descriptors
		## 11:32 < Widdershins> DoXiD: func exists as a class method, but you're setting an attribute with the same name on the instance during 
		##             init, self.func. instance attributes are seen before class attributes (like methods).
		##
		## 11:37 < Widdershins> DoXiD: no. the object instance's attributes are in a completely different place than the class methods, and will 
		##             always override. try putting func = dummy_func in the body of inherited instead of the __init__, or try looking at 
		##             dir(x).
		##
		## 11:39 < cdunklau> DoXiD: the method magic happens because of descriptors. https://docs.python.org/3/reference/datamodel.html#descriptors 
		##          for the gory details
		##
		## 11:39 < Widdershins> DoXiD: you're setting a field of the object that shadows the name of a method it has, to put it briefly
		##
		## 11:39 < Widdershins> DoXiD: if you `del c
		##
		## 11:40 < cdunklau> DoXiD: overall though... this makes me think you're up to no good :)

		# https://cdn.discordapp.com/attachments/463526340168122368/633244634956562432/unknown.png
		#self.render = self._render

	def move(self, dx, dy):
		## == Iterate through the vertices and move their
		##    x and y coordinates accordingly.
		##
		new_vertices = []
		for index in range(0, len(self.vertices),2):
			old_x, old_y = self.vertices[index:index+2]
			new_vertices += [old_x+dx, old_y+dy]

		self.vertices = new_vertices

	def set_color(self, array):
		self.colors = array

	def pre_render(self):
		if self.colors == None:
			self.set_color((255,255,255)*int(len(self.vertices)/2))

	def render(self):
		pyglet.graphics.draw(int(len(self.vertices)/2), pyglet.gl.GL_TRIANGLES,
			('v2i/stream', self.vertices),
			('c3B', self.colors)
		)

class genericShape(simplified_GL_TRIANGLES, genericSprite):
	def __init__(self, shapeType, *args, **kwargs):
		kwargs['width'] = 50
		kwargs['height'] = 50
		kwargs['_noBackdrop'] = True
		genericSprite.__init__(self, *args, **kwargs)

		if shapeType == 'GL_TRIANGLES':
			simplified_GL_TRIANGLES.__init__(self, *args, **kwargs)

		self.circle = gfx.create_circle(kwargs['x'], kwargs['y'], batch=None, radius=25)
		#if self.batch:
		#	self.vertices = self.circle['blob'].vertices
		#else:
		self.vertices = self.circle

class fps_counter(genericInteractive):
	def __init__(self, *args, **kwargs):
		super(fps_counter, self).__init__(*args, **kwargs)
		#self.text = '- fps'
		self.fps = 0
		self.last_udpate = time()
		#self.lbl = pyglet.text.Label(self.text, x=kwargs['x'], y=kwargs['y'])

	def update(self):
		self.fps += 1

		if time()-self.last_udpate>1:

			self.sprites['label'].text = str(self.fps) + 'fps'
			self.fps = 0
			self.last_udpate = time()

class camera():
	# http://docs.gl/gl2/glOrtho
	def __init__(self, x, y, width=None, height=None, parent=None, *args, **kwargs):
		if not 'debug' in kwargs: kwargs['debug'] = False
		if (not width or not height) and not parent:
			raise RenderError("Can not create a camera with no width/height and no parent.\n  Either set width/height OR supply a parent to the camera.")
		if not width: width = parent.width
		if not height: height = parent.height

		self.parent = parent
		self.x = x
		self.y = y
		self.width = width
		self.height = height

		self.debug = kwargs['debug']

	def __iter__(self):
		return iter([self.x, self.x+self.width, self.y, self.y+self.height])

	def move(self, dx, dy):
		self.x += dx
		self.y += dy
		#print(f'Camera moved to: {self.x,self.y} x {self.width, self.height}')

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
			self.add_sprite('fps_label', fps_counter(x=self.width/2-30, y=30, alpha=0, width=120, height=30))

		self.drag = False
		self.active = OrderedDict()

		self.keys = OrderedDict()
		
		self.mouse_x = 0
		self.mouse_y = 0

		self.alive = 1

		self.camera = camera(0, 0, parent=self)
		glClearColor(0/255, 0/255, 0/255, 0/255)

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
					print('Clickchecking:', sprite, 'with button', button)
					sprite_obj = sprite.mouse_inside(x, y, button)
					if sprite_obj:
						print('[DEBUG] Right clicking inside {name}\'s object: {obj}'.format(**{'name' : sprite_name, 'obj' : sprite_obj}))
						sprite_obj.right_click(x, y)
			

	def on_mouse_press(self, x, y, button, modifiers):
		if button == 1:
			for sprite_name, sprite in self.sprites.items():
				if sprite:
					print('Clickchecking:', sprite, 'with button', button)
					sprite_obj = sprite.mouse_inside(x, y, button)
					print(sprite_obj)
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

		func = getattr(self, f'key_{key.symbol_string(symbol)}', None)
		if callable(func):
			self.keys[symbol] = {'func' : func, 'params' : (symbol, 'press', modifiers)}
		else:
			self.keys[symbol] = None

	def post_setup(self):
		pass

	def pre_render(self):
		for key, val in self.keys.items():
			if val: val['func']( *val['params'] )

	def render(self):
		#t = timer()
		#self.clear()
		glClear( GL_COLOR_BUFFER_BIT )

		# Initialize Projection matrix
		glMatrixMode( GL_PROJECTION )
		glLoadIdentity()

		# Initialize Modelview matrix
		glMatrixMode( GL_MODELVIEW )
		glLoadIdentity()

		# Set orthographic projection matrix
		glOrtho(*self.camera, 1, -1 )

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

				for sprite_name, sprite_obj in self.pages[page]['sprites'].items():
					sprite_obj.update()
					sprite_obj.pre_render() # TODO: Might be a hogger
					sprite_obj.render()
				self.pages[page]['batch'].draw()

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