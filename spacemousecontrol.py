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
import json
import signal

sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from xarm.wrapper import XArmAPI
import pyspacemouse

# TODO
# Lock axis set (i.e. clamp any of x,y,z,roll,pitch,yaw to 0)
# Set speed for sequence capture
# Add pause to sequence
# Detect when sequence is finished
#
# Sequence storage under different names
# Sequence replay by sequence name
# (Sequences should probably just be Python code?)
#
# Standardize magnet mounts on rectangle magnets
# Move to melamine board
# Mount tools near bowls and iron (brush->butter, ladle->batter, spatula->iron)
# Record sequences and make a pancake
#
# Add jogging
# Add cursor position parameter changes
# Add inserts
# Add deletes
# Add axis locks
# Add TCP payload changes
# Add TCP offset changes? (problematic as that context is lost in the recorded position)
# Add reference frame changes?
# Add reference frame measurement? (i.e. move robot arm to a certain location and record that as the reference frame)
# Add comment/label ability?
#
# Ladle needs anti-tilt grip on handle
# Need to wait a bit for batter overflow to fall off ladle into reservoir
# Need a way to step through sequences and insert/update/delete commands
# Need a way to verify ladle location as it can move, maybe a short test sequence?


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

arm = XArmAPI(ip)

arm.motion_enable(enable=True)
time.sleep(1)

arm.set_tcp_load(*payloads[sys.argv[2]])
arm.set_tcp_offset(offsets[sys.argv[1]], is_radian=False)

arm.set_mode(5)
arm.set_state(0)
time.sleep(1)

# Very helpful!
arm.set_cartesian_velo_continuous(True)

pyspacemouse.open()

multiplier = 100.0
speed = 100
radius = 10
gripper_state = None

sequence = []

def callback_state_changed(item):
    pass
    # TODO add debug mode
    #print('state changed:', item)

arm.register_state_changed_callback(callback=callback_state_changed)

def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    arm.disconnect()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def execute_command(command):
    global gripper_state
    print(f"Executing: {command}")

    if arm.mode != 0:
        arm.set_mode(0)
        arm.set_state(0)
        time.sleep(1.0)

    if command == 'open':
        if gripper_state == "open":
            return
        arm.open_lite6_gripper()
        arm.set_pause_time(1.0)
        gripper_state = "open"
    elif command == 'close':
        if gripper_state == "close":
            return
        arm.close_lite6_gripper()
        arm.set_pause_time(1.0)
        gripper_state = "close"
    elif command == 'stop':
        if gripper_state == "stop":
            return
        arm.stop_lite6_gripper()
        arm.set_pause_time(1.0)
        gripper_state = "stop"
    elif command[0] == "pause":
        arm.set_pause_time(command[1])
    elif command[0] == "include":
        filename = command[1]
        play_sequence(read_sequence(filename))
    else:
        arm.set_position(*command, wait=False)

def play_sequence(mysequence):
    for newpos in mysequence:
        execute_command(newpos)
    finished = False
    ready = False
    while not finished:
        code, cmdnum = arm.get_cmdnum()
        if (cmdnum == 0):
            finished = True
        if (code != 0 or arm.has_err_warn):
            print("Error, stopping playback.")
            ready = True
            finished = True
            # TODO actually jump out of outer loop and reset robot at this point
        time.sleep(0.5)
    print("Waiting for arm to be ready.")
    while not ready:
        code, newstate = arm.get_state()
        if newstate == 2:
            ready = True
        if code != 0 or arm.has_err_warn:
            print("Playback error.")
            ready = True
        time.sleep(0.5)
    print("Playback finished.")

def read_sequence(filename):
    f = open(filename, "r")
    mysequence = []
    for line in f.readlines():
        strippedline = line.strip()
        mysequence.append(json.loads(strippedline))
    f.close()
    print(f"Loaded sequence from {filename}")
    return mysequence.copy()

while 1:
    delay_start = time.time()
    state = pyspacemouse.read()

    if msvcrt.kbhit():
        key = msvcrt.getch()
        print(key)  # just to show the result
        if key == b'r':
            code, curpos = arm.get_position()
            curpos.append(radius) # radius
            curpos.append(speed) # speed
            if code == 0:
                sequence.append(curpos)
            print(f"Recorded {curpos}")
        if key == b's':
            filename = input("Save sequence as: ")
            f = open(filename, "w")
            for newpos in sequence:
                f.write(json.dumps(newpos) + "\n")
            f.close()
            print(f"Saved as {filename}")
        if key == b'l':
            filename = input("Load sequence from: ")
            sequence = read_sequence(filename)
        if key == b'p':
            play_sequence(sequence)
        if key == b'c':
            sequence = []
            print("Cleared sequence.")
        if key == b'1':
            arm.open_lite6_gripper()
            sequence.append("open")
        if key == b'2':
            arm.close_lite6_gripper()
            sequence.append( "close")
        if key == b'3':
            arm.stop_lite6_gripper()
            sequence.append("stop")
        if key == b'4':
            duration = float(input("Pause length: "))
            sequence.append(["pause", duration])
        if key == b'x':
            arm.disconnect()
            sys.exit(0)
        if key == b'[':
            speed = max(10, speed-10)
            print(f"Speed: {speed}")
        if key == b']':
            speed = min(200, speed+10)
            print(f"Speed: {speed}")
        if key == b';':
            radius = max(1, radius-1)
            print(f"Radius: {radius}")
        if key == b"'":
            radius = min(50, radius+1)
            print(f"Radius: {radius}")
        if key == b'o':
            for newpos in sequence:
                print(json.dumps(newpos))
        if key == b'i':
            filename = input("Include subsequence: ")
            sequence.append(["include", filename])

    pos = [
        state.y * multiplier,
        state.x * multiplier * -1.0,
        state.z * multiplier,
        state.roll * multiplier / 1.5,
        state.pitch * multiplier / 1.5,
        state.yaw * multiplier / 1.5 * -1.0
    ]

    if sum([abs(v) for v in pos]) > 0:
        print(pos)

    if arm.mode != 5:
        arm.set_mode(5)
        arm.set_state(0)
        time.sleep(1.0)

    if not arm.connected:
        arm.connect()

    code = arm.vc_set_cartesian_velocity(pos, duration=0.05)

    if sum([abs(v) for v in pos]) > 0:
        print("done setting velocity")

    if code != 0:
        print("Error! Resetting ...")
        arm.clean_error()
        arm.clean_warn()
        arm.arm.clean_servo_error(4)
        arm.set_mode(5)
        arm.set_state(0)
        time.sleep(1)
        delay_state = time.time()
        while time.time() - delay_start < 0.05:
            pyspacemouse.read()  # Throwing out reads to avoid buffering

    while time.time() - delay_start < 0.05:
        pyspacemouse.read() # Throwing out reads to avoid buffering

arm.disconnect()
