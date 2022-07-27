
#!/usr/bin/env python

# Copyright (c) 2019 Computer Vision Center (CVC) at the Universitat Autonoma de
# Barcelona (UAB).
#
# This work is licensed under the terms of the MIT license.
# For a copy, see <https://opensource.org/licenses/MIT>.

# Allows controlling a vehicle with a keyboard. For a simpler and more
# documented example, please take a look at tutorial.py.

#RIDWAN#
#Suppressed every instance of ctrl+f : subprocess.call
#THIS FIXED ITSELF? Added offset to straighten steering, ctrl+f : steerCmd = K1
#Suppressed ctrl+f : subprocess.Popen
#Suppressed ctrl+f : self._joystick1
#Obtained speed and printed it to terminal, ctrl+f: get_speed
#point of interest at ctrl+f: print(event.button)
#
"""
Welcome to CARLA manual control.

Use ARROWS or WASD keys for control.

    W            : throttle
    S            : brake
    A/D          : steer left/right
    Q            : toggle reverse
    Space        : hand-brake
    P            : toggle autopilot
    M            : toggle manual transmission
    ,/.          : gear up/down
    CTRL + W     : toggle constant velocity mode at 60 km/h

    L            : toggle next light type
    SHIFT + L    : toggle high beam
    Z/X          : toggle right/left blinker
    I            : toggle interior light

    TAB          : change sensor position
    ` or N       : next sensor
    [1-9]        : change to sensor [1-9]
    G            : toggle radar visualization
    C            : change weather (Shift+C reverse)
    Backspace    : change vehicle

    O            : open/close all doors of vehicle
    T            : toggle vehicle's telemetry

    V            : Select next map layer (Shift+V reverse)
    B            : Load current selected map layer (Shift+B to unload)

    R            : toggle recording images to disk

    CTRL + R     : toggle recording of simulation (replacing any previous)
    CTRL + P     : start replaying last recorded simulation
    CTRL + +     : increments the start time of the replay by 1 second (+SHIFT = 10 seconds)
    CTRL + -     : decrements the start time of the replay by 1 second (+SHIFT = 10 seconds)

    F1           : toggle HUD
    H/?          : toggle help
    ESC          : quit
"""

from __future__ import print_function


# ==============================================================================
# -- find carla module ---------------------------------------------------------
# ==============================================================================

import glob
import os
from tracemalloc import start
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
import cantools
import can
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import pandas as pd

# Cluster Imports
import time
import serial
import struct

#RIDWAN import ADB functions
#import adblib

#RIDWAN import agents for autonomous driving
from agents.navigation.behavior_agent import BehaviorAgent  # pylint: disable=import-error
from agents.navigation.basic_agent import BasicAgent  # pylint: disable=import-error


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
    from pygame.locals import K_b
    from pygame.locals import K_c
    from pygame.locals import K_d
    from pygame.locals import K_g
    from pygame.locals import K_h
    from pygame.locals import K_i
    from pygame.locals import K_l
    from pygame.locals import K_m
    from pygame.locals import K_n
    from pygame.locals import K_o
    from pygame.locals import K_p
    from pygame.locals import K_q
    from pygame.locals import K_r
    from pygame.locals import K_s
    from pygame.locals import K_t
    from pygame.locals import K_v
    from pygame.locals import K_w
    from pygame.locals import K_x
    from pygame.locals import K_z
    from pygame.locals import K_MINUS
    from pygame.locals import K_EQUALS
except ImportError:
    raise RuntimeError('cannot import pygame, make sure pygame package is installed')

try:
    import numpy as np
except ImportError:
    raise RuntimeError('cannot import numpy, make sure numpy package is installed')


# ==============================================================================
# -- Global functions ----------------------------------------------------------
# ==============================================================================

#ser = serial.Serial('/dev/ttyACM0', 115200) #rpms
ser2 = serial.Serial('/dev/ttyACM1', 2000000) #speed
globalManualFlag = 0    #RIDWAN added
attackFlag = 0


def find_weather_presets():
    rgx = re.compile('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)')
    name = lambda x: ' '.join(m.group(0) for m in rgx.finditer(x))
    presets = [x for x in dir(carla.WeatherParameters) if re.match('[A-Z].+', x)]
    #print("preasets",presets)
    #print("weather parameters",carla.WeatherParameters)
    return [(getattr(carla.WeatherParameters, x), name(x)) for x in presets]


def get_actor_display_name(actor, truncate=250):
    name = ' '.join(actor.type_id.replace('_', '.').title().split('.')[1:])
    return (name[:truncate - 1] + u'\u2026') if len(name) > truncate else name

def get_actor_blueprints(world, filter, generation):
    bps = world.get_blueprint_library().filter(filter)

    if generation.lower() == "all":
        return bps

    # If the filter returns only one bp, we assume that this one needed
    # and therefore, we ignore the generation
    if len(bps) == 1:
        return bps

    try:
        int_generation = int(generation)
        # Check if generation is in available generations
        if int_generation in [1, 2]:
            bps = [x for x in bps if int(x.get_attribute('generation')) == int_generation]
            return bps
        else:
            print("   Warning! Actor Generation is not valid. No actor will be spawned.")
            return []
    except:
        print("   Warning! Actor Generation is not valid. No actor will be spawned.")
        return []


def get_speed(world, arduinotestFlag):
    global delay_counter
    last_indicator = 0
    last_speed = 0
    temp = round(speed/10)
    if(temp != last_speed):
        last_speed = temp
        #ser.write(struct.pack('>i', temp))
        #print(temp)
        
    if(indicator != 0 and delay_counter > 60):
        if(last_indicator != indicator):
            #ser2.write(str.encode(str(indicator)))
            last_indicator = indicator
        delay_counter = 0
    #print(delay_counter)
    delay_counter = delay_counter + 1


    if arduinotestFlag == 0:

        global attackFlag
        if(attackFlag == 0):
            c = world.player.get_control()
            p = world.player.get_physics_control()

            engine_rpm = p.max_rpm * c.throttle
            if c.gear > 0:
                try:
                    gear = p.forward_gears[c.gear]
                    calcGear = {-1: 'R', 0: 'N'}.get(c.gear, c.gear)
                   #print("calgear",calcGear)

                    #RPM Calculation
                    mph = int(speed) * 0.62137119223733 #convert speed from kph to mph
                    wheelRPM = mph / ( (60/63360) * math.pi * 25 )  #64 cm is 25 inches
                    engine_rpm = wheelRPM * gear.ratio * 10
                    ################
                except Exception:
                    pass
            
            #RIDWAN: This is to send the speed  and rpm to the Arduino board
            ser2.write(bytes(f"{str(int(speed))}\n", encoding='utf-8'))
            ser2.write(bytes(f"{str(int(engine_rpm))}\n", encoding='utf-8'))


            return speed if not reverse else speed * -1
    else:
        ser2.write(bytes(f"{str(-94616)}\n", encoding='utf-8'))
        ser2.write(bytes(f"{str(-94616)}\n", encoding='utf-8'))

        #Try to recieve the acknoledgment from the Arduino board, until a timeout
        timeout = time.time() + 2   #Loops for up to 2 seconds
        while True:
            if time.time() > timeout:
                break
            else:
                try:
                    data = ser2.readline()
                    return True
                except Exception:
                    pass
        
        return False



# ==============================================================================
# -- CAN -----------------------------------------------------------------------
# ==============================================================================


class CAN(object):
    def __init__(self):
        self.db = cantools.database.load_file('./honda.dbc')
        self.can_bus = can.interface.Bus('vcan0', bustype='socketcan')
        self.speed_message = self.db.get_message_by_name('WHEEL_SPEEDS')
        self.steer_message = self.db.get_message_by_name('STEERING_SENSORS')
        self.gear_message = self.db.get_message_by_name('GEARBOX')

    def send_car_speed(self, speed):
        data = self.speed_message.encode({'WHEEL_SPEED_FL': speed, 'WHEEL_SPEED_FR': speed, 'WHEEL_SPEED_RL': speed, 'WHEEL_SPEED_RR': speed})
        message = can.Message(arbitration_id=self.speed_message.frame_id, data=data)
        self.can_bus.send(message)

    def send_steering(self, steer):
        data = self.steer_message.encode({'STEER_ANGLE': steer * 500})
        message = can.Message(arbitration_id=self.steer_message.frame_id, data=data)
        self.can_bus.send(message)

    def send_gear(self, gear):
        if (gear == -1):
            data = self.gear_message.encode({'GEAR_SHIFTER': 'R', 'GEAR': 'R'})
        elif (gear == 1):
            data = self.gear_message.encode({'GEAR_SHIFTER': 1, 'GEAR': 1})
        elif (gear == 2):
            data = self.gear_message.encode({'GEAR_SHIFTER': 2, 'GEAR': 2})
        elif (gear == 3):
            data = self.gear_message.encode({'GEAR_SHIFTER': 3, 'GEAR': 3})
        elif (gear == 4):
            data = self.gear_message.encode({'GEAR_SHIFTER': 4, 'GEAR': 4})
        elif (gear == 5):
            data = self.gear_message.encode({'GEAR_SHIFTER': 5, 'GEAR': 5})
        elif (gear == 6):
            data = self.gear_message.encode({'GEAR_SHIFTER': 6, 'GEAR': 6})
        elif (gear == 7):
            data = self.gear_message.encode({'GEAR_SHIFTER': 7, 'GEAR': 7})
        else:
            data = self.gear_message.encode({'GEAR_SHIFTER': int(gear), 'GEAR': int(gear)})
        
        message = can.Message(arbitration_id=self.gear_message.frame_id, data=data)
        self.can_bus.send(message)


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
globalWeather = 'Clear Noon' #Default weather

# with open('location.csv', newline='') as loclist:
#     loc = list(csv.reader(loclist))

class World(object):
    def __init__(self, carla_world, hud, args):
        self.world = carla_world
        self.sync = args.sync
        self.actor_role_name = args.rolename
        try:
            self.map = self.world.get_map()
        except RuntimeError as error:
            print('RuntimeError: {}'.format(error))
            print('  The server could not send the OpenDRIVE (.xodr) file:')
            print('  Make sure it exists, has the same name of your town, and is correct.')
            sys.exit(1)
        self.hud = hud
        self.player = None
        self.collision_sensor = None
        self.lane_invasion_sensor = None
        self.gnss_sensor = None
        self.obstacle_sensor = None
        self.imu_sensor = None
        self.radar_sensor = None
        self.camera_manager = None
        self._weather_presets = find_weather_presets()
        self._weather_index = 0
        self._actor_filter = args.filter
        self._actor_generation = args.generation
        self._gamma = args.gamma
        self.restart()
        self.world.on_tick(hud.on_world_tick)
        self.recording_enabled = False
        self.recording_start = 0
        self.constant_velocity_enabled = False
        self.show_vehicle_telemetry = False
        self.doors_are_open = False
        self.current_map_layer = 0
        self.map_layer_names = [
            carla.MapLayer.NONE,
            carla.MapLayer.Buildings,
            carla.MapLayer.Decals,
            carla.MapLayer.Foliage,
            carla.MapLayer.Ground,
            carla.MapLayer.ParkedVehicles,
            carla.MapLayer.Particles,
            carla.MapLayer.Props,
            carla.MapLayer.StreetLights,
            carla.MapLayer.Walls,
            carla.MapLayer.All
        ]

    def restart(self):
        self.player_max_speed = 1.589
        self.player_max_speed_fast = 3.713
        # Keep same camera config if the camera manager exists.
        cam_index = self.camera_manager.index if self.camera_manager is not None else 0
        cam_pos_index = self.camera_manager.transform_index if self.camera_manager is not None else 0
        # Get a random blueprint.
        blueprint = random.choice(get_actor_blueprints(self.world, self._actor_filter, self._actor_generation))
        blueprint.set_attribute('role_name', self.actor_role_name)
        if blueprint.has_attribute('color'):
            color = random.choice(blueprint.get_attribute('color').recommended_values)
            blueprint.set_attribute('color', color)
        if blueprint.has_attribute('driver_id'):
            driver_id = random.choice(blueprint.get_attribute('driver_id').recommended_values)
            blueprint.set_attribute('driver_id', driver_id)
        if blueprint.has_attribute('is_invincible'):
            blueprint.set_attribute('is_invincible', 'true')
        # set the max speed
        if blueprint.has_attribute('speed'):
            self.player_max_speed = float(blueprint.get_attribute('speed').recommended_values[1])
            self.player_max_speed_fast = float(blueprint.get_attribute('speed').recommended_values[2])

        # Spawn the player.
        if self.player is not None:
            spawn_point = self.player.get_transform()
            spawn_point.location.z += 2.0
            spawn_point.rotation.roll = 0.0
            spawn_point.rotation.pitch = 0.0
            self.destroy()
            self.player = self.world.try_spawn_actor(blueprint, spawn_point)
            self.show_vehicle_telemetry = False
            self.modify_vehicle_physics(self.player)
        while self.player is None:
            if not self.map.get_spawn_points():
                print('There are no spawn points available in your map/town.')
                print('Please add some Vehicle Spawn Point to your UE4 scene.')
                sys.exit(1)
            spawn_points = self.map.get_spawn_points()
            spawn_point = random.choice(spawn_points) if spawn_points else carla.Transform()
            self.player = self.world.try_spawn_actor(blueprint, spawn_point)
            self.show_vehicle_telemetry = False
            self.modify_vehicle_physics(self.player)
        # Set up the sensors.
        self.collision_sensor = CollisionSensor(self.player, self.hud)
        self.lane_invasion_sensor = LaneInvasionSensor(self.player, self.hud)
        self.gnss_sensor = GnssSensor(self.player)
        self.obstacle_sensor = ObstacleSensor(self.player)
        self.imu_sensor = IMUSensor(self.player)
        self.camera_manager = CameraManager(self.player, self.hud, self._gamma)
        self.camera_manager.transform_index = cam_pos_index
        self.camera_manager.set_sensor(cam_index, notify=False)
        actor_type = get_actor_display_name(self.player)
        self.hud.notification(actor_type)

        if self.sync:
            self.world.tick()
        else:
            self.world.wait_for_tick()

    def next_weather(self, reverse=False):
        self._weather_index += -1 if reverse else 1
        self._weather_index %= len(self._weather_presets)
        preset = self._weather_presets[self._weather_index]
        self.hud.notification('Weather: %s' % preset[1])
        global globalWeather
        if preset[1] == "Default":
            globalWeather = "Clear Noon"    #Default weather is equivalent to Clear Noon
        else:
            globalWeather = preset[1]
        self.player.get_world().set_weather(preset[0])

    def next_map_layer(self, reverse=False):
        self.current_map_layer += -1 if reverse else 1
        self.current_map_layer %= len(self.map_layer_names)
        selected = self.map_layer_names[self.current_map_layer]
        self.hud.notification('LayerMap selected: %s' % selected)

    def load_map_layer(self, unload=False):
        selected = self.map_layer_names[self.current_map_layer]
        if unload:
            self.hud.notification('Unloading map layer: %s' % selected)
            self.world.unload_map_layer(selected)
        else:
            self.hud.notification('Loading map layer: %s' % selected)
            self.world.load_map_layer(selected)

    def toggle_radar(self):
        if self.radar_sensor is None:
            self.radar_sensor = RadarSensor(self.player)
        elif self.radar_sensor.sensor is not None:
            self.radar_sensor.sensor.destroy()
            self.radar_sensor = None

    def modify_vehicle_physics(self, actor):
        #If actor is not a vehicle, we cannot use the physics control
        try:
            physics_control = actor.get_physics_control()
            physics_control.use_sweep_wheel_collision = True
            actor.apply_physics_control(physics_control)
        except Exception:
            pass

    def tick(self, clock):
        self.hud.tick(self, clock)

    def render(self, display):
        self.camera_manager.render(display)
        self.hud.render(display)

    def destroy_sensors(self):
        self.camera_manager.sensor.destroy()
        self.camera_manager.sensor = None
        self.camera_manager.index = None

    def destroy(self):
        if self.radar_sensor is not None:
            self.toggle_radar()
        sensors = [
            self.camera_manager.sensor,
            self.collision_sensor.sensor,
            self.lane_invasion_sensor.sensor,
            self.gnss_sensor.sensor,
            self.obstacle_sensor.sensor,
            self.imu_sensor.sensor]
        for sensor in sensors:
            if sensor is not None:
                sensor.stop()
                sensor.destroy()
        if self.player is not None:
            self.player.destroy()


# ==============================================================================
# -- Data Logging -----------------------------------------------------------
# ==============================================================================

dfvehic = None
dfcoll = None
dflane = None
dfobs = None
recording_start_time = None

def create_dfs():
    global dfvehic
    vehicdata = {
        'Sim_time': [],
        'Rec_time': [],
        'Server_fps': [],
        'Client_fps': [],
        'Autopilot': [],
        'Speed': [],
        'Heading': [],
        'Accelerometer': [],
        'Gyroscope': [],
        'Location': [],
        'GNSS': [],
        'Height': [],
        'Throttle': [],
        'Brake': [],
        'Gear': [],
        'Steering': [],
        'Vehicle': [],
        'Weather/Time': []
    }
    dfvehic = pd.DataFrame(vehicdata)

    global dfcoll
    colldata = {
        'Sim_time': [],
        'Rec_time': [],
        'Autopilot': [],
        'Event': [],
        'Intensity': []
    }
    dfcoll = pd.DataFrame(colldata)

    global dflane
    lanedata = {
        'Sim_time': [],
        'Rec_time': [],
        'Autopilot': [],
        'Event': []
    }
    dflane = pd.DataFrame(lanedata)

    global dfobs
    obsdata = {
        'Sim_time': [],
        'Rec_time': [],
        'Autopilot': [],
        'Obstacle_Detected': [],
        'Distance_from_Obstacle': []
    }
    dfobs = pd.DataFrame(obsdata)




# ==============================================================================
# -- DualControl -----------------------------------------------------------
# ==============================================================================

handbrake_counter = 0
globalArduinoTestFlag = 0

class DualControl(object):
    def __init__(self, world, start_in_autopilot):
        self._autopilot_enabled = start_in_autopilot
        if isinstance(world.player, carla.Vehicle):
            self._control = carla.VehicleControl()
            world.player.set_autopilot(self._autopilot_enabled)
            self._lights = carla.VehicleLightState.NONE
            world.player.set_light_state(self._lights)
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

        self._joystick = pygame.joystick.Joystick(0)    #index out of range or joystick switch
        self._joystick.init()

        self._parser = ConfigParser()
        self._parser.read('wheel_config.ini')
        self._steer_idx = 0
        self._throttle_idx = 2
        self._brake_idx = 1
        self._reverse_idx = 5
        self._handbrake_idx = 0
        self._joystick1 = pygame.joystick.Joystick(1)   #index out of range or joystick switch
        self._joystick1.init()

    def parse_events(self, world, clock, testingFlag, testButton):
        global auto
        global bkup_cam
        global park
        global reverse
        global globalManualFlag
        if isinstance(self._control, carla.VehicleControl):
            current_lights = self._lights
        #(REZWANA) CODE FOR TEST CASES, SENDS A CLICK MOUSE EVENT SO THAT THE CLIENT IS IN FOCUS
        if testingFlag >= 1:
            if testingFlag >= 23 and testingFlag <= 25:
                pygame.init()
            post_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button = 2, pos = (5, 5))
            pygame.event.post(post_event)
            event = pygame.event.poll()
        for event in pygame.event.get():

            #RIDWAN added
            #Checking if we are doing a shifter test
            shortcutFlag = False
            if(testingFlag == 23):
                shortcutFlag = True
                event.joy = 0
                event.button = testButton
                self._control.manual_gear_shift = True
                self._control.gear = world.player.get_control().gear
                globalManualFlag = 1
            if testingFlag == 24 or testingFlag == 25: 
                shortcutFlag = True
                event.joy = 1
                event.button = testButton

            if event.type == pygame.QUIT:
                return True
            #(REZWANA) pygame recognizes steering wheel kit and gear shifter as "joys or joystick"
            #we are checking if the current event is from a joystick
            elif event.type == pygame.JOYBUTTONDOWN or shortcutFlag:
                #print(f"event.button = {event.button}\nevent.joy = {event.joy}\n")
                #(REZWANA) since there are 2 joy sticks, the indices for these are 0 and 1
                #index 1 = gear shifter
                #index 2 = steering wheel kit

                #(REZWANA) this if statement checks, if the input is from the gear shifter
                if event.joy == 1:  #index out of range or joystick switch
                    
                    #RIDWAN everything up to the END comment is added
                    if globalManualFlag:
                        reverse = 0
                        if event.button != 7:
                            try:
                                self._control.gear = event.button + 1
                            except Exception:
                                pass
                        else:
                            reverse = not reverse
                            self._control.gear = -1
                    #END
                    else:
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
                    #ADB_command_success = False #RIDWAN added: for testing adb commands
                    if event.button == 0:
                        if(indicator == 2):
                            indicator = 0
                        else:
                            indicator = 2
                        
                        global handbrake_counter
                        handbrake_counter += 1
                        if handbrake_counter % 2 == 1:
                            self._control.hand_brake = True
                        else:
                            self._control.hand_brake = False
                    elif event.button == 2:
                        pass
                        #ADB_command_success = adblib.play_pause()
                    elif event.button == 5:
                        #Enable Autonomous Driving
                        global global_autonomous
                        global autonomous_counter
                        global_autonomous = not global_autonomous
                        autonomous_counter = 0
                        if global_autonomous:
                            world.hud.notification("Autopilot ENABLED")
                        else:
                            world.hud.notification("Autopilot DISABLED")
                    elif event.button == self._reverse_idx:
                        self._control.gear = 1 if self._control.reverse else -1
                    elif event.button == 3:
                        if(indicator == 3):
                            indicator = 0
                        else:
                            indicator = 3

                        world.camera_manager.toggle_camera()
                    elif event.button == 1:
                        if bkup_cam == 0:
                            bkup_cam = 1
                        else:
                            bkup_cam = 0
                        world.restart()
                    # elif event.button == 12:
                    #     ADB_command_success = adblib.home()
                    # elif event.button == 7:
                    #     ADB_command_success = adblib.volume_up()
                    # elif event.button == 11:
                    #     ADB_command_success = adblib.volume_down()
                    # elif event.button == 6:
                    #     ADB_command_success = adblib.next()
                    # elif event.button == 10:
                    #     ADB_command_success = adblib.previous()
                    # elif event.button == 8:
                    #     ADB_command_success = adblib.back()
                    # elif event.button == 9:
                    #     ADB_command_success = adblib.recent_apps()
                    # elif event.button == 4:
                    #     adblib.launch_app('com.google.android.apps.maps')

                    # #RIDWAN added
                    # if testingFlag == 24:   #For testing ADB commands   
                    #     return ADB_command_success
            elif event.type == pygame.KEYUP:    #RIDWAN Keyboard controls
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
                elif event.key == K_r:  #Ridwan added data logging
                    global global_recording
                    global recording_start_time
                    global global_map
                    if (global_recording):
                        global_recording = False
                        foldername = global_map
                        dataset = 'dataset1'
                        file_index = 1
                        if not os.path.exists(f'./datasets/{foldername}'):
                            os.mkdir(f'./datasets/{foldername}')
                        while os.path.exists(f'./datasets/{foldername}/{dataset}'):
                            file_index += 1
                            dataset = f'dataset{file_index}'
                        os.mkdir(f'./datasets/{foldername}/{dataset}')
                        dfvehic.to_csv(f'./datasets/{foldername}/{dataset}/vehicle_telemetry.csv')
                        dfcoll.to_csv(f'./datasets/{foldername}/{dataset}/collision_data.csv')
                        dflane.to_csv(f'./datasets/{foldername}/{dataset}/lane_invasion_data.csv')
                        dfobs.to_csv(f'./datasets/{foldername}/{dataset}/obstacle_detection_data.csv')
                        world.hud.notification("Recording was SAVED")
                    else:
                        create_dfs()
                        recording_start_time = time.time()
                        global_recording = True
                        world.hud.notification("Recording has STARTED")
                elif event.key == K_l and pygame.key.get_mods() & KMOD_CTRL:
                        current_lights ^= carla.VehicleLightState.Special1
                elif event.key == K_l and pygame.key.get_mods() & KMOD_SHIFT:
                    current_lights ^= carla.VehicleLightState.HighBeam
                elif event.key == K_l:
                    # Use 'L' key to switch between lights:
                    # closed -> position -> low beam -> fog
                    if not self._lights & carla.VehicleLightState.Position:
                        world.hud.notification("Position lights")
                        current_lights |= carla.VehicleLightState.Position
                    else:
                        world.hud.notification("Low beam lights")
                        current_lights |= carla.VehicleLightState.LowBeam
                    if self._lights & carla.VehicleLightState.LowBeam:
                        world.hud.notification("Fog lights")
                        current_lights |= carla.VehicleLightState.Fog
                    if self._lights & carla.VehicleLightState.Fog:
                        world.hud.notification("Lights off")
                        current_lights ^= carla.VehicleLightState.Position
                        current_lights ^= carla.VehicleLightState.LowBeam
                        current_lights ^= carla.VehicleLightState.Fog
                elif event.key == K_i:
                    current_lights ^= carla.VehicleLightState.Interior
                elif event.key == K_z:
                    current_lights ^= carla.VehicleLightState.LeftBlinker
                elif event.key == K_x:
                    current_lights ^= carla.VehicleLightState.RightBlinker

                if isinstance(self._control, carla.VehicleControl):
                    if event.key == K_q:
                        self._control.gear = 1 if self._control.reverse else -1
                    elif event.key == K_m:
                        self._control.manual_gear_shift = not self._control.manual_gear_shift
                        self._control.gear = world.player.get_control().gear
                        world.hud.notification('%s Transmission' %
                                               ('Manual' if self._control.manual_gear_shift else 'Automatic'))
                        globalManualFlag = not globalManualFlag #RIDWAN added
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
        
        if not(testingFlag >= 23 and testingFlag <= 25):
            if not self._autopilot_enabled:
                if isinstance(self._control, carla.VehicleControl):
                    self._parse_vehicle_keys(pygame.key.get_pressed(), clock.get_time())
                    self._parse_vehicle_wheel(testingFlag)
                    self._control.reverse = self._control.gear < 0

                    # Set automatic control-related vehicle lights
                    if self._control.brake:
                        current_lights |= carla.VehicleLightState.Brake
                    else: # Remove the Brake flag
                        current_lights &= ~carla.VehicleLightState.Brake
                    if self._control.reverse:
                        current_lights |= carla.VehicleLightState.Reverse
                    else: # Remove the Reverse flag
                        current_lights &= ~carla.VehicleLightState.Reverse
                    if current_lights != self._lights: # Change the light state only if necessary
                        self._lights = current_lights
                        world.player.set_light_state(carla.VehicleLightState(self._lights))
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

        #RIDWAN added
        if testingFlag==21:  #Test sending data on arduino
            global globalArduinoTestFlag
            globalArduinoTestFlag = 1
        if testingFlag==22:  #Test handbrake
            self._control.hand_brake = True
        if testingFlag==23:  #Test shifter
            return self._control.gear

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
        #self._control.hand_brake = keys[K_SPACE]

    def _parse_vehicle_wheel(self, testingFlag):
        global locationPath
        global park
        numAxes = self._joystick.get_numaxes()
        jsInputs = [float(self._joystick.get_axis(i)) for i in range(numAxes)]
        jsButtons = [float(self._joystick.get_button(i)) for i in
                     range(self._joystick.get_numbuttons())]

        # Custom function to map range of inputs [1, -1] to outputs [0, 1] i.e 1 from inputs means nothing is pressed
        # For the steering, it seems fine as it is
        
        #steering_offset= 0.33331298828125
        K1 = 0.35  # 0.55
        steerCmd = K1 * math.tan(1.1 * (jsInputs[self._steer_idx]))
        #print(f"Axis?: {jsInputs[self._steer_idx] - 0.33331298828125}")

        K2 = 1.4  # 1.6
        try: #index out of range
            throttleCmd = (K2 + (2.05 * math.log10(-0.7 * jsInputs[self._throttle_idx] + 1.4) - 1.2) / 0.92) + 0.2494802700793417   #RIDWAN added throttle correction factor
        except Exception:
            throttleCmd = 0
        #print(f"throttleCmd: {throttleCmd}")
        if throttleCmd <= 0:
            throttleCmd = 0
        elif throttleCmd > 1:
            throttleCmd = 1
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
                    #subprocess.call("adb shell am startservice -a com.lexa.fakegps.START -e lat " + str(loc[locationPath][0])  + " -e long " +  str(loc[locationPath][1]) ,shell=True)
                    nav = 0
                nav += 1
            #(REZWANA) we have a global variable park that is changed with the gear shifter
            #this will only let the car accelerate if the car is not in park
            #throttleCmd = 1 if not park else 0 #This was causing the throttle issue
            
            
            
        brakeCmd = 1.6 + (2.05 * math.log10(
            -0.7 * jsInputs[self._brake_idx] + 1.4) - 1.2) / 0.92
        if brakeCmd <= 0:
            brakeCmd = 0
        elif brakeCmd > 1:
            brakeCmd = 1
        #(REZWANA) These if statements are again for our test cases
        #based on what testing flag is passed in, different things are happening within carla
        #for example testing flag 1 will set the car to accelerate, turn off the brakes and take the car out of park
        if testingFlag == 1 or testingFlag == 22:   #RIDWAN added 'or testingFlag == 22'
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
            park=1
            throttleCmd = 1 if not park else 0
            brakeCmd=0

        self._control.steer = steerCmd
        self._control.brake = brakeCmd
        self._control.throttle = throttleCmd

        
        #self._control.hand_brake = bool(jsButtons[self._handbrake_idx])

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
globalArduinoTestCounter = 0
global_compass = None
global_sim_time = None
global_map = None

class HUD(object):
    def __init__(self, width, height):
        self.dim = (width, height)
        font = pygame.font.Font(pygame.font.get_default_font(), 20)
        font_name = 'courier' if os.name == 'nt' else 'mono'
        fonts = [x for x in pygame.font.get_fonts() if font_name in x]
        default_font = 'ubuntumono'
        mono = default_font if default_font in fonts else fonts[0]
        mono = pygame.font.match_font(mono)
        self._font_mono = pygame.font.Font(mono, 20 if os.name == 'nt' else 22)
        self._notifications = FadingText(font, (width, 40), (0, height - 40))
        self.help = HelpText(pygame.font.Font(mono, 16), width, height)
        self.can = CAN()    #RIDWAN added CAN
        self.server_fps = 0
        self.frame = 0
        self.simulation_time = 0
        self._show_info = True
        self._info_text = []
        self._server_clock = pygame.time.Clock()

    def on_world_tick(self, timestamp):
        self._server_clock.tick()
        self.server_fps = self._server_clock.get_fps()
        self.frame = timestamp.frame
        self.simulation_time = timestamp.elapsed_seconds

    def tick(self, world, clock):
        self._notifications.tick(world, clock)
        if not self._show_info:
            return
        t = world.player.get_transform()
        v = world.player.get_velocity()
        c = world.player.get_control()
        compass = world.imu_sensor.compass
        heading = 'N' if compass > 270.5 or compass < 89.5 else ''
        heading += 'S' if 90.5 < compass < 269.5 else ''
        heading += 'E' if 0.5 < compass < 179.5 else ''
        heading += 'W' if 180.5 < compass < 359.5 else ''
        colhist = world.collision_sensor.get_collision_history()
        collision = [colhist[x + self.frame - 200] for x in range(0, 200)]
        max_col = max(1.0, max(collision))
        collision = [x / max_col for x in collision]
        vehicles = world.world.get_actors().filter('vehicle.*')

        # Speed Var
        global speed
        speed = (3.6 * math.sqrt(v.x**2 + v.y**2 + v.z**2))
        global globalArduinoTestFlag
        global globalArduinoTestCounter
        if globalArduinoTestFlag:
            if globalArduinoTestCounter == 0:
                get_speed(world, globalArduinoTestFlag)
                globalArduinoTestCounter += 1
        else:
            get_speed(world, globalArduinoTestFlag)
        self.can.send_car_speed(speed)  #RIDWAN added CAN

        global global_compass
        global_compass = ('% 17.0f\N{DEGREE SIGN} % 2s' % (compass, heading)).strip()
        global global_sim_time
        global_sim_time = ('% 12s' % datetime.timedelta(seconds=self.simulation_time)).strip()
        global global_map
        global_map = ('% 20s' % world.map.name.split('/')[-1]).strip()
        global global_autonomous

        self._info_text = [
            'Server:  % 16.0f FPS' % self.server_fps,
            'Client:  % 16.0f FPS' % clock.get_fps(),
            '',
            'Vehicle: % 20s' % get_actor_display_name(world.player, truncate=20),
            'Map:     % 20s' % world.map.name.split('/')[-1],
            'Sim time: % 12s' % datetime.timedelta(seconds=(self.simulation_time)),
            'Autopilot: % 12s' % ('Enabled' if global_autonomous else 'Disabled'),
            '',
            'Speed:   % 15.0f km/h' % (3.6 * math.sqrt(v.x**2 + v.y**2 + v.z**2)),
            u'Compass:% 17.0f\N{DEGREE SIGN} % 2s' % (compass, heading),
            'Accelero: (%5.1f,%5.1f,%5.1f)' % (world.imu_sensor.accelerometer),
            'Gyroscop: (%5.1f,%5.1f,%5.1f)' % (world.imu_sensor.gyroscope),
            'Location:% 20s' % ('(% 5.1f, % 5.1f)' % (t.location.x, t.location.y)),
            'GNSS:% 24s' % ('(% 2.6f, % 3.6f)' % (world.gnss_sensor.lat, world.gnss_sensor.lon)),
            'Height:  % 18.0f m' % t.location.z,
            '']
        if isinstance(c, carla.VehicleControl):
            self.can.send_gear(c.gear)
            self.can.send_steering(c.steer)
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
            for d, vehicle in sorted(vehicles, key=lambda vehicles: vehicles[0]):
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
            info_surface = pygame.Surface((350, self.dim[1]))
            info_surface.set_alpha(100)
            display.blit(info_surface, (0, 0))
            v_offset = 4
            bar_h_offset = 200
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
    """Helper class to handle text output using pygame"""
    def __init__(self, font, width, height):
        lines = __doc__.split('\n')
        self.font = font
        self.line_space = 18
        self.dim = (780, len(lines) * self.line_space + 12)
        self.pos = (0.5 * width - 0.5 * self.dim[0], 0.5 * height - 0.5 * self.dim[1])
        self.seconds_left = 0
        self.surface = pygame.Surface(self.dim)
        self.surface.fill((0, 0, 0, 0))
        for n, line in enumerate(lines):
            text_texture = self.font.render(line, True, (255, 255, 255))
            self.surface.blit(text_texture, (22, n * self.line_space))
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
global_elapsed_time = None

class CollisionSensor(object):
    def __init__(self, parent_actor, hud):
        self.sensor = None
        self.history = []
        self._parent = parent_actor
        self.hud = hud
        world = self._parent.get_world()
        bp = world.get_blueprint_library().find('sensor.other.collision')
        self.sensor = world.spawn_actor(bp, carla.Transform(), attach_to=self._parent)
        # We need to pass the lambda a weak reference to self to avoid circular
        # reference.
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
        self.history.append((event.frame, intensity))
        if len(self.history) > 4000:
            self.history.pop(0)

        #RIDWAN added data logging
        if(global_recording):
            global global_sim_time
            global dfcoll
            global global_elapsed_time
            global global_autonomous
            event = 'Collision with %r' % actor_type
            dfcoll = dfcoll.append({'Sim_time': global_sim_time, 'Rec_time': global_elapsed_time,'Autopilot': str(global_autonomous),
            'Event': event, 'Intensity': intensity}, ignore_index= True)



# ==============================================================================
# -- LaneInvasionSensor --------------------------------------------------------
# ==============================================================================


class LaneInvasionSensor(object):
    def __init__(self, parent_actor, hud):
        self.sensor = None

        # If the spawn object is not a vehicle, we cannot use the Lane Invasion Sensor
        if parent_actor.type_id.startswith("vehicle."):
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
        self.hud.notification('Crossed line %s' % ' and '.join(text))

        #RIDWAN added data logging
        if(global_recording):
            global global_sim_time
            global dflane
            global global_elapsed_time
            global global_autonomous
            lane_event = 'Crossed line %s' % ' and '.join(text)
            dflane = dflane.append({'Sim_time': global_sim_time, 'Rec_time': global_elapsed_time, 'Autopilot': str(global_autonomous), 'Event': lane_event}, ignore_index= True)


# ==============================================================================
# -- GnssSensor ----------------------------------------------------------------
# ==============================================================================


class GnssSensor(object):
    def __init__(self, parent_actor):
        self.sensor = None
        self._parent = parent_actor
        self.lat = 0.0
        self.lon = 0.0
        world = self._parent.get_world()
        bp = world.get_blueprint_library().find('sensor.other.gnss')
        self.sensor = world.spawn_actor(bp, carla.Transform(carla.Location(x=1.0, z=2.8)), attach_to=self._parent)
        # We need to pass the lambda a weak reference to self to avoid circular
        # reference.
        weak_self = weakref.ref(self)
        self.sensor.listen(lambda event: GnssSensor._on_gnss_event(weak_self, event))

    @staticmethod
    def _on_gnss_event(weak_self, event):
        self = weak_self()
        if not self:
            return
        self.lat = event.latitude
        self.lon = event.longitude



#RIDWAN added obstacle sensor
# ==============================================================================
# -- ObstacleDetection ---------------------------------------------------------
# ==============================================================================

class ObstacleSensor(object):
    def __init__(self, parent_actor):
        self.sensor = None
        self._parent = parent_actor
        self.location = carla.Location(0, 0, 0)
        self.rotation = carla.Rotation(0, 0, 0)
        self.transform = carla.Transform(self.location, self.rotation)
        world = self._parent.get_world()
        bp = world.get_blueprint_library().find('sensor.other.obstacle')
        bp.set_attribute('distance','30')
        bp.set_attribute('hit_radius','1')
        bp.set_attribute("only_dynamics",str(True))
        self.sensor = world.spawn_actor(bp, self.transform, attach_to=self._parent)
        # We need to pass the lambda a weak reference to self to avoid circular
        # reference.
        weak_self = weakref.ref(self)
        self.sensor.listen(lambda event: ObstacleSensor._on_obstacle(weak_self, event))

    @staticmethod
    def _on_obstacle(weak_self, event):
        self = weak_self()
        if not self:
            return
        self.distance = event.distance
        obstacle = event.other_actor.type_id
        distance = event.distance
        #print(f"Obstacle detected [{obstacle}] at distance {distance} m")


        #RIDWAN added data logging
        if(global_recording):
            global global_sim_time
            global dfobs
            global global_elapsed_time
            global global_autonomous
            dfobs = dfobs.append({'Sim_time': global_sim_time, 'Rec_time': global_elapsed_time, 'Autopilot': str(global_autonomous), 'Obstacle_Detected': obstacle, 
            'Distance_from_Obstacle': distance}, ignore_index= True)




# ==============================================================================
# -- IMUSensor -----------------------------------------------------------------
# ==============================================================================


class IMUSensor(object):
    def __init__(self, parent_actor):
        self.sensor = None
        self._parent = parent_actor
        self.accelerometer = (0.0, 0.0, 0.0)
        self.gyroscope = (0.0, 0.0, 0.0)
        self.compass = 0.0
        world = self._parent.get_world()
        bp = world.get_blueprint_library().find('sensor.other.imu')
        self.sensor = world.spawn_actor(
            bp, carla.Transform(), attach_to=self._parent)
        # We need to pass the lambda a weak reference to self to avoid circular
        # reference.
        weak_self = weakref.ref(self)
        self.sensor.listen(
            lambda sensor_data: IMUSensor._IMU_callback(weak_self, sensor_data))

    @staticmethod
    def _IMU_callback(weak_self, sensor_data):
        self = weak_self()
        if not self:
            return
        limits = (-99.9, 99.9)
        self.accelerometer = (
            max(limits[0], min(limits[1], sensor_data.accelerometer.x)),
            max(limits[0], min(limits[1], sensor_data.accelerometer.y)),
            max(limits[0], min(limits[1], sensor_data.accelerometer.z)))
        self.gyroscope = (
            max(limits[0], min(limits[1], math.degrees(sensor_data.gyroscope.x))),
            max(limits[0], min(limits[1], math.degrees(sensor_data.gyroscope.y))),
            max(limits[0], min(limits[1], math.degrees(sensor_data.gyroscope.z))))
        self.compass = math.degrees(sensor_data.compass)


# ==============================================================================
# -- RadarSensor ---------------------------------------------------------------
# ==============================================================================


class RadarSensor(object):
    def __init__(self, parent_actor):
        self.sensor = None
        self._parent = parent_actor
        bound_x = 0.5 + self._parent.bounding_box.extent.x
        bound_y = 0.5 + self._parent.bounding_box.extent.y
        bound_z = 0.5 + self._parent.bounding_box.extent.z

        self.velocity_range = 7.5 # m/s
        world = self._parent.get_world()
        self.debug = world.debug
        bp = world.get_blueprint_library().find('sensor.other.radar')
        bp.set_attribute('horizontal_fov', str(35))
        bp.set_attribute('vertical_fov', str(20))
        self.sensor = world.spawn_actor(
            bp,
            carla.Transform(
                carla.Location(x=bound_x + 0.05, z=bound_z+0.05),
                carla.Rotation(pitch=5)),
            attach_to=self._parent)
        # We need a weak reference to self to avoid circular reference.
        weak_self = weakref.ref(self)
        self.sensor.listen(
            lambda radar_data: RadarSensor._Radar_callback(weak_self, radar_data))

    @staticmethod
    def _Radar_callback(weak_self, radar_data):
        self = weak_self()
        if not self:
            return
        # To get a numpy [[vel, altitude, azimuth, depth],...[,,,]]:
        # points = np.frombuffer(radar_data.raw_data, dtype=np.dtype('f4'))
        # points = np.reshape(points, (len(radar_data), 4))

        current_rot = radar_data.transform.rotation
        for detect in radar_data:
            azi = math.degrees(detect.azimuth)
            alt = math.degrees(detect.altitude)
            # The 0.25 adjusts a bit the distance so the dots can
            # be properly seen
            fw_vec = carla.Vector3D(x=detect.depth - 0.25)
            carla.Transform(
                carla.Location(),
                carla.Rotation(
                    pitch=current_rot.pitch + alt,
                    yaw=current_rot.yaw + azi,
                    roll=current_rot.roll)).transform(fw_vec)

            def clamp(min_v, max_v, value):
                return max(min_v, min(value, max_v))

            norm_velocity = detect.velocity / self.velocity_range # range [-1, 1]
            r = int(clamp(0.0, 1.0, 1.0 - norm_velocity) * 255.0)
            g = int(clamp(0.0, 1.0, 1.0 - abs(norm_velocity)) * 255.0)
            b = int(abs(clamp(- 1.0, 0.0, - 1.0 - norm_velocity)) * 255.0)
            self.debug.draw_point(
                radar_data.transform.location + fw_vec,
                size=0.075,
                life_time=0.06,
                persistent_lines=False,
                color=carla.Color(r, g, b))

# ==============================================================================
# -- CameraManager -------------------------------------------------------------
# ==============================================================================


class CameraManager(object):
    def __init__(self, parent_actor, hud, gamma_correction):
        self.sensor = None
        self.surface = None
        self._parent = parent_actor
        self.hud = hud
        self.recording = False
        bound_x = 0.5 + self._parent.bounding_box.extent.x
        bound_y = 0.5 + self._parent.bounding_box.extent.y
        bound_z = 0.5 + self._parent.bounding_box.extent.z
        Attachment = carla.AttachmentType

        if not self._parent.type_id.startswith("walker.pedestrian"):
            self._camera_transforms = [
                (carla.Transform(carla.Location(x=-2.0*bound_x, y=+0.0*bound_y, z=2.0*bound_z), carla.Rotation(pitch=8.0)), Attachment.SpringArm),
                (carla.Transform(carla.Location(x=+0.8*bound_x, y=+0.0*bound_y, z=1.3*bound_z)), Attachment.Rigid),
                (carla.Transform(carla.Location(x=+1.9*bound_x, y=+1.0*bound_y, z=1.2*bound_z)), Attachment.SpringArm),
                (carla.Transform(carla.Location(x=-2.8*bound_x, y=+0.0*bound_y, z=4.6*bound_z), carla.Rotation(pitch=6.0)), Attachment.SpringArm),
                (carla.Transform(carla.Location(x=-1.0, y=-1.0*bound_y, z=0.4*bound_z)), Attachment.Rigid)]
        else:
            self._camera_transforms = [
                (carla.Transform(carla.Location(x=-2.5, z=0.0), carla.Rotation(pitch=-8.0)), Attachment.SpringArm),
                (carla.Transform(carla.Location(x=1.6, z=1.7)), Attachment.Rigid),
                (carla.Transform(carla.Location(x=2.5, y=0.5, z=0.0), carla.Rotation(pitch=-8.0)), Attachment.SpringArm),
                (carla.Transform(carla.Location(x=-4.0, z=2.0), carla.Rotation(pitch=6.0)), Attachment.SpringArm),
                (carla.Transform(carla.Location(x=0, y=-2.5, z=-0.0), carla.Rotation(yaw=90.0)), Attachment.Rigid)]

        self.transform_index = 1
        self.sensors = [
            ['sensor.camera.rgb', cc.Raw, 'Camera RGB', {}],
            ['sensor.camera.depth', cc.Raw, 'Camera Depth (Raw)', {}],
            ['sensor.camera.depth', cc.Depth, 'Camera Depth (Gray Scale)', {}],
            ['sensor.camera.depth', cc.LogarithmicDepth, 'Camera Depth (Logarithmic Gray Scale)', {}],
            ['sensor.camera.semantic_segmentation', cc.Raw, 'Camera Semantic Segmentation (Raw)', {}],
            ['sensor.camera.semantic_segmentation', cc.CityScapesPalette, 'Camera Semantic Segmentation (CityScapes Palette)', {}],
            ['sensor.camera.instance_segmentation', cc.CityScapesPalette, 'Camera Instance Segmentation (CityScapes Palette)', {}],
            ['sensor.camera.instance_segmentation', cc.Raw, 'Camera Instance Segmentation (Raw)', {}],
            ['sensor.lidar.ray_cast', None, 'Lidar (Ray-Cast)', {'range': '50'}],
            ['sensor.camera.dvs', cc.Raw, 'Dynamic Vision Sensor', {}],
            ['sensor.camera.rgb', cc.Raw, 'Camera RGB Distorted',
                {'lens_circle_multiplier': '3.0',
                'lens_circle_falloff': '3.0',
                'chromatic_aberration_intensity': '0.5',
                'chromatic_aberration_offset': '0'}],
            ['sensor.camera.optical_flow', cc.Raw, 'Optical Flow', {}],
        ]
        world = self._parent.get_world()
        bp_library = world.get_blueprint_library()
        for item in self.sensors:
            bp = bp_library.find(item[0])
            if item[0].startswith('sensor.camera'):
                bp.set_attribute('image_size_x', str(hud.dim[0]))
                bp.set_attribute('image_size_y', str(hud.dim[1]))
                if bp.has_attribute('gamma'):
                    bp.set_attribute('gamma', str(gamma_correction))
                for attr_name, attr_value in item[3].items():
                    bp.set_attribute(attr_name, attr_value)
            elif item[0].startswith('sensor.lidar'):
                self.lidar_range = 50

                for attr_name, attr_value in item[3].items():
                    bp.set_attribute(attr_name, attr_value)
                    if attr_name == 'range':
                        self.lidar_range = float(attr_value)

            item.append(bp)
        self.index = None

    def toggle_camera(self):
        self.transform_index = (self.transform_index + 1) % len(self._camera_transforms)
        self.set_sensor(self.index, notify=False, force_respawn=True)

    def set_sensor(self, index, notify=True, force_respawn=False):
        index = index % len(self.sensors)
        needs_respawn = True if self.index is None else \
            (force_respawn or (self.sensors[index][2] != self.sensors[self.index][2]))
        if needs_respawn:
            if self.sensor is not None:
                self.sensor.destroy()
                self.surface = None
            self.sensor = self._parent.get_world().spawn_actor(
                self.sensors[index][-1],
                self._camera_transforms[self.transform_index][0],
                attach_to=self._parent,
                attachment_type=self._camera_transforms[self.transform_index][1])
            # We need to pass the lambda a weak reference to self to avoid
            # circular reference.
            weak_self = weakref.ref(self)
            self.sensor.listen(lambda image: CameraManager._parse_image(weak_self, image))
        if notify:
            self.hud.notification(self.sensors[index][2])
        self.index = index

    def next_sensor(self):
        self.set_sensor(self.index + 1)

    def toggle_recording(self):
        self.recording = not self.recording
        self.hud.notification('Recording %s' % ('On' if self.recording else 'Off'))

    def render(self, display):
        if self.surface is not None:
            display.blit(self.surface, (0, 0))

    @staticmethod
    def _parse_image(weak_self, image):
        self = weak_self()
        if not self:
            return
        if self.sensors[self.index][0].startswith('sensor.lidar'):
            points = np.frombuffer(image.raw_data, dtype=np.dtype('f4'))
            points = np.reshape(points, (int(points.shape[0] / 4), 4))
            lidar_data = np.array(points[:, :2])
            lidar_data *= min(self.hud.dim) / (2.0 * self.lidar_range)
            lidar_data += (0.5 * self.hud.dim[0], 0.5 * self.hud.dim[1])
            lidar_data = np.fabs(lidar_data)  # pylint: disable=E1111
            lidar_data = lidar_data.astype(np.int32)
            lidar_data = np.reshape(lidar_data, (-1, 2))
            lidar_img_size = (self.hud.dim[0], self.hud.dim[1], 3)
            lidar_img = np.zeros((lidar_img_size), dtype=np.uint8)
            lidar_img[tuple(lidar_data.T)] = (255, 255, 255)
            self.surface = pygame.surfarray.make_surface(lidar_img)
        elif self.sensors[self.index][0].startswith('sensor.camera.dvs'):
            # Example of converting the raw_data from a carla.DVSEventArray
            # sensor into a NumPy array and using it as an image
            dvs_events = np.frombuffer(image.raw_data, dtype=np.dtype([
                ('x', np.uint16), ('y', np.uint16), ('t', np.int64), ('pol', np.bool)]))
            dvs_img = np.zeros((image.height, image.width, 3), dtype=np.uint8)
            # Blue is positive, red is negative
            dvs_img[dvs_events[:]['y'], dvs_events[:]['x'], dvs_events[:]['pol'] * 2] = 255
            self.surface = pygame.surfarray.make_surface(dvs_img.swapaxes(0, 1))
        elif self.sensors[self.index][0].startswith('sensor.camera.optical_flow'):
            image = image.get_color_coded_flow()
            array = np.frombuffer(image.raw_data, dtype=np.dtype("uint8"))
            array = np.reshape(array, (image.height, image.width, 4))
            array = array[:, :, :3]
            array = array[:, :, ::-1]
            self.surface = pygame.surfarray.make_surface(array.swapaxes(0, 1))
        else:
            image.convert(self.sensors[self.index][1])
            array = np.frombuffer(image.raw_data, dtype=np.dtype("uint8"))
            array = np.reshape(array, (image.height, image.width, 4))
            array = array[:, :, :3]
            array = array[:, :, ::-1]
            self.surface = pygame.surfarray.make_surface(array.swapaxes(0, 1))
        if self.recording:
            image.save_to_disk('_out/%08d' % image.frame)


# ==============================================================================
# -- game_loop() ---------------------------------------------------------------
# ==============================================================================
global_world = None
global_sim_world = None
global_client = None
global_controller = None
global_recording = False
global_clock = None
global_autonomous = False
autonomous_counter = 0

def game_loop(args, testingFlag):
    global global_client
    pygame.init()
    pygame.font.init()
    world = None
    original_settings = None

    try:
        client = carla.Client(args.host, args.port)
        global_client = client 
        client.set_timeout(20.0)

        sim_world = client.get_world()  #RIDWAN changed this for map selection. Original was client.get_world(), specific was client.load_world('Town06')
        if args.sync:
            original_settings = sim_world.get_settings()
            settings = sim_world.get_settings()
            if not settings.synchronous_mode:
                settings.synchronous_mode = True
                settings.fixed_delta_seconds = 0.05
            sim_world.apply_settings(settings)

            traffic_manager = client.get_trafficmanager()
            traffic_manager.set_synchronous_mode(True)

        if args.autopilot and not sim_world.get_settings().synchronous_mode:
            print("WARNING: You are currently in asynchronous mode and could "
                  "experience some issues with the traffic simulation")

        display = pygame.display.set_mode(
            (args.width, args.height),
            pygame.HWSURFACE | pygame.DOUBLEBUF)
        display.fill((0,0,0))
        pygame.display.flip()

        hud = HUD(args.width, args.height)
        global global_hud
        global_hud = hud
        world = World(sim_world, hud, args)
        global global_world
        global_world = world
        #controller = DualControl(world, args.autopilot)

        if(testingFlag >= 23 and testingFlag <= 25):
            global global_controller
            global_controller = DualControl(world, args.autopilot)
        else:
            controller = DualControl(world, args.autopilot)

        agent = BasicAgent(world.player)    #RIDWAN autonomous

        clock = pygame.time.Clock()
        global global_clock
        global steer
        global auto
        global_clock = clock
        if testingFlag >=1:
            for i in range(60):
                clock.tick_busy_loop(60)
                if testingFlag >= 23 and testingFlag <= 25:
                    if global_controller.parse_events(world, clock, testingFlag, 0):
                        return
                else:
                    if controller.parse_events(world, clock, testingFlag, 0):
                        return
                world.tick(clock)
                world.render(display)
                
                if(auto == 1):
                    world.player.apply_control(carla.VehicleControl(throttle=.25, steer=steer))
                pygame.display.flip()
        else:

            run_time = time.time()
            while True:
                clock.tick_busy_loop(60)
                if controller.parse_events(world, clock, 0, 0):
                    return  
                world.tick(clock)
                world.render(display)

                #RIDWAN autonomous 
                global global_autonomous
                global autonomous_counter
                if global_autonomous:
                    world.player.set_autopilot(True)
                elif autonomous_counter == 0:
                    world.player.set_autopilot(False)
                    autonomous_counter += 1

                if(auto == 1):
                    world.player.apply_control(carla.VehicleControl(throttle=.25, steer=steer))
                pygame.display.flip()



                #RIDWAN added data logging
                global global_recording
                if(global_recording == True):
                    if time.time() > run_time + 0.5:    #0.5 is 120 samples per minute
                        run_time = time.time() 
                        global recording_start_time
                        global speed
                        global dfvehic
                        global global_compass
                        global global_sim_time
                        global global_elapsed_time
                        global globalWeather

                        elapsed_time = time.time() - recording_start_time
                        global_elapsed_time = elapsed_time
                        accelerometer = '(%5.1f,%5.1f,%5.1f)' % (world.imu_sensor.accelerometer)
                        gyroscope = '(%5.1f,%5.1f,%5.1f)' % (world.imu_sensor.gyroscope)
                        location = ('% 20s' % ('(% 5.1f, % 5.1f)' % (world.player.get_transform().location.x, world.player.get_transform().location.y))).strip()
                        gnss = ('% 24s' % ('(% 2.6f, % 3.6f)' % (world.gnss_sensor.lat, world.gnss_sensor.lon))).strip()
                        height = ('% 18.0f m' % world.player.get_transform().location.z).strip()
                        if(height == '-0 m'):
                            height = '0 m'
                        throttle = f"{int((world.player.get_control().throttle)*100)}%"
                        brake = f"{int((world.player.get_control().brake)*100)}%"
                        gear = '%s' % {-1: 'R', 0: 'N'}.get(world.player.get_control().gear, world.player.get_control().gear)
                        steering = world.player.get_control().steer
                        vehicle = get_actor_display_name(world.player, truncate=20)

                        dfvehic = dfvehic.append({'Sim_time': global_sim_time, 'Rec_time': elapsed_time, 'Server_fps': hud.server_fps, 'Client_fps': clock.get_fps(), 
                        'Autopilot': str(global_autonomous),'Speed': speed, 'Heading': global_compass, 'Accelerometer': accelerometer, 'Gyroscope': gyroscope, 'Location': location, 
                        'GNSS': gnss, 'Height': height, 'Throttle': throttle, 'Brake': brake, 'Gear': gear, 'Steering': steering, 'Vehicle': vehicle, 'Weather/Time': globalWeather}, 
                        ignore_index= True)

                #RIDWAN added CAN messages
                msg = hud.can.can_bus.recv(0)
                global attackFlag
                if msg is not None:
                    attackFlag=1
                    msg_data = msg.data
                    if (msg_data == bytearray(b'\x13\x88\x00\x00\x00\x00\x00\x00')):
                        world.player.apply_control(carla.VehicleControl(steer=0.99))
                    if (msg_data == bytearray(b'\xf2\x54\x00\x00\x00\x00\x00\x00')):
                        world.player.apply_control(carla.VehicleControl(steer=0.99))
                    if (msg_data == bytearray(b'\x20\x4E\x40\x9c\x81\x39\x02\x70')):
                        world.player.apply_control(carla.VehicleControl(throttle=1.0, brake=0.0, hand_brake=False, gear=2))
                else:
                    attackFlag = 0

    finally:
        global global_sim_world 
        world = global_world
        global_sim_world = sim_world
        global_client = client

        if testingFlag == 0:
            if (world and world.recording_enabled):
                client.stop_recorder()

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
        default='1600x900',
        help='window resolution (default: 1600x900)')
    argparser.add_argument(
        '--filter',
        metavar='PATTERN',
        default='vehicle.*',
        help='actor filter (default: "vehicle.*")')
    argparser.add_argument(
        '--generation',
        metavar='G',
        default='2',
        help='restrict to certain actor generation (values: "1","2","All" - default: "2")')
    argparser.add_argument(
        '--rolename',
        metavar='NAME',
        default='hero',
        help='actor role name (default: "hero")')
    argparser.add_argument(
        '--gamma',
        default=2.2,
        type=float,
        help='Gamma correction of the camera (default: 2.2)')
    argparser.add_argument(
        '--sync',
        action='store_true',
        help='Activate synchronous mode execution')
    args = argparser.parse_args()

    args.width, args.height = [int(x) for x in args.res.split('x')]

    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(format='%(levelname)s: %(message)s', level=log_level)

    logging.info('listening to server %s:%s', args.host, args.port)

    print(__doc__)

    try:

        game_loop(args, testingFlag)

    except KeyboardInterrupt:
        print('\nCancelled by user. Bye!')


if __name__ == '__main__':

    main(0)
