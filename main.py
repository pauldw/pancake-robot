#!/usr/bin/env python3

import sys
import time
import msvcrt
import json
import signal

from xarm.wrapper import XArmAPI
import pyspacemouse

XARM_IP = sys.argv[1]

TCP_OFFSETS = {
    'gripper_tip': [0, 0, 80, 0, 0, 0],
}
TCP_OFFSET = 'gripper_tip'

TCP_LOADS = {
    'gripper': [0.277, [0, 0, 30]],
}
TCP_LOAD = 'gripper'


class Controller:
    def __init__(self, arm, spacemouse):
        self.arm = arm
        self.spacemouse = spacemouse

        self.multiplier = 100.0
        self.speed = 100
        self.radius = 10
        self.gripper_state = None

        self.sequence = []

        self.last_set_velocity = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

        arm.set_cartesian_velo_continuous(True)

        def sigint_handler(sig, frame):
            print('You pressed Ctrl+C!')
            self.arm.disconnect()
            sys.exit(0)

        signal.signal(signal.SIGINT, sigint_handler)

    def execute_command(self, command):
        print(f"Executing: {command}")

        if self.arm.mode != 0:
            self.arm.set_mode(0)
            self.arm.set_state(0)
            time.sleep(1.0)

        if command == 'open':
            if self.gripper_state == "open":
                return
            self.arm.open_lite6_gripper()
            self.arm.set_pause_time(1.0)
            self.gripper_state = "open"
        elif command == 'close':
            if self.gripper_state == "close":
                return
            self.arm.close_lite6_gripper()
            self.arm.set_pause_time(1.0)
            self.gripper_state = "close"
        elif command == 'stop':
            if self.gripper_state == "stop":
                return
            self.arm.stop_lite6_gripper()
            self.arm.set_pause_time(1.0)
            self.gripper_state = "stop"
        elif command[0] == "pause":
            self.arm.set_pause_time(command[1])
        elif command[0] == "include":
            filename = command[1]
            self.play_sequence(self.read_sequence(filename))
        else:
            self.arm.set_position(*command, wait=False)

    def play_sequence(self, mysequence):
        for newpos in mysequence:
            self.execute_command(newpos)
        finished = False
        ready = False
        while not finished:
            code, cmdnum = self.arm.get_cmdnum()
            if cmdnum == 0:
                finished = True
            if code != 0 or self.arm.has_err_warn:
                print("Error, stopping playback.")
                ready = True
                finished = True
            time.sleep(0.5)
        print("Waiting for arm to be ready.")
        while not ready:
            code, newstate = self.arm.get_state()
            if newstate == 2:
                ready = True
            if code != 0 or self.arm.has_err_warn:
                print("Playback error.")
                ready = True
            time.sleep(0.5)
        print("Playback finished.")

    def read_sequence(self, filename):
        f = open(filename, "r")
        sequence = []
        for line in f.readlines():
            strippedline = line.strip()
            sequence.append(json.loads(strippedline))
        f.close()
        print(f"Loaded sequence from {filename}")
        return sequence.copy()

    def run_forever(self):
        while 1:
            loop_start_time = time.time()

            if not self.arm.connected:
                print("Arm not connected! Connecting ...")
                self.arm.connect()
            elif not self.arm.arm.ready:
                print("Arm not ready. Resetting ...")
                self.arm.clean_error()
                self.arm.clean_warn()
                self.arm.motion_enable(enable=True)
                delay_start_time = time.time()
                while time.time() - delay_start_time < 1:
                    pyspacemouse.read()  # Throwing out reads to avoid buffering
                self.arm.set_tcp_offset(TCP_OFFSETS[TCP_OFFSET], is_radian=False)
                self.arm.set_mode(5)
                self.arm.set_state(0)
                self.arm.set_tcp_load(*TCP_LOADS[TCP_LOAD])
                print("Done resetting.")
            elif msvcrt.kbhit():
                key = msvcrt.getch()
                print(key)  # just to show the result
                if key == b'r':
                    code, curpos = self.arm.get_position()
                    curpos.append(self.radius)  # radius
                    curpos.append(self.speed)  # speed
                    if code == 0:
                        self.sequence.append(curpos)
                    print(f"Recorded {curpos}")
                elif key == b's':
                    filename = input("Save sequence as: ")
                    f = open(filename, "w")
                    for pos in self.sequence:
                        f.write(json.dumps(pos) + "\n")
                    f.close()
                    print(f"Saved as {filename}")
                elif key == b'l':
                    filename = input("Load sequence from: ")
                    self.sequence = self.read_sequence(filename)
                elif key == b'p':
                    self.play_sequence(self.sequence)
                elif key == b'c':
                    self.sequence = []
                    print("Cleared sequence.")
                elif key == b'1':
                    self.arm.open_lite6_gripper()
                    self.sequence.append("open")
                elif key == b'2':
                    self.arm.close_lite6_gripper()
                    self.sequence.append("close")
                elif key == b'3':
                    self.arm.stop_lite6_gripper()
                    self.sequence.append("stop")
                elif key == b'4':
                    duration = float(input("Pause length: "))
                    self.sequence.append(["pause", duration])
                elif key == b'x':
                    self.arm.disconnect()
                    sys.exit(0)
                elif key == b'[':
                    speed = max(10, self.speed - 10)
                    print(f"Speed: {speed}")
                elif key == b']':
                    speed = min(200, self.speed + 10)
                    print(f"Speed: {speed}")
                elif key == b';':
                    radius = max(1, self.radius - 1)
                    print(f"Radius: {radius}")
                elif key == b"'":
                    radius = min(50, self.radius + 1)
                    print(f"Radius: {radius}")
                elif key == b'o':
                    for pos in self.sequence:
                        print(json.dumps(pos))
                elif key == b'i':
                    filename = input("Include subsequence: ")
                    self.sequence.append(["include", filename])
            elif self.spacemouse is not None:
                if self.arm.mode != 5:
                    self.arm.set_mode(5)
                    self.arm.set_state(0)
                    delay_start_time = time.time()
                    while time.time() - delay_start_time < 1:
                        self.spacemouse.read()  # Throwing out reads to avoid buffering
                    continue

                spacemouse_state = self.spacemouse.read()

                velocity = [
                    spacemouse_state.y * self.multiplier,
                    spacemouse_state.x * self.multiplier * -1.0,
                    spacemouse_state.z * self.multiplier,
                    spacemouse_state.roll * self.multiplier / 1.5,
                    spacemouse_state.pitch * self.multiplier / 1.5,
                    spacemouse_state.yaw * self.multiplier / 1.5 * -1.0
                ]

                if sum([abs(v) for v in velocity]) > 0 or sum([abs(v) for v in self.last_set_velocity]) > 0:
                    print(f"Setting velocity: {velocity}")
                    self.arm.vc_set_cartesian_velocity(velocity, duration=0.5)
                    self.last_set_velocity = velocity

            while time.time() - loop_start_time < 0.05:
                if self.spacemouse is not None:
                    self.spacemouse.read()  # Throwing out reads to avoid buffering


def main():
    arm = XArmAPI(XARM_IP)
    spacemouse = pyspacemouse.open()

    if spacemouse is None:
        print("No spacemouse found, continuing with jogging disabled.")

    controller = Controller(arm, spacemouse)
    controller.run_forever()


if __name__ == '__main__':
    main()
