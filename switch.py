
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.graphics.instructions import InstructionGroup
from common.gfxutil import AnimGroup, CEllipse
from kivy.core.image import Image as CoreImage
from PIL import Image, ImageEnhance, ImageOps
from io import BytesIO

class Switch(InstructionGroup):
    def __init__(self):
        super(Switch, self).__init__()

        self.on = False

        dim_size = min(0.05*Window.width, 0.05*Window.height)
        self.line = Line()
        self.switch_knob = CEllipse()
        self.add(self.line)
        self.add(Color(rgb=(235/255, 74/255, 90/255)))
        self.add(self.switch_knob)
        self.add(Color(rgb=(1,1,1)))


        img = ImageOps.invert(Image.open('./dominoes/5-7.png').convert('RGB'))
        data = BytesIO()
        img.save(data, format='png')
        data.seek(0)

        self.white_domino = Rectangle(texture = CoreImage(BytesIO(data.read()), ext='png').texture)
        self.black_domino = Rectangle(texture = CoreImage('./dominoes/5-7.png').texture)
        self.add(self.white_domino)
        self.add(self.black_domino)

    def on_layout(self):
        dim_size = min(0.05*Window.width, 0.05*Window.height)
        self.set_knob_pos()
        self.switch_knob.csize=(dim_size, dim_size)
        self.line.points=[Window.width-1.5*dim_size, Window.height-1*dim_size, Window.width-2.5*dim_size, Window.height-1*dim_size]
        self.line.width=dim_size//2

        self.white_domino.size, self.black_domino.size = (dim_size/2, dim_size) , (dim_size/2, dim_size)
        self.white_domino.pos, self.black_domino.pos = (Window.width-0.75*dim_size, Window.height-1.5*dim_size) , (Window.width-3.75*dim_size, Window.height-1.5*dim_size)

    def on_update(self):
        pass


    def set_knob_pos(self):
        dim_size = min(0.05*Window.width, 0.05*Window.height)
        if self.on:
            self.switch_knob.cpos=(Window.width-1.5*dim_size, Window.height-1*dim_size)
        else:
            self.switch_knob.cpos=(Window.width-2.5*dim_size, Window.height-1*dim_size)

    def on_touch_up(self, touch):
        if self.switch_knob.cpos[0] - self.switch_knob.csize[0] <= touch.pos[0] <= self.switch_knob.cpos[0] + self.switch_knob.csize[0] and \
        self.switch_knob.cpos[1] - self.switch_knob.csize[1]  <= touch.pos[1] <= self.switch_knob.cpos[1] + self.switch_knob.csize[1]:
            self.on = not self.on
            self.set_knob_pos()
