PygletGui
=========

GUI framework for Pyglet, one that's not hard to understand but you still get to build your custom gui.

Usage example
=============

Here's a quick demo of what you can do:

```Python
from pyglet_gui import *
from random import randint

class circle(generic_sprite):
	def __init__(self, *args, **kwargs):
		super(circle, self).__init__(*args, **kwargs)
		self.circle = gfx_helpers.create_circle(self.x, self.y, batch=self.batch)
		
	def update(self):
		## == Iterate through the vertices and move their
		##    x and y coordinates accordingly.
		##
		new_vertices = []
		x, y = randint(-1, 1), randint(-1, 1)
		for index in range(0, len(self.circle['blob'].vertices),2):
			old_x, old_y = self.circle['blob'].vertices[index:index+2]
			new_vertices += [old_x+x, old_y+y]
		self.circle['blob'].vertices = new_vertices

class window(main):
	def __init__(self):
		super(window, self).__init__(vsync=True, fps=True)

		## == Create 100 random circles that will float around in space.

		for i in range(100):
			self.add_sprite('circle'+str(i), circle(x=int(self.width/2), y=int(self.height/2), alpha=0))

W = window()
W.run()
```
