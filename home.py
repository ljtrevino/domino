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
        self.w_h_ratio = width / height
        self.image_rect = Rectangle(texture = CoreImage(self.filepath).texture)
        self.canvas.add(self.image_rect)

        # CENTER PIXELATED IMAGE & SLIDER #
        self.pixeate_image = im.copy()
        self.pixelate_rect = Rectangle()
        self.canvas.add(self.pixelate_rect)
        self.value = None
        self.pixel_slider = Slider(1, ((Window.width - self.image_rect.size[0])//2, (Window.height - self.image_rect.size[1])//2), self.pixelate_rect.size)

        self.generate_pressed = False
        self.generate_button = Rectangle(texture = CoreImage('./images/generate_button.png').texture)
        self.canvas.add(self.generate_button)

        # RIGHT DOMINO IMAGE #
        self.domino_image = Image.new(mode='RGBA', size=(width, height), color=(235, 74, 90, 150))
        data = BytesIO()
        self.domino_image.save(data, format='png')
        data.seek(0)
        self.domino_rect = Rectangle(texture=CoreImage(BytesIO(data.read()), ext='png').texture)
        self.canvas.add(self.domino_rect)

        self.label = Label()
        self.add_widget(self.label)

        self.imgSmall = None

        self.on_update()
        self.on_layout((Window.width, Window.height))

    def on_layout(self, winsize):
        width, height = self.image.size
        display_width = Window.width/3.5
        self.image_rect.pos = (Window.width-display_width)/20, (Window.height - 1/self.w_h_ratio*display_width)//2
        self.image_rect.size = (display_width, 1/self.w_h_ratio*display_width)
        self.pixelate_rect.pos = (Window.width-display_width)/2, (Window.height - 1/self.w_h_ratio*display_width)//2
        self.pixelate_rect.size = (display_width, 1/self.w_h_ratio*display_width)
        self.domino_rect.pos = 19*(Window.width-display_width)/20, (Window.height - 1/self.w_h_ratio*display_width)//2
        self.domino_rect.size = (display_width, 1/self.w_h_ratio*display_width)

        self.generate_button.pos = (Window.width-0.75*display_width)/2, self.pixelate_rect.pos[1] - Window.height//10 - 0.75*display_width/4.24
        self.generate_button.size = (0.75*display_width, 0.75*display_width/4.24)

        if self.pixel_slider in self.canvas.children:
            self.canvas.remove(self.pixel_slider)

        self.pixel_slider = Slider(1, self.pixelate_rect.pos, self.pixelate_rect.size)
        self.canvas.add(self.pixel_slider)

        self.label.center_x = Window.width/2
        self.label.center_y = (Window.height + 1/self.w_h_ratio*display_width)//2 + Window.height/20
        self.label.font_size = str(Window.width//170) + 'sp'

    def on_touch_down(self, touch):
        self.pixel_slider.on_touch_down(touch)

    def on_touch_up(self, touch):
        self.pixel_slider.on_touch_up(touch)

        # handle generate button press
        if self.generate_button.pos[0] <= touch.pos[0] <= self.generate_button.pos[0] + self.generate_button.size[0] and \
        self.generate_button.pos[1] <= touch.pos[1] <= self.generate_button.pos[1] + self.generate_button.size[1]:
            self.generate_pressed = True
            self.generate_button.texture = CoreImage('./images/generating_button.png').texture

    def on_touch_move(self, touch):
        self.pixel_slider.on_touch_move(touch)

    def on_update(self):
        if not self.value == self.pixel_slider.on_update():
            self.value = self.pixel_slider.on_update()

            # Scale value based on dominoes produced
            num_sets = self.value
            height_in_pixels = max(1, math.sqrt(55*num_sets / self.w_h_ratio))
            # make height even so that number of pixels is even and dominoes can fill entire image
            height_in_pixels = height_in_pixels + 1 if round(height_in_pixels) % 2 == 1 else height_in_pixels
            # round values to nearest integer
            width_in_pixels = round(max(1, self.w_h_ratio * height_in_pixels))
            height_in_pixels = round(height_in_pixels)
            self.imgSmall = self.image.resize((width_in_pixels, height_in_pixels), resample=Image.BILINEAR)

            # Scale back up using NEAREST to original size
            self.pixeate_image = self.imgSmall.resize(self.image.size, Image.NEAREST).convert("L")

            data = BytesIO()
            self.pixeate_image.save(data, format='png')
            data.seek(0)

            # update image
            self.pixelate_rect.texture = CoreImage(BytesIO(data.read()), ext='png').texture

            # update label
            self.label.text = "This would require " + str(math.ceil(width_in_pixels*height_in_pixels / 55)) + " sets of dominoes ( " + str(width_in_pixels*height_in_pixels) + " dominoes in total )"

        # generate domino image on button press
        if self.generate_pressed:
            # create and update domino image
            self.domino_image = calculate.generate_domino_graphics(self.imgSmall, self.imgSmall.size[0], self.imgSmall.size[1])
            data = BytesIO()
            self.domino_image.save(data, format='png')
            data.seek(0)
            self.domino_rect.texture = CoreImage(BytesIO(data.read()), ext='png').texture

            # return generate button to former state
            self.generate_button.texture = CoreImage('./images/generate_button.png').texture
            self.generate_pressed = False
