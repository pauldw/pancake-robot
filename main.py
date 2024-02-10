#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2019, UFACTORY, Inc.
# All rights reserved.
#
# Author: Vinman <vinman.wen@ufactory.cc> <vinman.cub@gmail.com>

"""
Description: Move line(linear motion)
"""

import os
import sys
import time
import msvcrt

sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from xarm.wrapper import XArmAPI


#######################################################
"""
Just for test example
"""
try:
    from configparser import ConfigParser
    parser = ConfigParser()
    parser.read('robot.conf')
    ip = parser.get('xArm', 'ip')
except:
    ip = input('Please input the xArm ip address:')
    if not ip:
        print('input error, exit')
        sys.exit(1)
########################################################

offsets = {
    'gripper_tip': [0, 0, 80, 0, 0, 0],
    'ladle_lip': [0, 70, 250, 0, 9, -90],
    'brush_tip': [0, 0, 230, 0, 0, -90],
    'spatula_edge': [0, -40, 250, 0, -56, -90]
}

payloads = {
    'gripper': [0.277, [0, 0, 30]],
    'brush': [0.377, [0, 0, 65]],
    'ladle': [0.4, [0, 2.5, 90]],
    'spatula': [0.3, [0, 1, 80]] # total guess
}

positions = {
    # Relative to "gripper tip"
    'ladle': [200, 265, 197, 180, 0, 0],
    'brush': [242.076828, 282.630585, 208.809418, -175.604689, 1.695268, 90.70936],
    'spatula': [169.0, 278.0, 197.0, -177.000013, 0.0, 92.000005],
    'open_iron': [
        [296.221893, -85.830528, 40.560802, 98.589249, 0.369271, 33.893261],
        [314.422791, -111.97261, 122.805984, 132.589252, 0.369271, 33.893261],
        [375.90332, -202.867126, 176.57402, 176.589259, 0.369271, 33.893261]
    ],
    # Relative to "brush tip"
    'butter_dish': [342.459381, 113.522774, 15.214893, -178.239091, -4.378085, -179.380366],
    'butter_circle_top': [
        [416.364777, -236.65036, 128.111008, -173.239863, 38.273008, 133.082855],
        [396.010529, -222.641266, 52.147526, -173.239863, 38.273008, 133.082855],
        [432.203522, -206.247498, 85.152382, -173.239863, 38.273008, 133.082855],
    ],
    'butter_circle_bottom': [
        [372.843414, -166.932495, 14.932927, 179.202119, 39.424481, 129.362067],
        [341.170593, -110.324371, 17.019363, 179.202119, 39.424481, 129.362067],
        [311.383667, -168.212387, 13.902067, 179.202119, 39.424481, 129.362067],
    ],
    'pancake_iron': [336.530579, -143.349777, 23.555216, -175.359119, -0.935525, 123.618337],
    # Relative to "ladle lip"
    'batter_bowl': [84.279709, -281.187317, -4.071232, 179.999275, 0.009798, 90.035046],
    'ladle_dump': [345.092316, -107.443298, 52.222782, -175.255586, -0.719062, 65.020568],
    # Relative to "spatula"
    'spatula_seq': [
        [105.1436, 135.41745, 29.250355, 179.992629, 53.009826, -178.014606],
        [305.686859, -108.030716, 54.34576, 179.520053, 19.572181, -56.002155],
        [305.686859, -108.030716, 44.34576, 179.520053, 19.572181, -56.002155],
        [349.244751, -152.787125, 33.339344, 179.538388, 11.57243, -55.933973],
        [365.229889, -176.417435, 28.191858, 179.546352, 4.572662, -55.877537],
        [369.106201, -181.741928, 47.381966, 179.527616, -3.420673, -55.789932],
        [366.914642, -177.315811, 129.233093, 179.527616, -3.420673, -55.789932],
        [618.467224, 29.214106, 124.689827, 176.780914, -1.225499, 5.168881],
        [618.467224, 29.214106, 124.689827, 75.960968, 21.940846, 11.592082],
        [618.467224, 29.214106, 124.689827, 176.780914, -1.225499, 5.168881],
        [366.914642, -177.315811, 129.233093, 179.527616, -3.420673, -55.789932],
        [305.686859, -108.030716, 54.34576, 179.520053, 19.572181, -56.002155],
        [105.1436, 135.41745, 29.250355, 179.992629, 53.009826, -178.014606],
    ]
}

keys = {
    b'w': [ 1,  0,  0,  0,  0,  0],
    b'a': [ 0,  1,  0,  0,  0,  0],
    b's': [-1,  0,  0,  0,  0,  0],
    b'd': [ 0, -1,  0,  0,  0,  0],
    b'r': [ 0,  0,  1,  0,  0,  0],
    b'f': [ 0,  0, -1,  0,  0,  0],

    b'u': [ 0,  0,  0,  0,  1,  0],
    b'h': [ 0,  0,  0, -1,  0,  0],
    b'j': [ 0,  0,  0,  0, -1,  0],
    b'k': [ 0,  0,  0,  1,  0,  0],
    b'i': [ 0,  0,  0,  0,  0, -1],
    b'y': [ 0,  0,  0,  0,  0,  1],
}

arm = XArmAPI(ip)

arm.set_tcp_offset(offsets[sys.argv[1]], is_radian=False)
arm.set_tcp_load(*payloads[sys.argv[2]])

arm.motion_enable(enable=True)
arm.set_mode(0)
arm.set_state(state=0)

#arm.reset(wait=True)

def pick_up_ladle():
    arm.open_lite6_gripper()
    time.sleep(1.5)
    pos = positions['ladle'].copy()
    pos[2] += 40
    arm.set_position(*pos, speed=100, is_radian=False, wait=True)
    pos[2] -= 40
    arm.set_position(*pos, speed=100, is_radian=False, wait=True)
    arm.close_lite6_gripper()
    time.sleep(1.0)
    pos[2] += 10
    arm.set_position(*pos, speed=100, is_radian=False, wait=True)
    pos[1] -= 20
    arm.set_position(*pos, speed=100, is_radian=False, wait=True)

    arm.set_tcp_load(*payloads['ladle'], wait=True)
    arm.set_tcp_offset(offsets['ladle_lip'], is_radian=False)
    arm.set_state(state=0)

def return_ladle():
    # Assumes ladle is already picked up with pick_up_ladle
    arm.set_tcp_load(*payloads['ladle'], wait=True)
    arm.set_tcp_offset(offsets['gripper_tip'], is_radian=False)
    arm.set_state(state=0)

    pos = positions['ladle'].copy()
    pos[2] += 10
    pos[1] -= 20
    arm.set_position(*pos, speed=100, is_radian=False, wait=True)
    pos[1] += 20
    arm.set_position(*pos, speed=100, is_radian=False, wait=True)
    pos[2] -= 10
    arm.set_position(*pos, speed=100, is_radian=False, wait=True)
    arm.open_lite6_gripper()
    time.sleep(1.0)
    pos[2] += 40
    arm.set_position(*pos, speed=100, is_radian=False, wait=True)
    arm.stop_lite6_gripper()

def pick_up_brush():
    arm.open_lite6_gripper()
    time.sleep(1.5)
    pos = positions['brush'].copy()
    pos[2] += 40
    arm.set_position(*pos, speed=100, is_radian=False, wait=True)
    pos[2] -= 40
    arm.set_position(*pos, speed=100, is_radian=False, wait=True)
    arm.close_lite6_gripper()
    time.sleep(1.0)
    pos[0] += 20
    arm.set_position(*pos, speed=100, is_radian=False, wait=True)

    arm.set_tcp_load(*payloads['brush'], wait=True)
    arm.set_tcp_offset(offsets['brush_tip'], is_radian=False)
    arm.set_state(state=0)

def return_brush():
    # Assumes brush is already picked up with pick_up_brush
    arm.set_tcp_load(*payloads['brush'], wait=True)
    arm.set_tcp_offset(offsets['gripper_tip'], is_radian=False)
    arm.set_state(state=0)

    pos = positions['brush'].copy()
    pos[0] += 20
    arm.set_position(*pos, speed=100, is_radian=False, wait=True)
    pos[0] -= 20
    arm.set_position(*pos, speed=100, is_radian=False, wait=True)
    arm.open_lite6_gripper()
    time.sleep(1.0)
    pos[2] += 40
    arm.set_position(*pos, speed=100, is_radian=False, wait=True)
    arm.stop_lite6_gripper()

def pick_up_spatula():
    arm.open_lite6_gripper()
    time.sleep(1.5)
    pos = positions['spatula'].copy()
    pos[2] += 40
    arm.set_position(*pos, speed=100, is_radian=False, wait=True)
    pos[2] -= 40
    arm.set_position(*pos, speed=100, is_radian=False, wait=True)
    arm.close_lite6_gripper()
    time.sleep(1.0)
    pos[0] -= 20
    arm.set_position(*pos, speed=100, is_radian=False, wait=True)

    arm.set_tcp_load(*payloads['spatula'], wait=True)
    arm.set_tcp_offset(offsets['spatula_edge'], is_radian=False)
    arm.set_state(state=0)

def return_spatula():
    # Assumes brush is already picked up with pick_up_brush
    arm.set_tcp_load(*payloads['spatula'], wait=True)
    arm.set_tcp_offset(offsets['gripper_tip'], is_radian=False)
    arm.set_state(state=0)

    pos = positions['spatula'].copy()
    pos[0] -= 20
    pos[1] -= 100
    arm.set_position(*pos, speed=100, is_radian=False, wait=True)

    pos[1] += 100
    arm.set_position(*pos, speed=100, is_radian=False, wait=True)

    pos[0] += 20
    arm.set_position(*pos, speed=100, is_radian=False, wait=True)
    arm.open_lite6_gripper()
    time.sleep(1.0)
    pos[2] += 40
    arm.set_position(*pos, speed=100, is_radian=False, wait=True)
    arm.stop_lite6_gripper()

def load_butter():
    # Assumes brush is already picked up with pick_up_brush
    pos = positions['butter_dish'].copy()
    pos[2] += 60
    arm.set_position(*pos, speed=100, is_radian=False, wait=True)
    pos[2] -= 60
    arm.set_position(*pos, speed=100, is_radian=False, wait=True)
    time.sleep(1.0)
    pos[2] += 60
    arm.set_position(*pos, speed=100, is_radian=False, wait=True)

def butter_circle():
    pose0 = positions['butter_circle_top'][0].copy()
    pose1 = positions['butter_circle_top'][1].copy()
    pose2 = positions['butter_circle_top'][2].copy()

    arm.set_position(*pose0, speed=100, is_radian=False, wait=True)
    arm.move_circle(pose1, pose2, 100, speed=100, is_radian=False, wait=True)

    pose0 = positions['butter_circle_bottom'][0].copy()
    pose1 = positions['butter_circle_bottom'][1].copy()
    pose2 = positions['butter_circle_bottom'][2].copy()

    arm.set_position(*pose0, speed=100, is_radian=False, wait=True)
    arm.move_circle(pose1, pose2, 100, speed=100, is_radian=False, wait=True)

    pos = positions['pancake_iron'].copy()
    pos[2] += 60

    arm.set_position(*pos, speed=100, is_radian=False, wait=True)

def load_batter():
    # Assumes ladle is picked up
    pos = positions['batter_bowl'].copy()

    # Move to lip of bowl first to avoid collisions
    pos[2] += 160
    pos[0] += 100
    pos[1] += 100
    arm.set_position(*pos, speed=100, is_radian=False, wait=True)

    # Above middle of bowl
    pos[0] -= 100
    pos[1] -= 100
    arm.set_position(*pos, speed=100, is_radian=False, wait=True)

    pos[2] -= 160
    arm.set_position(*pos, speed=25, is_radian=False, wait=True)

    time.sleep(2)

    # TODO set new payload

    pos[2] += 160
    arm.set_position(*pos, speed=25, is_radian=False, wait=True)

def dump_batter():
    # Assumes ladle is picked up
    pos = positions['ladle_dump'].copy()

    # Avoid colliding with bowl
    pos[2] += 100
    pos[0] -= 60
    pos[1] -= 60
    arm.set_position(*pos, speed=25, is_radian=False, wait=True)

    pos[2] -= 100
    pos[0] += 60
    pos[1] += 60
    arm.set_position(*pos, speed=25, is_radian=False, wait=True)


    arm.set_tool_position(pitch=80, is_radian=False, wait=True)
    arm.set_tool_position(pitch=-80, speed=100, is_radian=False, wait=True)

    # Avoid colliding with butter
    pos[2] += 100
    pos[0] -= 60
    pos[1] -= 60
    arm.set_position(*pos, speed=100, is_radian=False, wait=True)

def open_iron():
    arm.close_lite6_gripper()
    time.sleep(1.0)

    pose0 = positions['open_iron'][0].copy()
    pose1 = positions['open_iron'][1].copy()
    pose2 = positions['open_iron'][2].copy()

    pose0[0] -= 40
    pose0[1] += 40
    arm.set_position(*pose0, speed=100, is_radian=False, wait=True)

    pose0[0] += 40
    pose0[1] -= 40
    arm.set_position(*pose0, speed=100, is_radian=False, wait=True)

    arm.move_circle(pose1, pose2, 25, speed=100, is_radian=False, wait=True)

def record_trajectory():
    # Turn on manual mode before recording
    arm.set_mode(2)
    arm.set_state(0)

    arm.start_record_trajectory()

    # Wait for any key to finish
    print("Recording. Press any key to finish.")
    msvcrt.getch()

    arm.stop_record_trajectory()
    arm.save_record_trajectory('recorded.traj')

    time.sleep(1)

    # Turn off manual mode after recording
    arm.set_mode(0)
    arm.set_state(0)

def play_trajectory():
    arm.close_lite6_gripper()
    time.sleep(1.0)
    arm.load_trajectory('recorded.traj')
    arm.playback_trajectory()

def dispense_pancake():
    for pos in positions['spatula_seq']:
        arm.set_position(*pos, speed=100, is_radian=False, wait=False)

amount = 1
while 1:
    key = msvcrt.getch()
    print(key)

    if key == b'-':
        amount = max(1, amount-1)
        continue

    if key == b'+':
        amount = amount + 1
        continue

    if key == b'1':
        arm.open_lite6_gripper()
        continue

    if key == b'2':
        arm.close_lite6_gripper()
        continue

    if key == b'3':
        arm.stop_lite6_gripper()
        continue

    if key == b'z':
        pick_up_ladle()
        continue

    if key == b'x':
        return_ladle()
        continue

    if key == b'c':
        pick_up_brush()
        continue

    if key == b'v':
        return_brush()
        continue

    if key == b'b':
        pick_up_spatula()
        continue

    if key == b'n':
        return_spatula()
        continue

    if key == b'5':
        load_butter()
        continue

    if key == b'6':
        butter_circle()
        continue

    if key == b'7':
        load_batter()
        continue

    if key == b'8':
        dump_batter()
        continue

    if key == b'9':
        open_iron()
        continue

    if key == b'0':
        dispense_pancake()
        continue

    if key == b',':
        record_trajectory()
        continue

    if key == b'.':
        play_trajectory()
        continue

    if key == b'\\':
        arm.reset()
        continue

    if key == b'\x1b': # esc
        sys.exit(0)

    # Otherwise, treat as position control
    if key in keys:
        pos = keys[key].copy()
        for i in range(0, len(pos)):
            pos[i] = pos[i] * amount

        arm.set_tool_position(*pos, speed=100, wait=True)
        print(arm.get_position(is_radian=False))
        continue

    print(f"Unrecognized key {key}")

arm.disconnect()

