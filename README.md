pyglet2d
=========

Create 2D/GUI by wrapping pyglet functionality as transparent as possible.<br>
Create buttons, player objects or tiled backgrounds easily. A generic 2D/GUI framework.

Documentation
=============

 * [Wiki](https://github.com/Torxed/pyglet2d/wiki)

Usage example
=============

Here's a quick demo of what you can do:<br>
*(for more examples, see [test.py](/test.py))*

![screenshot](screenshot.png)

```Python
from pyglet_gui import *
from random import randint

class circle(genericShape):
	def __init__(self, *args, **kwargs):
		## TODO: Add batch
		super(circle, self).__init__('GL_TRIANGLES', *args, **kwargs)

	def update(self):
		self.move(randint(-1, 1), randint(-1, 1))

class window(windowWrapper):
	def __init__(self):
		super(window, self).__init__(vsync=True, fps=True)

		self.add_sprite('circle', circle(x=int(self.width/2), y=int(self.height/2), alpha=0))
		self.add_sprite('webimage', resources.image_from_url('https://hvornum.se/favicon.ico', x=self.width-64, y=self.height-64))

W = window()
W.run()
```
