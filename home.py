import glob
import sys, os, math, time
sys.path.insert(0, os.path.abspath('..'))

from common.screen import Screen

from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.graphics import Rectangle, Rotate, PushMatrix, PopMatrix
from kivy.graphics.instructions import InstructionGroup
from kivy.core.image import Image as CoreImage
# from kivy.uix.slider import Slider as KivySlider

from io import BytesIO
from PIL import Image, ImageEnhance, ImageOps
import numpy as np

from slider import Slider
import calculate

class Homepage(Screen) :
    def __init__(self, filepath, **kwargs):
        super(Homepage, self).__init__(**kwargs)

        self.filepath = filepath

        # LEFT IMAGE #
        im = Image.open(filepath).convert("RGBA")
        self.image = im.copy()
        width, height = self.image.size
        self.image_rect = Rectangle(size = (width, height), texture = CoreImage(self.filepath).texture)
        self.canvas.add(self.image_rect)

        # CENTER PIXELATED IMAGE & SLIDER #
        self.pixeate_image = im.convert("L").copy()
        self.pixelate_rect = Rectangle(size = (width, height), texture = CoreImage(self.filepath).texture)
        self.canvas.add(self.pixelate_rect)
        self.value = 1
        self.pixel_slider = Slider(1, ((Window.width - width)//2, (Window.height - height)//2), self.pixelate_rect.size)

        # RIGHT DOMINO IMAGE #


        self.label = Label()
        self.add_widget(self.label)

        self.on_layout((Window.width, Window.height))


    def on_layout(self, winsize):
        width, height = self.image.size
        self.image_rect.pos = (Window.width - width)//20, (Window.height - height)//2
        self.pixelate_rect.pos = (Window.width - width)//2, (Window.height - height)//2

        if self.pixel_slider in self.canvas.children:
            self.canvas.remove(self.pixel_slider)

        self.pixel_slider = Slider(1, self.pixelate_rect.pos, self.pixelate_rect.size)
        self.canvas.add(self.pixel_slider)

        self.label.center_x = Window.width/2
        self.label.center_y = 19*Window.height/20
        self.label.font_size = str(Window.width//170) + 'sp'

    def on_touch_down(self, touch):
        self.pixel_slider.on_touch_down(touch)

    def on_touch_up(self, touch):
        self.pixel_slider.on_touch_up(touch)

    def on_touch_move(self, touch):
        self.pixel_slider.on_touch_move(touch)

    def on_update(self):
        if not self.value == self.pixel_slider.on_update():
            self.value = self.pixel_slider.on_update()

            # Resize smoothly down to 16x16 pixels
            width_in_pixels = max(1, round(self.image.size[0]*self.value))
            height_in_pixels = max(1, round(self.image.size[1]*self.value))
            imgSmall = self.image.resize((width_in_pixels, height_in_pixels), resample=Image.BILINEAR)

            print(str(width_in_pixels) + 'x' + str(height_in_pixels))
            print("sets of dominoes required: " + str(math.ceil(width_in_pixels*height_in_pixels / 55)))

            # calculate.generate_domino_graphics(imgSmall, width_in_pixels, height_in_pixels)

            # Scale back up using NEAREST to original size
            self.pixeate_image = imgSmall.resize(self.image.size, Image.NEAREST).convert("L")

            data = BytesIO()
            self.pixeate_image.save(data, format='png')
            data.seek(0)

            # update image
            self.pixelate_rect.texture = CoreImage(BytesIO(data.read()), ext='png').texture

            # update label
            self.label.text = "This requires " + str(math.ceil(width_in_pixels*height_in_pixels / 55)) + " sets of dominoes"
