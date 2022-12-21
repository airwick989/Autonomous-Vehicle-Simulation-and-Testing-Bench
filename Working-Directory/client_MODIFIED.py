#!/usr/bin/env python

# Copyright (c) 2019 Intel Labs
#
# This work is licensed under the terms of the MIT license.
# For a copy, see <https://opensource.org/licenses/MIT>.

# Allows controlling a vehicle with a keyboard. For a simpler and more
# documented example, please take a look at tutorial.py.

"""
Welcome to CARLA manual control with steering wheel Logitech G29.

To drive start by preshing the brake pedal.
Change your wheel_config.ini according to your steering wheel.

To find out the values of your steering wheel use jstest-gtk in Ubuntu.

"""

from __future__ import print_function
from dataclasses import asdict


# ==============================================================================
# -- find carla module ---------------------------------------------------------
# ==============================================================================


import glob
import os
from turtle import hideturtle
import cv2
import sys
import csv
import signal
import subprocess

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass


# ==============================================================================
# -- imports -------------------------------------------------------------------
# ==============================================================================


import carla

from carla import ColorConverter as cc

import argparse
import collections
import datetime
import logging
import math
import random
import re
import weakref

# Cluster Imports
import time
import serial
import struct

if sys.version_info >= (3, 0):

    from configparser import ConfigParser

else:

    from ConfigParser import RawConfigParser as ConfigParser

try:
    import pygame
    from pygame.locals import KMOD_CTRL
    from pygame.locals import KMOD_SHIFT
    from pygame.locals import K_0
    from pygame.locals import K_9
    from pygame.locals import K_BACKQUOTE
    from pygame.locals import K_BACKSPACE
    from pygame.locals import K_COMMA
    from pygame.locals import K_DOWN
    from pygame.locals import K_ESCAPE
    from pygame.locals import K_F1
    from pygame.locals import K_LEFT
    from pygame.locals import K_PERIOD
    from pygame.locals import K_RIGHT
    from pygame.locals import K_SLASH
    from pygame.locals import K_SPACE
    from pygame.locals import K_TAB
    from pygame.locals import K_UP
    from pygame.locals import K_a
    from pygame.locals import K_c
    from pygame.locals import K_d
    from pygame.locals import K_h
    from pygame.locals import K_m
    from pygame.locals import K_p
    from pygame.locals import K_q
    from pygame.locals import K_r
    from pygame.locals import K_s
    from pygame.locals import K_w
except ImportError:
    raise RuntimeError('cannot import pygame, make sure pygame package is installed')

try:
    import numpy as np
except ImportError:
    raise RuntimeError('cannot import numpy, make sure numpy package is installed')

# For collision mitigation algo with LiDAR
from ploygon_calc import Cuboid             #  ploygon_calc.py
from ploygon_calc import XYZPoint           #  ploygon_calc.py


# Here -y axis the front of the car
p1 = XYZPoint(-4,-9,1.5)
p2 = XYZPoint(4,-9,1.5)
p3 = XYZPoint(4,-4,1.5)
p4 = XYZPoint(-4,-4,1.5)
p5 = XYZPoint(-4,-9,-2)
p6 = XYZPoint(4,-9,-2)
p7 = XYZPoint(4,-4,-2)
p8 = XYZPoint(-4,-4,-2)
# This is the cuboid that sits infront of the car, this same priciple
# can be applied to place unsafe zone's any where around the car.
car_unsafe_zone = Cuboid(p1, p2, p3, p4, p5, p6, p7, p8)

# ==============================================================================
# -- Global functions ----------------------------------------------------------
# ==============================================================================

ser = serial.Serial('COM3', 9600)
ser2 = serial.Serial('COM4', 9600)

status = "false"
def sound_alarm(alarm):
    global status
	# play an alarm sound
	#playsound.playsound(path)
    if alarm == "true":
        if status == "false":
            subprocess.call("adb shell am start -n com.example.alertapp/.MainActivity",shell=True)
            status = "true"
    else:
        if status == "true":
            subprocess.call("adb shell am start -n com.microntek.navisettings/.MainActivity",shell=True)
            status = "false"

def find_weather_presets():
    rgx = re.compile('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)')
    name = lambda x: ' '.join(m.group(0) for m in rgx.finditer(x))
    presets = [x for x in dir(carla.WeatherParameters) if re.match('[A-Z].+', x)]
    return [(getattr(carla.WeatherParameters, x), name(x)) for x in presets]


def get_actor_display_name(actor, truncate=250):
    name = ' '.join(actor.type_id.replace('_', '.').title().split('.')[1:])
    return (name[:truncate - 1] + u'\u2026') if len(name) > truncate else name

def get_speed():
    global delay_counter
    last_indicator = 0
    last_speed = 0
    temp = round(speed/10)
    if(temp != last_speed):
        last_speed = temp
        ser.write(struct.pack('>i', temp))
        #print(temp)
        
    if(indicator != 0 and delay_counter > 60):
        if(last_indicator != indicator):
            ser2.write(str.encode(str(indicator)))
            last_indicator = indicator
        delay_counter = 0
    #print(delay_counter)
    delay_counter = delay_counter + 1
    return speed if not reverse else speed * -1
# ==============================================================================
# -- World ---------------------------------------------------------------------
# ==============================================================================
steer = 0
auto = 0
speed = 0
locationPath = 0
indicator = 0
delay_counter = 0
reverse = 0
bkup = 0
drive = 0
drive_ctr = 201
bkup_cam = 1
nav = 0
array3 = None
attentionFlag = 0
park = 0

with open('C:\\Users\\RTEMSOFT\\Desktop\\carla-capstone\\python\\client\\location.csv', newline='') as loclist:
    loc = list(csv.reader(loclist))

class World(object):
    def __init__(self, carla_world, hud, actor_filter):
        self.world = carla_world
        self.hud = hud
        self.player = None
        self.collision_sensor = None
        self.lane_invasion_sensor = None
        self.camera_manager = None
        self._weather_presets = find_weather_presets()
        self._weather_index = 0
        self._actor_filter = actor_filter
        self.restart()
        self.world.on_tick(hud.on_world_tick)

    def restart(self):
        # Keep same camera config if the camera manager exists.
        cam_index = self.camera_manager.index if self.camera_manager is not None else 0
        cam_pos_index = self.camera_manager.transform_index if self.camera_manager is not None else 0
        # Get a random blueprint.
        blueprint = random.choice(self.world.get_blueprint_library().filter(self._actor_filter))
        blueprint.set_attribute('role_name', 'hero')
        if blueprint.has_attribute('color'):
            color = random.choice(blueprint.get_attribute('color').recommended_values)
            blueprint.set_attribute('color', color)
        # Spawn the player.
        if self.player is not None:
            spawn_point = self.player.get_transform()
            spawn_point.location.z += 2.0
            spawn_point.rotation.roll = 0.0
            spawn_point.rotation.pitch = 0.0
            self.destroy()
            self.player = self.world.try_spawn_actor(blueprint, spawn_point)
        while self.player is None:
            spawn_points = self.world.get_map().get_spawn_points()
            spawn_point = random.choice(spawn_points) if spawn_points else carla.Transform()
            self.player = self.world.try_spawn_actor(blueprint, spawn_point)
        # Set up the sensors.
        self.collision_sensor = CollisionSensor(self.player, self.hud)
        self.lane_invasion_sensor = LaneInvasionSensor(self.player, self.hud)
        self.camera_manager = CameraManager(self.player, self.hud)
        self.camera_manager.transform_index = cam_pos_index
        self.camera_manager.set_sensor(cam_index, notify=False)
        actor_type = get_actor_display_name(self.player)
        self.hud.notification(actor_type)

    def next_weather(self, reverse=False):
        self._weather_index += -1 if reverse else 1
        self._weather_index %= len(self._weather_presets)
        preset = self._weather_presets[self._weather_index]
        self.hud.notification('Weather: %s' % preset[1])
        self.player.get_world().set_weather(preset[0])

    def tick(self, clock):
        self.hud.tick(self, clock)

    def render(self, display):
        self.camera_manager.render(display)
        #self.hud.render(display)

    def destroy(self):
        actors = [
            self.camera_manager.sensor,
            self.camera_manager.sensor_bkup,
            self.collision_sensor.sensor,
            self.lane_invasion_sensor.sensor,
            self.player]
        for actor in actors:
            if actor is not None:
                actor.destroy()


# ==============================================================================
# -- DualControl -----------------------------------------------------------
# ==============================================================================


class DualControl(object):
    def __init__(self, world, start_in_autopilot):
        self._autopilot_enabled = start_in_autopilot
        if isinstance(world.player, carla.Vehicle):
            self._control = carla.VehicleControl()
            world.player.set_autopilot(self._autopilot_enabled)
        elif isinstance(world.player, carla.Walker):
            self._control = carla.WalkerControl()
            self._autopilot_enabled = False
            self._rotation = world.player.get_transform().rotation
        else:
            raise NotImplementedError("Actor type not supported")
        self._steer_cache = 0.0
        world.hud.notification("Press 'H' or '?' for help.", seconds=4.0)

        # initialize steering wheel
        pygame.joystick.init()

        joystick_count = pygame.joystick.get_count()
        # if joystick_count > 1:
        #     raise ValueError("Please Connect Just One Joystick")

        self._joystick = pygame.joystick.Joystick(0)
        self._joystick.init()

        self._parser = ConfigParser()
        self._parser.read('wheel_config.ini')
        self._steer_idx = 0
        self._throttle_idx = 2
        self._brake_idx = 1
        self._reverse_idx = 5
        self._handbrake_idx = 4
        self._joystick1 = pygame.joystick.Joystick(1)
        self._joystick1.init()

    def parse_events(self, world, clock, testingFlag):
        global auto
        global bkup_cam
        global park
        global reverse
        #(REZWANA) CODE FOR TEST CASES, SENDS A CLICK MOUSE EVENT SO THAT THE CLIENT IS IN FOCUS
        if testingFlag >= 1:
            post_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button = 2, pos = (5, 5))
            pygame.event.post(post_event)
            event = pygame.event.poll()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
            #(REZWANA) pygame recognizes steering wheel kit and gear shifter as "joys or joystick"
            #we are checking if the current event is from a joystick
            elif event.type == pygame.JOYBUTTONDOWN:
                print(event.button)
                #(REZWANA) since there are 2 joy sticks, the indices for these are 0 and 1
                #index 1 = gear shifter
                #index 2 = steering wheel kit

                #(REZWANA) this if statement checks, if the input is from the gear shifter
                if event.joy == 1:
                    #if its a 0 input, put in park, if 1 put in drive etc.
                    if event.button == 0:
                        print(park)
                        park = 1
                    elif event.button == 1:
                        park=0
                        if (reverse==1):
                            reverse=0
                            self._control.gear = 1
                    elif event.button==2:
                        hideturtle
                    elif event.button==7:
                        reverse = 1
                        self._control.gear = -1
                        park = 0
                #(REZWANA) if the input is a joystick, but it is NOT from the gear shifter, it is from the steering wheel kit
                #the rest of these if statemenst are parsing inputs from the steering wheel kit
                #all the different buttons etc.
                else:
                    global indicator
                    if event.button == 4:
                        world.camera_manager.toggle_camera()
                    elif event.button == 0:
                        if(indicator == 2):
                            indicator = 0
                        else:
                            indicator = 2
                    elif event.button == 2:
                        if(indicator == 1):
                            indicator = 0
                        else:
                            indicator = 1
                    elif event.button == 10:
                        global attentionFlag
                        if (attentionFlag == 0):
                            file1 = open("myfile.txt","r")
                            pid = int(file1.read())
                            file1.close()
                            os.kill(pid, signal.SIGTERM)
                            attentionFlag = 1
                        else:
                            attentionFlag = 0
                            subprocess.Popen(['python','capture.py'])
                    elif event.button == 5:
                        if event.joy == 0:
                            
                            if(reverse == 0):
                                subprocess.call("adb shell am start -n com.microntek.avin/.MainActivity",shell=True)
                                reverse = 1
                                self._control.gear = -1
                            else:
                                subprocess.call("adb shell am start -n com.microntek.navisettings/.MainActivity",shell=True)
                                reverse = 0
                                self._control.gear = 1
                    elif event.button == 6:
                        world.camera_manager.toggle_camera()
                    elif event.button == 12:
                        world.destroy()
                        pygame.quit()
                    elif event.button == 7:
                        if(auto == 1):
                            print("Disable Lane Assist")
                            auto = 0
                        else:
                            print("Enable Lane Assist")
                            auto = 1
                    elif event.button == self._reverse_idx:
                        self._control.gear = 1 if self._control.reverse else -1
                    elif event.button == 3:
                        if(indicator == 3):
                            indicator = 0
                        else:
                            indicator = 3
                    elif event.button == 1:
                        if bkup_cam == 0:
                            bkup_cam = 1
                        else:
                            bkup_cam = 0
                        world.restart()

            elif event.type == pygame.KEYUP:
                if self._is_quit_shortcut(event.key):
                    return True
                elif event.key == K_BACKSPACE:
                    world.restart()
                elif event.key == K_F1:
                    world.hud.toggle_info()
                elif event.key == K_h or (event.key == K_SLASH and pygame.key.get_mods() & KMOD_SHIFT):
                    world.hud.help.toggle()
                elif event.key == K_TAB:
                    world.camera_manager.toggle_camera()
                elif event.key == K_c and pygame.key.get_mods() & KMOD_SHIFT:
                    world.next_weather(reverse=True)
                elif event.key == K_c:
                    world.next_weather()
                elif event.key == K_BACKQUOTE:
                    world.camera_manager.next_sensor()
                elif event.key > K_0 and event.key <= K_9:
                    world.camera_manager.set_sensor(event.key - 1 - K_0)

                if isinstance(self._control, carla.VehicleControl):
                    if event.key == K_q:
                        self._control.gear = 1 if self._control.reverse else -1
                    elif event.key == K_m:
                        self._control.manual_gear_shift = not self._control.manual_gear_shift
                        self._control.gear = world.player.get_control().gear
                        world.hud.notification('%s Transmission' %
                                               ('Manual' if self._control.manual_gear_shift else 'Automatic'))
                    elif self._control.manual_gear_shift and event.key == K_COMMA:
                        self._control.gear = max(-1, self._control.gear - 1)
                    elif self._control.manual_gear_shift and event.key == K_PERIOD:
                        self._control.gear = self._control.gear + 1
                    elif event.key == K_p:
                        if(auto == 1):
                            print("Disable Lane Assist")
                            auto = 0
                        else:
                            print("Enable Lane Assist")
                            auto = 1
        if not self._autopilot_enabled:
            if isinstance(self._control, carla.VehicleControl):
                self._parse_vehicle_keys(pygame.key.get_pressed(), clock.get_time())
                self._parse_vehicle_wheel(testingFlag)
                self._control.reverse = self._control.gear < 0
            elif isinstance(self._control, carla.WalkerControl):
                self._parse_walker_keys(pygame.key.get_pressed(), clock.get_time())
            world.player.apply_control(self._control)
        
        #(REZWANA) These if statements are for specific test cases
        #when this client is run through our test cases, we pass a testing flag variable
        #the value of this flag is based on what test is running
        #for example if the testing flag is 1 we are testing acceleration
        if testingFlag==3:
            reverse=1
            self._control.gear = -1
        if testingFlag == 1:
            self._control.gear = 1
            reverse=0
        if testingFlag==4:
            self._control.gear=1
            park=1

    #(REZWANA) These next 2 functions are calculating the wheel axis turn and the throttle/brake
    #we do not exactly know how these functions are working, but we do know this is where it calculates
    #the throttle/brake and wheel turning
    def _parse_vehicle_keys(self, keys, milliseconds):
        self._control.throttle = 1.0 if keys[K_UP] or keys[K_w] else 0.0
        steer_increment = 5e-4 * milliseconds
        if keys[K_LEFT] or keys[K_a]:
            self._steer_cache -= steer_increment
        elif keys[K_RIGHT] or keys[K_d]:
            self._steer_cache += steer_increment
        else:
            self._steer_cache = 0.0
        self._steer_cache = min(0.7, max(-0.7, self._steer_cache))
        self._control.steer = round(self._steer_cache, 1)
        self._control.brake = 1.0 if keys[K_DOWN] or keys[K_s] else 0.0
        self._control.hand_brake = keys[K_SPACE]

    def _parse_vehicle_wheel(self, testingFlag):
        global locationPath
        global park
        numAxes = self._joystick.get_numaxes()
        jsInputs = [float(self._joystick.get_axis(i)) for i in range(numAxes)]
        jsButtons = [float(self._joystick.get_button(i)) for i in
                     range(self._joystick.get_numbuttons())]

        # Custom function to map range of inputs [1, -1] to outputs [0, 1] i.e 1 from inputs means nothing is pressed
        # For the steering, it seems fine as it is
        
        K1 = 0.35  # 0.55
        steerCmd = K1 * math.tan(1.1 * jsInputs[self._steer_idx])

        K2 = 1.4  # 1.6
        throttleCmd = K2 + (2.05 * math.log10(
            -0.7 * jsInputs[self._throttle_idx] + 1.4) - 1.2) / 0.92
        #print(throttleCmd)
        if throttleCmd <= 0:
            throttleCmd = 0
        else:
            #global drive
            #global drive_ctr
            #drive_ctr +=1
            
            #print(drive_ctr)
            #print(drive)
            #if(drive_ctr > 600):
            #    drive += 0.2
            #    drive_ctr = 0
            global nav
            if((throttleCmd > 0.8)):
                if nav > 200:
                    locationPath += 10
                    subprocess.call("adb shell am startservice -a com.lexa.fakegps.START -e lat " + str(loc[locationPath][0])  + " -e long " +  str(loc[locationPath][1]) ,shell=True)
                    nav = 0
                nav += 1
            #(REZWANA) we have a global variable park that is changed with the gear shifter
            #this will only let the car accelerate if the car is not in park
            throttleCmd = 1 if not park else 0
            
            
            
        brakeCmd = 1.6 + (2.05 * math.log10(
            -0.7 * jsInputs[self._brake_idx] + 1.4) - 1.2) / 0.92
        if brakeCmd <= 0:
            brakeCmd = 0
        elif brakeCmd > 1:
            brakeCmd = 1
        #(REZWANA) These if statements are again for our test cases
        #based on what testing flag is passed in, different things are happening within carla
        #for example testing flag 1 will set the car to accelerate, turn off the brakes and take the car out of park
        if testingFlag == 1:
            throttleCmd = 1
            brakeCmd=0
            park = 0
        elif testingFlag == 2:
            throttleCmd = 1
            brakeCmd = 1
            park = 0
        elif testingFlag ==3:
            throttleCmd=1
            brakeCmd=0
            park=0
        elif testingFlag==4:
            throttleCmd = 1 if not park else 0
            brakeCmd=0
            park=1

        self._control.steer = steerCmd
        self._control.brake = brakeCmd
        self._control.throttle = throttleCmd

        self._control.hand_brake = bool(jsButtons[self._handbrake_idx])

    def _parse_walker_keys(self, keys, milliseconds):
        self._control.speed = 0.0
        if keys[K_DOWN] or keys[K_s]:
            self._control.speed = 0.0
        if keys[K_LEFT] or keys[K_a]:
            self._control.speed = .01
            self._rotation.yaw -= 0.08 * milliseconds
        if keys[K_RIGHT] or keys[K_d]:
            self._control.speed = .01
            self._rotation.yaw += 0.08 * milliseconds
        if (keys[K_UP] or keys[K_w]):
            self._control.speed = 5.556 if pygame.key.get_mods() & KMOD_SHIFT else 2.778
        self._control.jump = keys[K_SPACE]
        self._rotation.yaw = round(self._rotation.yaw, 1)
        self._control.direction = self._rotation.get_forward_vector()

    @staticmethod
    def _is_quit_shortcut(key):
        return (key == K_ESCAPE) or (key == K_q and pygame.key.get_mods() & KMOD_CTRL)


# ==============================================================================
# -- HUD -----------------------------------------------------------------------
# ==============================================================================


class HUD(object):
    def __init__(self, width, height):
        self.dim = (width, height)
        font = pygame.font.Font(pygame.font.get_default_font(), 20)
        fonts = [x for x in pygame.font.get_fonts() if 'mono' in x]
        default_font = 'ubuntumono'
        mono = default_font if default_font in fonts else fonts[0]
        mono = pygame.font.match_font(mono)
        self._font_mono = pygame.font.Font(mono, 14)
        self._notifications = FadingText(font, (width, 40), (0, height - 40))
        self.help = HelpText(pygame.font.Font(mono, 24), width, height)
        self.server_fps = 0
        self.frame_number = 0
        self.simulation_time = 0
        self._show_info = True
        self._info_text = []
        self._server_clock = pygame.time.Clock()

    def on_world_tick(self, timestamp):
        self._server_clock.tick()
        self.server_fps = self._server_clock.get_fps()
        self.frame_number = timestamp.frame_count
        self.simulation_time = timestamp.elapsed_seconds

    def tick(self, world, clock):
        self._notifications.tick(world, clock)
        if not self._show_info:
            return
        t = world.player.get_transform()
        v = world.player.get_velocity()
        c = world.player.get_control()
        heading = 'N' if abs(t.rotation.yaw) < 89.5 else ''
        heading += 'S' if abs(t.rotation.yaw) > 90.5 else ''
        heading += 'E' if 179.5 > t.rotation.yaw > 0.5 else ''
        heading += 'W' if -0.5 > t.rotation.yaw > -179.5 else ''
        colhist = world.collision_sensor.get_collision_history()
        collision = [colhist[x + self.frame_number - 200] for x in range(0, 200)]
        max_col = max(1.0, max(collision))
        collision = [x / max_col for x in collision]
        vehicles = world.world.get_actors().filter('vehicle.*')

        # Speed Var
        global speed
        speed = (3.6 * math.sqrt(v.x**2 + v.y**2 + v.z**2))
        get_speed()
        
        if isinstance(c, carla.VehicleControl):
            self._info_text += [
                ('Throttle:', c.throttle, 0.0, 1.0),
                ('Steer:', c.steer, -1.0, 1.0),
                ('Brake:', c.brake, 0.0, 1.0),
                ('Reverse:', c.reverse),
                ('Hand brake:', c.hand_brake),
                ('Manual:', c.manual_gear_shift),
                'Gear:        %s' % {-1: 'R', 0: 'N'}.get(c.gear, c.gear)]
        elif isinstance(c, carla.WalkerControl):
            
            self._info_text += [
                ('Speed:', c.speed, 0.0, 5.556),
                ('Jump:', c.jump)]
        self._info_text += [
            '',
            'Collision:',
            collision,
            '',
            'Number of vehicles: % 8d' % len(vehicles)]
        if len(vehicles) > 1:
            self._info_text += ['Nearby vehicles:']
            distance = lambda l: math.sqrt((l.x - t.location.x)**2 + (l.y - t.location.y)**2 + (l.z - t.location.z)**2)
            vehicles = [(distance(x.get_location()), x) for x in vehicles if x.id != world.player.id]
            for d, vehicle in sorted(vehicles):
                if d > 200.0:
                    break
                vehicle_type = get_actor_display_name(vehicle, truncate=22)
                self._info_text.append('% 4dm %s' % (d, vehicle_type))



    def toggle_info(self):
        self._show_info = not self._show_info

    def notification(self, text, seconds=2.0):
        self._notifications.set_text(text, seconds=seconds)

    def error(self, text):
        self._notifications.set_text('Error: %s' % text, (255, 0, 0))

    def render(self, display):
        if self._show_info:
            info_surface = pygame.Surface((220, self.dim[1]))
            info_surface.set_alpha(100)
            display.blit(info_surface, (0, 0))
            v_offset = 4
            bar_h_offset = 100
            bar_width = 106
            for item in self._info_text:
                if v_offset + 18 > self.dim[1]:
                    break
                if isinstance(item, list):
                    if len(item) > 1:
                        points = [(x + 8, v_offset + 8 + (1.0 - y) * 30) for x, y in enumerate(item)]
                        pygame.draw.lines(display, (255, 136, 0), False, points, 2)
                    item = None
                    v_offset += 18
                elif isinstance(item, tuple):
                    if isinstance(item[1], bool):
                        rect = pygame.Rect((bar_h_offset, v_offset + 8), (6, 6))
                        pygame.draw.rect(display, (255, 255, 255), rect, 0 if item[1] else 1)
                    else:
                        rect_border = pygame.Rect((bar_h_offset, v_offset + 8), (bar_width, 6))
                        pygame.draw.rect(display, (255, 255, 255), rect_border, 1)
                        f = (item[1] - item[2]) / (item[3] - item[2])
                        if item[2] < 0.0:
                            rect = pygame.Rect((bar_h_offset + f * (bar_width - 6), v_offset + 8), (6, 6))
                        else:
                            rect = pygame.Rect((bar_h_offset, v_offset + 8), (f * bar_width, 6))
                        pygame.draw.rect(display, (255, 255, 255), rect)
                    item = item[0]
                if item:  # At this point has to be a str.
                    surface = self._font_mono.render(item, True, (255, 255, 255))
                    display.blit(surface, (8, v_offset))
                v_offset += 18
        self._notifications.render(display)
        self.help.render(display)


# ==============================================================================
# -- FadingText ----------------------------------------------------------------
# ==============================================================================


class FadingText(object):
    def __init__(self, font, dim, pos):
        self.font = font
        self.dim = dim
        self.pos = pos
        self.seconds_left = 0
        self.surface = pygame.Surface(self.dim)

    def set_text(self, text, color=(255, 255, 255), seconds=2.0):
        text_texture = self.font.render(text, True, color)
        self.surface = pygame.Surface(self.dim)
        self.seconds_left = seconds
        self.surface.fill((0, 0, 0, 0))
        self.surface.blit(text_texture, (10, 11))

    def tick(self, _, clock):
        delta_seconds = 1e-3 * clock.get_time()
        self.seconds_left = max(0.0, self.seconds_left - delta_seconds)
        self.surface.set_alpha(500.0 * self.seconds_left)

    def render(self, display):
        display.blit(self.surface, self.pos)


# ==============================================================================
# -- HelpText ------------------------------------------------------------------
# ==============================================================================


class HelpText(object):
    def __init__(self, font, width, height):
        lines = __doc__.split('\n')
        self.font = font
        self.dim = (680, len(lines) * 22 + 12)
        self.pos = (0.5 * width - 0.5 * self.dim[0], 0.5 * height - 0.5 * self.dim[1])
        self.seconds_left = 0
        self.surface = pygame.Surface(self.dim)
        self.surface.fill((0, 0, 0, 0))
        for n, line in enumerate(lines):
            text_texture = self.font.render(line, True, (255, 255, 255))
            self.surface.blit(text_texture, (22, n * 22))
            self._render = False
        self.surface.set_alpha(220)

    def toggle(self):
        self._render = not self._render

    def render(self, display):
        if self._render:
            display.blit(self.surface, self.pos)


# ==============================================================================
# -- CollisionSensor -----------------------------------------------------------
# ==============================================================================


class CollisionSensor(object):
    def __init__(self, parent_actor, hud):
        self.sensor = None
        self.history = []
        self._parent = parent_actor
        self.hud = hud
        world = self._parent.get_world()
        bp = world.get_blueprint_library().find('sensor.other.collision')
        self.sensor = world.spawn_actor(bp, carla.Transform(), attach_to=self._parent)
       
        weak_self = weakref.ref(self)
        self.sensor.listen(lambda event: CollisionSensor._on_collision(weak_self, event))

    def get_collision_history(self):
        history = collections.defaultdict(int)
        for frame, intensity in self.history:
            history[frame] += intensity
        return history

    @staticmethod
    def _on_collision(weak_self, event):
        self = weak_self()
        if not self:
            return
        actor_type = get_actor_display_name(event.other_actor)
        self.hud.notification('Collision with %r' % actor_type)
        impulse = event.normal_impulse
        intensity = math.sqrt(impulse.x**2 + impulse.y**2 + impulse.z**2)
        self.history.append((event.frame_number, intensity))
        if len(self.history) > 4000:
            self.history.pop(0)


# ==============================================================================
# -- LaneInvasionSensor --------------------------------------------------------
# ==============================================================================


class LaneInvasionSensor(object):
    def __init__(self, parent_actor, hud):
        self.sensor = None
        self._parent = parent_actor
        self.hud = hud
        world = self._parent.get_world()
        bp = world.get_blueprint_library().find('sensor.other.lane_invasion')
        self.sensor = world.spawn_actor(bp, carla.Transform(), attach_to=self._parent)
        # We need to pass the lambda a weak reference to self to avoid circular
        # reference.
        weak_self = weakref.ref(self)
        self.sensor.listen(lambda event: LaneInvasionSensor._on_invasion(weak_self, event))

    @staticmethod
    def _on_invasion(weak_self, event):
        self = weak_self()
        if not self:
            return
        lane_types = set(x.type for x in event.crossed_lane_markings)
        text = ['%r' % str(x).split()[-1] for x in lane_types]
        #print("crossed line")
        self.hud.notification('Crossed line %s' % ' and '.join(text))

# ==============================================================================
# -- CameraManager -------------------------------------------------------------
# ==============================================================================


class CameraManager(object):
    def __init__(self, parent_actor, hud):
        self.sensor = None
        self.sensor_bkup = None
        self.surface = None
        self.cam_backup = None
        self._parent = parent_actor
        self.hud = hud
        self.recording = False
        self._camera_transforms = [
            carla.Transform(carla.Location(x=-5.5, z=2.8), carla.Rotation(pitch=-15)),
            carla.Transform(carla.Location(x=1.6, z=1.7))]
        self.transform_index = 1
        
        world = self._parent.get_world()
        bp_library = world.get_blueprint_library()
        
        self.backup_loc = carla.Transform(carla.Location(x=-5, z=1), carla.Rotation(yaw=180, pitch=-10))

        self.cam_backup = bp_library.find('sensor.camera.rgb')
        self.cam_backup.set_attribute('image_size_x', str(hud.dim[0]))
        self.cam_backup.set_attribute('image_size_y', str(hud.dim[1]))
        
        self.sensors = [
            ['sensor.camera.rgb', cc.Raw, 'Camera RGB'],
            ['sensor.lidar.ray_cast', None, 'Lidar (Ray-Cast)']]

        self.sensor_bkup = world.spawn_actor(self.cam_backup, self.backup_loc, attach_to=self._parent)
        
        
        for item in self.sensors:
            bp = bp_library.find(item[0])
            if item[0].startswith('sensor.camera'):
                bp.set_attribute('image_size_x', str(hud.dim[0]))
                bp.set_attribute('image_size_y', str(hud.dim[1]))
            elif item[0].startswith('sensor.lidar'):
                bp.set_attribute('range', '5000')
            item.append(bp)
        self.index = None

    def toggle_camera(self):
        self.transform_index = (self.transform_index + 1) % len(self._camera_transforms)
        self.sensor.set_transform(self._camera_transforms[self.transform_index])

    # TAB          : change sensor position
    # `            : next sensor
    # [1-9]        : change to sensor [1-9]
    def set_sensor(self, index, notify=True):
        index = index % len(self.sensors)
        needs_respawn = True if self.index is None \
            else self.sensors[index][0] != self.sensors[self.index][0]
        if needs_respawn:
            if self.sensor is not None:
                self.sensor.destroy()
                self.surface = None
                
            self.sensor = self._parent.get_world().spawn_actor(
                self.sensors[index][-1],
                self._camera_transforms[1],
                attach_to=self._parent)
            # We need to pass the lambda a weak reference to self to avoid
            # circular reference.
            weak_self = weakref.ref(self)
            self.sensor.listen(lambda image: CameraManager._parse_image(weak_self, image))
            global bkup_cam
            if(bkup_cam == 1):
                self.sensor_bkup.listen(lambda bkup: CameraManager.backup(weak_self, bkup)) 
            
            
        if notify:
            self.hud.notification(self.sensors[index][2])
        self.index = index

    def next_sensor(self):
        self.set_sensor(self.index + 1)

    def render(self, display):
        if self.surface is not None:
            self.surface = pygame.transform.scale(self.surface, (1920, 1080))
            display.blit(self.surface, (0, 0))

    def process_img(img):
        processed_img = cv2.Canny(img, threshold1=200, threshold2=300)
        processed_img = cv2.GaussianBlur(processed_img, (5, 5), 0)
        return processed_img
        
    def backup(weak_self, image):
        self = weak_self()

        array = np.frombuffer(image.raw_data, dtype=np.dtype("uint8"))
        array = np.reshape(array, (image.height, image.width, 4))

        array = array[:, :, :3]
        
        cv2.namedWindow("window")
        cv2.moveWindow("window", 1900, 0)
        cv2.resizeWindow("window", 1920, 1080)
        array = cv2.resize(array, dsize=(1080, 1080), interpolation=cv2.INTER_CUBIC)        
        cv2.imshow("window", array)
        
        cv2.waitKey(1)

    def region_of_interest(img):
        height = img.shape[0]
        width = img.shape[1]
        
        a1 = (int) (0.20 * width)
        a2 = (int) (0.82 * width)
        b = (int) (0.76 * height)
        
        interest = np.array([[(a1, b),(a1, height), (a2,height), (a2, b)]])
        mask = np.zeros_like(img)
        cv2.fillPoly(mask, interest, 255)
        masked_img = cv2.bitwise_and(img, mask)
        return masked_img

    def display_lines(img, lines):
    
        height = img.shape[0]
        width = img.shape[1]
        
        a1 = (int) (0.20 * width)
        a2 = (int) (0.82 * width)
        b = (int) (0.76 * height)
        
        line_image = np.zeros_like(img)
        m1 = 0.0; ## Right
        m2 = 0.0; ## Left
        length1 = 0
        length2 = 0
        m1coords = [[a2, b], [a2,height]]
        m2coords = [[a1, b], [a1,height]]
        
        # Check all the lines that is was able to detect and see which is most a road line
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line.reshape(4)
                x = (float)(x2.item() - x1.item())
                y = (float)(y2.item() - y1.item())
                if (x != 0 and y != 0):
                    m = y/x
                    if(m > m1):
                        m1 = m
                        z = (x*x)+(y*y)
                        #length = math.sqrt(z)
                        m1coords[0] = [x1, y1]
                        m1coords[1] = [x2, y2]
                    if(m < m2):
                        m2 = m
                        
                        z = (x*x)+(y*y)
                        #length = math.sqrt(z)
                        m2coords[0] = [x1, y1]
                        m2coords[1] = [x2, y2]
            cv2.line(line_image, (m1coords[0][0], m1coords[0][1]), (m1coords[1][0], m1coords[1][1]), (255, 255, 255), 10)
            cv2.line(line_image, (m2coords[0][0], m2coords[0][1]), (m2coords[1][0], m2coords[1][1]), (255, 255, 255), 10)
        return line_image, m1coords, m2coords

    @staticmethod
    def _parse_image(weak_self, image):
        self = weak_self()
        if not self:
            return
        if self.sensors[self.index][0].startswith('sensor.lidar'):
            print("lidar started")
            points = np.frombuffer(image.raw_data, dtype=np.dtype('f4'))
            points = np.reshape(points, (int(points.shape[0] / 3), 3)) # looks like [[x,y,x],[x,y,x],[x,y,x]]
            for x in np.nditer(points, flags=['external_loop'], order='F'):
                this = XYZPoint(x[0], x[1], x[2]) # Make point object out of the array
                if(get_speed() != 0):
                    if(car_unsafe_zone.point_is_within(this)):
                        # one point is in the unsafe zone, so warn and exit
                        print("Warning!!")
                        sound_alarm("true")
                        break
                else:
                    sound_alarm("false")
            lidar_data = np.array(points[:, :2])
            lidar_data *= min(self.hud.dim) / 100.0
            lidar_data += (0.5 * self.hud.dim[0], 0.5 * self.hud.dim[1])
            lidar_data = np.fabs(lidar_data)  # pylint: disable=E1111
            lidar_data = lidar_data.astype(np.int32)
            lidar_data = np.reshape(lidar_data, (-1, 2))
            lidar_img_size = (self.hud.dim[0], self.hud.dim[1], 3)
            lidar_img = np.zeros(lidar_img_size) # Return a new array of given shape and type, filled with zeros
            lidar_img[tuple(lidar_data.T)] = (255, 255, 255)
            self.surface = pygame.surfarray.make_surface(lidar_img)
        
        else:
            image.convert(self.sensors[0][1])
            
            array = np.frombuffer(image.raw_data, dtype=np.dtype("uint8"))
            array = np.reshape(array, (image.height, image.width, 4))
            
            array2 = array[:, :, :3]
            array = array2[:, :, ::-1]
            
            self.surface = pygame.surfarray.make_surface(array.swapaxes(0, 1))
            
            processed_img = CameraManager.process_img(CameraManager.region_of_interest(CameraManager.process_img(CameraManager.process_img(array2))))
            
            lines = cv2.HoughLinesP(processed_img, 2, np.pi/180, 100, np.array([]), minLineLength=100, maxLineGap=80)
            
            lined_img, m1, m2 = CameraManager.display_lines(processed_img, lines)
            
            overlayed_img = cv2.addWeighted(cv2.cvtColor(array2, cv2.COLOR_BGR2GRAY), 0.8, lined_img, 1, 1)
            
            height = image.height
            width = image.width
            
            a1 = (int) (0.20 * width)
            a2 = (int) (0.82 * width)
            b = (int) (0.76 * height)
            
            cv2.rectangle(overlayed_img,(a1,b),(a2,height),(0,255,0),3)
            pts = np.array([m1, m2], np.int32)
            pts = pts.reshape((-1,1,2))
            avgm1 = (m1[0][0] + m1[1][0])/2
            avgm2 = (m2[0][0] + m2[1][0])/2
            
            m1dif = avgm1 - (width/2)
            m2dif = (width/2) - avgm2
            global steer
            if(m1dif < 100):
                #print("Steer left!")
                steer = -0.3
                
            if(m2dif < 100):
                #print("Steer right!")
                steer = 0.3

            if ((m1dif > 200) and (m2dif > 200)):
                steer = 0
        
                cv2.polylines(overlayed_img,[pts],True,(0,255,255))
                cv2.fillPoly(overlayed_img, np.int_([pts]), (0, 255, 0))
                cv2.moveWindow("window2", 1900, 0)
                #cv2.imshow('window2', overlayed_img)
                cv2.waitKey(1)

# ==============================================================================
# -- game_loop() ---------------------------------------------------------------
# ==============================================================================

def game_loop(args, testing_Flag):
    pygame.init()
    pygame.font.init()
    world = None

    try:
        client = carla.Client(args.host, args.port)
        client.set_timeout(2.0)
        os.environ['SDL_VIDEO_CENTERED'] = '1'

        display = pygame.display.set_mode(
            (1920, 1080))

        hud = HUD(args.width, args.height)
        #(REZWANA) Here is where we change the world/environment
        #CARLA comes with default worlds (town01-town0x)
        #reading the documentation will tell you a description of the world
        #Town06 is mostly flat highways

        #Reading the documentation will also let you learn how to create custom worlds, and this is where you would load them in
        world_map = client.load_world('Town06')
        world = World(world_map, hud, args.filter)
        controller = DualControl(world, args.autopilot)

        clock = pygame.time.Clock()
        global steer
        global auto
        if testing_Flag >=1:
            for i in range(600):
                clock.tick_busy_loop(60)
                if controller.parse_events(world, clock, testing_Flag):
                    return
                world.tick(clock)
                world.render(display)
                
                if(auto == 1):
                    world.player.apply_control(carla.VehicleControl(throttle=.25, steer=steer))
                pygame.display.flip()
        else:

            while True:
                clock.tick_busy_loop(60)
                if controller.parse_events(world, clock, 0):
                    return
                world.tick(clock)
                world.render(display)
                print(get_speed())
                if(auto == 1):
                    world.player.apply_control(carla.VehicleControl(throttle=.25, steer=steer))
                pygame.display.flip()

    finally:
        if world is not None:
            world.destroy()

        pygame.quit()


# ==============================================================================
# -- main() --------------------------------------------------------------------
# ==============================================================================


def main(testingFlag):
    argparser = argparse.ArgumentParser(
        description='CARLA Manual Control Client')
    argparser.add_argument(
        '-v', '--verbose',
        action='store_true',
        dest='debug',
        help='print debug information')
    argparser.add_argument(
        '--host',
        metavar='H',
        default='127.0.0.1',
        help='IP of the host server (default: 127.0.0.1)')
    argparser.add_argument(
        '-p', '--port',
        metavar='P',
        default=2000,
        type=int,
        help='TCP port to listen to (default: 2000)')
    argparser.add_argument(
        '-a', '--autopilot',
        action='store_true',
        help='enable autopilot')
    argparser.add_argument(
        '--res',
        metavar='WIDTHxHEIGHT',
        default='858x480',
        help='window resolution (default: 1280x720)')
    argparser.add_argument(
        '--filter',
        metavar='PATTERN',
        default='vehicle.audi.*',
        help='actor filter (default: "vehicle.*")')
    args = argparser.parse_args()

    args.width, args.height = [int(x) for x in args.res.split('x')]



    #print(__doc__)

    try:

        game_loop(args,testingFlag)

    except KeyboardInterrupt:
        print('\nCancelled by user. Bye!')


if __name__ == '__main__':

    main(0)