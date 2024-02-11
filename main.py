#!/usr/bin/env python3

import sys
import time
import msvcrt
import json
import signal

from xarm.wrapper import XArmAPI
import pyspacemouse

XARM_IP = sys.argv[1]

offsets = {
    'gripper_tip': [0, 0, 80, 0, 0, 0],
}

payloads = {
    'gripper': [0.277, [0, 0, 30]],
}

arm = XArmAPI(XARM_IP)

arm.motion_enable(enable=True)
time.sleep(1)

arm.set_tcp_load(*payloads['gripper'])
arm.set_tcp_offset(offsets['gripper_tip'], is_radian=False)

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


def sigint_handler(sig, frame):
    print('You pressed Ctrl+C!')
    arm.disconnect()
    sys.exit(0)


signal.signal(signal.SIGINT, sigint_handler)


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
    loop_start_time = time.time()

    if not arm.connected:
        print("Arm not connected! Connecting ...")
        arm.connect()
    elif arm.has_err_warn:
        print("Error or warn! Resetting ...")
        arm.clean_error()
        arm.clean_warn()
        delay_start_time = time.time()
        while time.time() - delay_start_time < 1:
            pyspacemouse.read()  # Throwing out reads to avoid buffering
        continue
    elif msvcrt.kbhit():
        key = msvcrt.getch()
        print(key)  # just to show the result
        if key == b'r':
            code, curpos = arm.get_position()
            curpos.append(radius)  # radius
            curpos.append(speed)  # speed
            if code == 0:
                sequence.append(curpos)
            print(f"Recorded {curpos}")
        elif key == b's':
            filename = input("Save sequence as: ")
            f = open(filename, "w")
            for newpos in sequence:
                f.write(json.dumps(newpos) + "\n")
            f.close()
            print(f"Saved as {filename}")
        elif key == b'l':
            filename = input("Load sequence from: ")
            sequence = read_sequence(filename)
        elif key == b'p':
            play_sequence(sequence)
        elif key == b'c':
            sequence = []
            print("Cleared sequence.")
        elif key == b'1':
            arm.open_lite6_gripper()
            sequence.append("open")
        elif key == b'2':
            arm.close_lite6_gripper()
            sequence.append("close")
        elif key == b'3':
            arm.stop_lite6_gripper()
            sequence.append("stop")
        elif key == b'4':
            duration = float(input("Pause length: "))
            sequence.append(["pause", duration])
        elif key == b'x':
            arm.disconnect()
            sys.exit(0)
        elif key == b'[':
            speed = max(10, speed - 10)
            print(f"Speed: {speed}")
        elif key == b']':
            speed = min(200, speed + 10)
            print(f"Speed: {speed}")
        elif key == b';':
            radius = max(1, radius - 1)
            print(f"Radius: {radius}")
        elif key == b"'":
            radius = min(50, radius + 1)
            print(f"Radius: {radius}")
        elif key == b'o':
            for newpos in sequence:
                print(json.dumps(newpos))
        elif key == b'i':
            filename = input("Include subsequence: ")
            sequence.append(["include", filename])
    else:
        if arm.mode != 5:
            arm.set_mode(5)
            arm.set_state(0)
            delay_start_time = time.time()
            while time.time() - delay_start_time < 1:
                pyspacemouse.read()  # Throwing out reads to avoid buffering
            continue

        spacemouse_state = pyspacemouse.read()

        velocity = [
            spacemouse_state.y * multiplier,
            spacemouse_state.x * multiplier * -1.0,
            spacemouse_state.z * multiplier,
            spacemouse_state.roll * multiplier / 1.5,
            spacemouse_state.pitch * multiplier / 1.5,
            spacemouse_state.yaw * multiplier / 1.5 * -1.0
        ]

        if sum([abs(v) for v in velocity]) > 0:
            print(f"Setting velocity: {velocity}")
            code = arm.vc_set_cartesian_velocity(velocity, duration=0.05)
            print("Done setting velocity.")

    while time.time() - loop_start_time < 0.05:
        pyspacemouse.read()  # Throwing out reads to avoid buffering
