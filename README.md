PygletGui
=========

GUI framework for Pyglet, one that's not hard to understand but you still get to build your custom gui.

Usage example
=============

Here's a quick demo of what you can do:

```Python
import PygletGui.gui
from PygletGui.gui_classes import *

def test_func(*args, **kwargs):
	print('Pressed a button:', args, kwargs)


context = PygletGui.gui.main()

sprites = {
	'menu' : Menu(context, {'Main' : {}, 'Preferences' : {}}),
	'testBtn' : Button("Test button", pos=(40, 300), func=test_func, func_params={'testing' : True})
}

context.add_merge_sprites(sprites)
context.add_page('main', ['menu', 'testBtn'])
context.swap_page('main')

context.run()
```

And to build your own custom `widgets` (for a lack of better term, even tho I'm not particularly fond of that term), you can do this:

```Python
import PygletGui.gui
from PygletGui.gui_classes import *
from PygletGui.gui_classes_generic import Spr

class myWidget(Spr):
	def __init__(self, title='Test', pos=(0,0), width=64, height=64):
		if not title: return False
		super(myWidget, self).__init__(texture='object.png', width=width, height=height, x=pos[0], y=pos[1])

		self.sprites = {'1-title' : pyglet.text.Label(title, anchor_x='center', font_size=12, x=self.x+self.width/2, y=self.y+self.height-20)}

	def _draw(self):
		self.draw()
		#self.draw_header()
		
		for obj in sorted(self.sprites):
			self.sprites[obj].draw()

		#self.draw_border()

context = PygletGui.gui.main()

sprites = {
	'menu' : Menu(context, {'Main' : {}, 'Preferences' : {}}),
	'testBtn' : Button("Test button", pos=(40, 300)),
	'myWidget1' : myWidget(),
}

context.add_merge_sprites(sprites)
context.add_page('main', ['menu', 'testBtn', 'myWidget1'])
context.swap_page('main')

context.run()
