PygletGui
=========

GUI framework for Pyglet, one that's not hard to understand but you still get to build your custom gui.

Usage example
=============

Here's a quick demo of what you can do:

```Python
import PygletGui.gui
from PygletGui.gui_classes import *
from PygletGui.gui_classes_generic import Spr

context = PygletGui.gui.main()

sprites = {
	'menu' : Menu(context, {'Main' : {}, 'Preferences' : {}}),
	'testBtn' : Button("Test button", pos=(40, 300))
}

context.add_merge_sprites(sprites)
context.add_page('main', ['menu', 'testBtn']) # Debug, fix so that we can do 'menu' or ('menu') without the need for ", )"
context.swap_page('main')

context.run()
```
