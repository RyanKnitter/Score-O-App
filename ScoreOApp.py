import kivy
kivy.require('1.11.1')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.graphics import Line, InstructionGroup, Color
from kivy.properties import (NumericProperty, ListProperty, ObjectProperty)
from kivy.animation import Animation
import datetime as dt
from random import random
import numpy as np
from itertools import permutations, repeat


class CheckPoint(Widget):
    lineColor = ListProperty([])
    touched_switch = NumericProperty(0)
    
    #def __init__(self, **kwargs):
    #    super(CheckPoint, self).__init__(**kwargs)
    #    self.touched_switch = 0
        
    # When the widget is touched, it should update a coordinates list in its
    # parent class.
    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            if self.touched_switch == 0:
                self.parent.touched_coordinates.append(list(self.pos))
                self.touched_switch = 1
                self.parent.touched_cps += 1             

    
    def on_touch_move(self, touch):
        if self.collide_point(touch.x, touch.y):
            if self.touched_switch == 0:
                self.parent.touched_coordinates.append(list(self.pos))
                self.touched_switch = 1
                self.parent.touched_cps += 1  

 
class StartFinish(Widget):
    lineColor = ListProperty([])
    touched_switch = NumericProperty(0)
    
    #def __init__(self, **kwargs):
    #    super(StartFinish, self).__init__(**kwargs)
    #    self.touched_switch = 0
        
    # When the widget is touched, it should update a coordinates list in its
    # parent class.
    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            if self.touched_switch == 0:
                self.parent.touched_coordinates.append(list(self.pos))
                self.touched_switch = 1
                self.parent.touched_strt_fnsh = 1
            if self.touched_switch == 1 and self.parent.touched_cps == self.parent.total_cps - 1:
                self.parent.touched_coordinates.append(list(self.pos))
                self.parent.plot_touched_coordinates()                

    
    def on_touch_move(self, touch):
        if self.collide_point(touch.x, touch.y):
            if self.touched_switch == 0:
                self.parent.touched_coordinates.append(list(self.pos))
                self.touched_switch = 1
                self.parent.touched_strt_fnsh = 1
            if self.touched_switch == 1 and self.parent.touched_cps == self.parent.total_cps - 1:
                self.parent.touched_coordinates.append(list(self.pos))
                self.parent.plot_touched_coordinates() 
    
 
class MainLayout(BoxLayout):
    pass       
        

class GameTimer(Label):
    strt = NumericProperty(0.1)
    
    def start(self):
        Animation.cancel_all(self)  # stop any current animations
        self.anim = Animation(strt=3600, duration=3600)
        self.anim.start(self)
 
    def on_strt(self, instance, value):
        self.text = self.dt_to_string(self.strt)

    def dt_to_string(self, time_in_seconds):
        time_string = str(dt.time(minute= int(time_in_seconds // 1 // 60 % 60), 
                                second= int(time_in_seconds // 1 % 60), 
                                microsecond= int(time_in_seconds % 1 * 1000000))\
                                    .isoformat(timespec = 'milliseconds'))[3:10]
        return time_string
    

class oMap(FloatLayout):
    strt = NumericProperty()
    cp_coordinates = ListProperty([])
    touched_coordinates = ListProperty([])
    cp_size = ListProperty([])
    shortest_route_inst = ObjectProperty(InstructionGroup())
    touched_route_inst = ObjectProperty(InstructionGroup())
    
    def __init__(self, total_cps = 7, difficulty = 3, **kwargs):
        super(oMap, self).__init__(**kwargs)
        self.total_cps = total_cps
        self.instructions = "Add ScoreO Instructions here."
        self.touched_strt_fnsh = 0
        self.touched_cps = 0
        self.difficulty = difficulty
        

    def count_down(self):
        Animation.cancel_all(self)
        self.anim = Animation(strt=0, duration=4)
        self.anim.start(self)
        
        
    def on_strt(self, instance, value):
        self.oMapLabel.font_size = self.height * 0.4
        
        if int(self.strt) == 0:
            Animation.cancel_all(self)
            self.plot_CPs()
            self.gameTmr.start()
        else: self.oMapLabel.text = str(int(self.strt))
        
        
    def generate_coordinates(self):
        return [int(random() * (self.width - self.cp_size[0]) + self.pos[0]), 
                int(random() * (self.height - self.cp_size[0]) + self.pos[1])]
        
        
    def create_coordinate_list(self):
        cp_coordinates = []
        
        # Start generating all the CPs
        for cp in range(self.total_cps):
            new_coordinates = self.generate_coordinates()
    
        # If CP coordinates overlap, generate new coordinates
            if cp > 0:
                while self.check_cp_overlap(cp_coordinates, new_coordinates):
                    new_coordinates = self.generate_coordinates()
                    
            cp_coordinates += [new_coordinates]
        
        self.cp_coordinates = cp_coordinates
        
        self.shortest_route()
    
    
    def check_cp_overlap(self, cp_coordinates, new_coordinates):
        # All CPs are square widgets so we only need 1 cp_size value
        for cp in cp_coordinates:
            if not (cp[0] > new_coordinates[0] + self.cp_size[0] 
                    or new_coordinates[0] > cp[0] + self.cp_size[0]
                    or cp[1] > new_coordinates[1] + self.cp_size [0]
                    or new_coordinates[1] > cp[1] + self.cp_size[0]):
                return True
            
        return False
    
    def shortest_route(self):
        
        # Find all the permutations of the coordinates with the first
        # coordinate removed.
        lst_comb = np.array(list(map(list,
                                     permutations(self.cp_coordinates[1:], 
                                                  len(self.cp_coordinates[1:])))))
        
        # Convert the first coordinate to match the format of the permutations.
        strt_fnsh = np.array(list(repeat(([self.cp_coordinates[0]]), 
                                         len(lst_comb))), 
                             ndmin=3)
        
        # Add the first coordinates to the beginning and end of all permutations
        # since the user has to start and end at the same spot.
        add_strt = np.append(strt_fnsh, lst_comb, axis=1)
        
        add_fnsh = np.append(add_strt, strt_fnsh, axis=1)
        
        # Find the permutation with the shortest distance.
        self.route_distances = np.sum(np.sqrt(np.sum(np.diff(add_fnsh, 1, 
                                                        axis=1)**2, 
                                                axis=-1)), 
                                 axis=1)
        
        self.cp_coordinates = add_fnsh[np.argmin(self.route_distances)].tolist()
        
        self.route_distances.sort()
        
        if self.route_distances[0]/self.route_distances[self.difficulty * 2] < .995:
            self.create_coordinate_list()
            
    
    def plot_CPs(self):
        
        self.oMapLabel.text = ""
        
        self.cp_size = (self.size[0] * 0.05, self.size[0] * 0.05)
        
        self.create_coordinate_list()
        
        self.add_widget(StartFinish(pos = self.cp_coordinates[0], 
                                    size = self.cp_size))
        
        for cp in range(self.total_cps):
            if cp > 0:
                self.add_widget(CheckPoint(pos = self.cp_coordinates[cp], 
                                           size = self.cp_size))
                       
        self.shrtDistLabel.text = "{0:,.1f}".format(float(np.min(self.route_distances)))
                
        
    def clear_oMap(self):
        self.touched_strt_fnsh = 0
        self.touched_cps = 0
        self.cp_coordinates = []
        self.touched_coordinates = []
        self.touched_route_inst.clear()
        self.shortest_route_inst.clear()
        for child in self.children[:]:
            if type(child) in (CheckPoint, StartFinish):
                self.remove_widget(child)
                
                
    def plot_touched_coordinates(self):
        Animation.cancel_all(self.gameTmr)
        updated_coordinates = np.array(self.touched_coordinates) + self.cp_size[0] / 2        
        shortest_coordinates = np.array(self.cp_coordinates) + self.cp_size[0] / 2
        
        route_distances = np.sum(np.sqrt(np.sum(np.diff([updated_coordinates],
                                                        1, 
                                                        axis=1)**2, 
                                                axis=-1)), 
                                 axis=1)
                    
        self.yourDistLabel.text = "{0:,.1f}".format(float(route_distances))
        self.touched_route_inst.add(Color(r=1, g=1, b=1, a=1.0))
        self.touched_route_inst.add(Line(points=(tuple(tuple(i) for i in updated_coordinates)), 
                                       width=1.2,
                                       cap='round',
                                       joint='round'))
        self.shortest_route_inst.add(Color(r=(113/255), g=(197/255), b=(232/255), a=0.01))
        self.shortest_route_inst.add(Line(points=(tuple(tuple(i) for i in shortest_coordinates)), 
                                          width=5,
                                          cap='round',
                                          joint='round'))  
        self.canvas.add(self.touched_route_inst)
        self.canvas.add(self.shortest_route_inst)


class NewGameButton(Button):

    def on_release(self):

        # Reset the oMap Countdown and Labels
        self.oMp.strt = 3.9999999
        self.shrtDistLabel.text = 'Shortest Distance'
        self.yourDistLabel.text = 'Your Distance'
        
        # Clear any CP widgets on the oMap space
        self.oMp.clear_oMap()
        
        # Stop the GameTimer animation and reset the text
        Animation.cancel_all(self.gameTmr)
        self.gameTmr.text = '00:00.0'
        
        self.oMp.count_down()

class ScoreOApp(App):

    def build(self):
        self.title = 'Score-O'
        myLayout = MainLayout()
        return myLayout
        

if __name__ == '__main__':
    ScoreOApp().run()