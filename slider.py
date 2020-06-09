
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.graphics.instructions import InstructionGroup
from common.gfxutil import AnimGroup, CEllipse

MAX_NUM_OF_DOMINO_SETS = 500

class Slider(InstructionGroup):
    def __init__(self, initial_val, image_pos, image_size):
        super(Slider, self).__init__()
        self.value = initial_val
        self.min_val = 1
        self.max_val = MAX_NUM_OF_DOMINO_SETS
        self.image_size = image_size
        self.image_pos = image_pos

        # self.percent = (self.value - self.min_val) / (self.max_val - self.min_val)

        self.line = Line(points=[image_pos[0], image_pos[1] - Window.height//20, image_pos[0] + image_size[0], image_pos[1] - Window.height//20], width=10)
        self.add(self.line)

        dim_size = min(0.03*Window.width, 0.03*Window.height)
        self.add(Color(rgb=(235/255, 74/255, 90/255)))
        self.slider_knob = CEllipse(cpos=(self.image_pos[0] + (((self.value - self.min_val) / (self.max_val - self.min_val))*self.image_size[0]), self.image_pos[1] - Window.height//20), csize=(dim_size, dim_size))
        self.knob_selected = False
        self.add(self.slider_knob)


    def on_update(self):
        return self.value


    def on_touch_down(self, touch):
        if self.line.points[0] - min(0.03*Window.width, 0.03*Window.height) <= touch.pos[0] <= self.line.points[2] + min(0.03*Window.width, 0.03*Window.height) and \
        self.slider_knob.cpos[1] - min(0.03*Window.width, 0.03*Window.height) <= touch.pos[1] <= self.slider_knob.cpos[1] + min(0.03*Window.width, 0.03*Window.height):
            # touching knob valid slider area, adjust value accordingly
            percent = (touch.pos[0] - self.image_pos[0]) / self.image_size[0]
            self.value = min(self.max_val, max(self.min_val, percent * (self.max_val - self.min_val) + self.min_val))
            self.knob_selected = True
        else:
            self.knob_selected = False

    def on_touch_move(self, touch):
        if self.knob_selected:
            percent = (touch.pos[0] - self.image_pos[0]) / self.image_size[0]
            self.value = min(self.max_val, max(self.min_val, percent * (self.max_val - self.min_val) + self.min_val))
            # self.value = min(max(percent, self.min_val), self.max_val) / self.max_val
            self.slider_knob.cpos = (self.image_pos[0] + (((self.value - self.min_val) / (self.max_val - self.min_val))*self.image_size[0]), self.image_pos[1] - Window.height//20)

    def on_touch_up(self, touch):
        if self.knob_selected:
            self.slider_knob.cpos = (self.image_pos[0] + (((self.value - self.min_val) / (self.max_val - self.min_val))*self.image_size[0]), self.image_pos[1] - Window.height//20)
            self.knob_selected = False
