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

class Homepage(Screen) :
    def __init__(self, filepath, **kwargs):
        super(Homepage, self).__init__(**kwargs)

        self.filepath = filepath
        im = Image.open(filepath).convert("RGBA")
        self.image = im.copy()

        width, height = self.image.size
        self.image_rect = Rectangle(size = (width, height), texture = CoreImage(self.filepath).texture)
        self.canvas.add(self.image_rect)

        self.pixelate_rect = Rectangle(size = (width, height), texture = CoreImage(self.filepath).texture)
        self.canvas.add(self.pixelate_rect)

        self.pixel_slider = Slider(0, ((Window.width - width)//2, (Window.height - height)//2), self.pixelate_rect.size)

        self.on_layout((Window.width, Window.height))

        # self.add_widget(KivySlider(min=0, max=width, value=0))


    def on_layout(self, winsize):
        width, height = self.image.size
        self.image_rect.pos = (Window.width - width)//20, (Window.height - height)//2
        self.pixelate_rect.pos = (Window.width - width)//2, (Window.height - height)//2

        if self.pixel_slider in self.canvas.children:
            self.canvas.remove(self.pixel_slider)

        self.pixel_slider = Slider(0, self.pixelate_rect.pos, self.pixelate_rect.size)
        self.canvas.add(self.pixel_slider)


    def on_touch_up(self, touch):
        self.pixel_slider.on_touch_up(touch)


    def on_update(self):
        self.pixel_slider.on_update()

        data = BytesIO()
        self.image.save(data, format='png')
        data.seek(0)

        # update image
        self.image_rect.texture = CoreImage(BytesIO(data.read()), ext='png').texture
