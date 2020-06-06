#####################################################################
#
# buttons.py
#
# Copyright (c) 2018, Eran Egozy
#
# Released under the MIT License (http://opensource.org/licenses/MIT)
#
#####################################################################

import sys, os
sys.path.insert(0, os.path.abspath('..'))

from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, Line
from kivy.graphics.instructions import InstructionGroup
from kivy.clock import Clock as kivyClock

import photo_editor

from common.gfxutil import CEllipse, CRectangle

import numpy as np


# UI Button for use with a 3D sensor
# valid modes are: 'push', 'relpush', 'hover'

class SensorButton(InstructionGroup) :
    border_color = (23/255, 87/255, 151/255, 1)
    active_color = (63/255, 127/255, 191/255, 0.8)
    on_color     = (63/255, 127/255, 191/255, 1)

    def __init__(self, size = (150,100), pos = (200,200), mode='push', border_color=border_color, active_color=active_color, on_color=on_color, texture=None):
        super(SensorButton, self).__init__()

        # button mode
        self.mode = mode

        self.texture = texture

        self.border_color = border_color
        self.active_color = active_color
        self.on_color     = on_color

        # button state
        self.is_on = False
        self.active_progress = 0

        # bounds of this button, for intersection detection
        self.x_bounds = (pos[0], pos[0] + size[0])
        self.y_bounds = (pos[1], pos[1] + size[1])

        # inside rectangle coordinates
        margin = int(.05 * size[0])
        self.size2 = np.array(size) - margin
        self.pos2 = np.array(pos) + 0.5*margin

        # inside part
        half_m = int(margin/2)
        self.inside_color = Color(rgba=self.active_color)
        self.add( self.inside_color )
        self.inside_circle = CEllipse(cpos = (pos[0]+half_m+(size[0]-margin)/2, pos[1]+half_m + (size[1]-margin)/2), csize = (size[0]-margin, size[1]-margin), angle_end=0)
        self.add( self.inside_circle )

        # icon
        if photo_editor.DARK_MODE:
            self.add(Color(rgba=(1,1,1,0.95)))
        else:
            self.add(Color(rgba=(0,0,0,0.95)))
        self.texture_rect = Rectangle(size = (self.size2[0]*0.7, self.size2[1]*0.7), pos = (self.pos2[0] + self.size2[0]*0.15, self.pos2[1] + self.size2[1]*0.15), texture = self.texture)
        self.add( self.texture_rect )

        # border of button
        self.add( Color(rgba=self.border_color) )
        self.border = Line(circle = (pos[0]+half_m+(size[0]-margin)/2, pos[1]+half_m + (size[1]-margin)/2, (size[0]-margin)/2 ), width=half_m)
        self.add(self.border)


    def update_pos_and_size(self, pos, size):
        self.x_bounds = (pos[0], pos[0] + size[0])
        self.y_bounds = (pos[1], pos[1] + size[1])
        margin = int(.05 * size[0])
        self.size2 = np.array(size) - margin
        self.pos2 = np.array(pos) + 0.5*margin
        half_m = int(margin/2)
        self.inside_circle.cpos = (pos[0]+half_m+(size[0]-margin)/2, pos[1]+half_m + (size[1]-margin)/2)
        self.inside_circle.csize = (size[0]-margin, size[1]-margin)
        self.inside_circle.angle_end = 0
        self.texture_rect.size = (self.size2[0]*0.7, self.size2[1]*0.7)
        self.texture_rect.pos = (self.pos2[0] + self.size2[0]*0.15, self.pos2[1] + self.size2[1]*0.15)
        self.border.circle =  (pos[0]+half_m+(size[0]-margin)/2, pos[1]+half_m + (size[1]-margin)/2, (size[0]-margin)/2 )
        self.border.width = half_m

    def set_screen_pos(self, pos, z) :
        # collision detection
        x,y = pos
        collide = self.x_bounds[0] < x and x < self.x_bounds[1] and self.y_bounds[0] < y and y < self.y_bounds[1]

        if not collide:
            self.is_on = False
            self.active_progress = 0

        # push behavior: z-based activation
        if collide and self.mode == 'push':
            if not self.is_on and z < 0.5:
                self.is_on = True
                self.active_progress = 1
            if self.is_on and z > 0.52:
                self.is_on = False
                self.active_progress = 0

        # relative push:
        if collide and self.mode == 'relpush' and not self.is_on:
            if self.active_progress == 0:
                self.z_anchor = z
            self.active_progress = np.clip( 5. * (self.z_anchor - z), 0.01, 1)
            if self.active_progress == 1.0:
                self.is_on = True

        # hover behavior: timer-based activation
        if collide and self.mode == 'hover':
            self.active_progress += kivyClock.frametime
            if self.active_progress > 1.0:
                self.is_on = True
                self.active_progress = 1


        # button look based on state:
        self.inside_circle.angle_end = 360 * self.active_progress
        self.inside_color.rgba = self.on_color if self.is_on else self.active_color

    def on_update(self):
        self.remove( self.texture_rect )
        if photo_editor.DARK_MODE:
            self.add(Color(rgba=(1,1,1,0.95)))
        else:
            self.add(Color(rgba=(0,0,0,0.95)))
        self.texture_rect = Rectangle(size = (self.size2[0]*0.7, self.size2[1]*0.7), pos = (self.pos2[0] + self.size2[0]*0.15, self.pos2[1] + self.size2[1]*0.15), texture = self.texture)
        self.add( self.texture_rect )

class SensorButtonPhoto(InstructionGroup) :
    border_color = (23/255, 87/255, 151/255, 1)
    active_color = (63/255, 127/255, 191/255, 0.4)
    on_color     = (63/255, 127/255, 191/255, 0.6)

    def __init__(self, path, size = (150,100), pos = (200,200), mode='push', border_color=border_color, active_color=active_color, on_color=on_color, texture=None):
        super(SensorButtonPhoto, self).__init__()

        # button mode
        self.mode = mode

        self.texture = texture
        self.path = path

        self.border_color = border_color
        self.active_color = active_color
        self.on_color     = on_color

        # button state
        self.is_on = False
        self.active_progress = 0

        # bounds of this button, for intersection detection
        self.x_bounds = (pos[0], pos[0] + size[0])
        self.y_bounds = (pos[1], pos[1] + size[1])

        # inside rectangle coordinates
        margin = int(.05 * size[0])
        self.size2 = np.array(size) - margin
        self.pos2 = np.array(pos) + 0.5*margin

        # icon
        self.add(Color(rgba=(1,1,1,1)))
        self.texture_rect = Rectangle(size = (0,0), pos = self.pos2, texture = self.texture)
        self.add( self.texture_rect )

        self.on_enter()

        # inside part
        half_m = int(margin/2)
        self.inside_color = Color(rgba=self.active_color)
        self.add( self.inside_color )
        self.inside_rect = CRectangle(size = (0,0), pos = self.pos2)
        self.add( self.inside_rect )

        # border of button
        self.add( Color(rgba=self.border_color) )
        self.border = Line(rectangle = (pos[0]+half_m, pos[1]+half_m, size[0]-margin, size[1]-margin), width=half_m/2)
        self.add(self.border)

    def update_pos_and_size(self, pos, size):
        self.x_bounds = (pos[0], pos[0] + size[0])
        self.y_bounds = (pos[1], pos[1] + size[1])
        margin = int(.05 * size[0])
        self.size2 = np.array(size) - margin
        self.pos2 = np.array(pos) + 0.5*margin
        half_m = int(margin/2)
        self.inside_rect.cpos = (pos[0]+half_m+(size[0]-margin)/2, pos[1]+half_m + (size[1]-margin)/2)
        self.inside_rect.csize = (size[0]-margin, size[1]-margin)
        self.texture_rect.size = (self.size2[0], self.size2[1])
        self.texture_rect.pos = (self.pos2[0], self.pos2[1])
        self.border.rectangle = (pos[0]+half_m, pos[1]+half_m, size[0]-margin, size[1]-margin)
        self.border.width = half_m/2

    def set_screen_pos(self, pos, z) :
        # collision detection
        x,y = pos
        collide = self.x_bounds[0] < x and x < self.x_bounds[1] and self.y_bounds[0] < y and y < self.y_bounds[1]

        if not collide:
            self.is_on = False
            self.active_progress = 0

        # push behavior: z-based activation
        if collide and self.mode == 'push':
            if not self.is_on and z < 0.5:
                self.is_on = True
                self.active_progress = 1
            if self.is_on and z > 0.52:
                self.is_on = False
                self.active_progress = 0

        # relative push:
        if collide and self.mode == 'relpush' and not self.is_on:
            if self.active_progress == 0:
                self.z_anchor = z
            self.active_progress = np.clip( 5. * (self.z_anchor - z), 0.01, 1)
            if self.active_progress == 1.0:
                self.is_on = True

        # hover behavior: timer-based activation
        if collide and self.mode == 'hover':
            self.active_progress += kivyClock.frametime
            if self.active_progress > 1.0:
                self.is_on = True
                self.active_progress = 1


        # button look based on state:
        self.inside_rect.size = (self.size2[0], self.size2[1] * self.active_progress)
        self.inside_color.rgba = self.on_color if self.is_on else self.active_color

    def on_enter(self):
        self.remove( self.texture_rect )
        self.add(Color(rgba=(1,1,1,1)))
        self.texture_rect = Rectangle(size = (self.size2[0], self.size2[1]), pos = (self.pos2[0], self.pos2[1]), texture = self.texture)
        self.add( self.texture_rect )
