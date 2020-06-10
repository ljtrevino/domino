import sys, os
sys.path.insert(0, os.path.abspath('..'))

from common.core import BaseWidget, run, lookup
from common.screen import ScreenManager, Screen

from kivy.core.window import Window

from home import Homepage

# Makes window open full screen
# Window.fullscreen = 'auto'

if __name__ == "__main__":
    if (len(sys.argv) >= 2): # ['main.py', 'filepath', '...']
        _, filepath = sys.argv[:2]
        sm = ScreenManager()
        sm.add_screen(Homepage(name='home', filepath=filepath))
        run(sm)
    else:
        print("You must enter a filepath to your image")
