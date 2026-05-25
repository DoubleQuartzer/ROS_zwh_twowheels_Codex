#!/usr/bin/env python3
import select
import sys
import termios
import tty

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node


HELP_TEXT = """
WASD keyboard control
---------------------
W/S   : forward / backward
A/D   : turn left / turn right, or add curve steering while driving straight
W then A : forward left curve
W then D : forward right curve
S then A : backward left curve
S then D : backward right curve
Space : stop
Q/E   : linear speed faster / slower
Z/C   : turn speed faster / slower
Ctrl+C: quit

Command rule:
W/S always interrupt the current motion and switch to straight driving.
A/D add curve steering only when the robot is currently driving straight;
otherwise A/D interrupt the current motion and switch to spin-in-place.
"""


class WasdTeleop(Node):
    def __init__(self):
        super().__init__('wasd_teleop')
        self.publisher = self.create_publisher(Twist, 'cmd_vel', 10)
        self.linear_speed = 0.25
        self.angular_speed = 0.9
        self.linear_dir = 0
        self.angular_dir = 0
        self.current_linear = 0.0
        self.current_angular = 0.0
        self.settings = termios.tcgetattr(sys.stdin)
        self.timer = self.create_timer(0.05, self.publish_current_twist)
        self.get_logger().info('WASD teleop ready. Focus this terminal and press W/A/S/D.')
        print(HELP_TEXT)
        self.print_status('ready')

    def read_key(self):
        tty.setraw(sys.stdin.fileno())
        ready, _, _ = select.select([sys.stdin], [], [], 0.1)
        key = sys.stdin.read(1) if ready else ''
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.settings)
        return key.lower()

    def publish_twist(self, linear_x=0.0, angular_z=0.0):
        msg = Twist()
        msg.linear.x = linear_x
        msg.angular.z = angular_z
        self.publisher.publish(msg)

    def publish_current_twist(self):
        self.publish_twist(self.current_linear, self.current_angular)

    def update_motion_from_dirs(self, action):
        self.current_linear = self.linear_dir * self.linear_speed
        self.current_angular = self.angular_dir * self.angular_speed
        self.publish_current_twist()
        self.print_status(action, self.current_linear, self.current_angular)

    def print_status(self, action, linear_x=0.0, angular_z=0.0):
        radius_text = 'straight'
        if abs(angular_z) > 1e-6 and abs(linear_x) > 1e-6:
            radius_text = f'curve_radius={abs(linear_x / angular_z):.2f} m'
        elif abs(angular_z) > 1e-6:
            radius_text = 'spin in place'

        self.get_logger().info(
            f'{action}: cmd_linear={linear_x:.2f} m/s, cmd_angular={angular_z:.2f} rad/s, '
            f'setting_linear={self.linear_speed:.2f} m/s, setting_angular={self.angular_speed:.2f} rad/s, '
            f'{radius_text}'
        )

    def describe_motion(self):
        if self.linear_dir == 0 and self.angular_dir == 0:
            return 'stop'
        if self.linear_dir > 0 and self.angular_dir > 0:
            return 'forward left curve'
        if self.linear_dir > 0 and self.angular_dir < 0:
            return 'forward right curve'
        if self.linear_dir < 0 and self.angular_dir > 0:
            return 'backward left curve'
        if self.linear_dir < 0 and self.angular_dir < 0:
            return 'backward right curve'
        if self.linear_dir > 0:
            return 'forward'
        if self.linear_dir < 0:
            return 'backward'
        if self.angular_dir > 0:
            return 'turn left'
        return 'turn right'

    def stop_motion(self):
        self.linear_dir = 0
        self.angular_dir = 0
        self.update_motion_from_dirs('stop')

    def set_straight_motion(self, linear_dir):
        self.linear_dir = linear_dir
        self.angular_dir = 0
        self.update_motion_from_dirs(self.describe_motion())

    def set_turn_motion(self, angular_dir):
        if self.linear_dir != 0 and self.angular_dir == 0:
            self.angular_dir = angular_dir
        else:
            self.linear_dir = 0
            self.angular_dir = angular_dir
        self.update_motion_from_dirs(self.describe_motion())

    def spin(self):
        try:
            while rclpy.ok():
                key = self.read_key()
                rclpy.spin_once(self, timeout_sec=0.0)

                if key == 'w':
                    self.set_straight_motion(1)
                elif key == 's':
                    self.set_straight_motion(-1)
                elif key == 'a':
                    self.set_turn_motion(1)
                elif key == 'd':
                    self.set_turn_motion(-1)
                elif key == ' ':
                    self.stop_motion()
                elif key == 'q':
                    self.linear_speed *= 1.1
                    self.update_motion_from_dirs('linear speed increased')
                elif key == 'e':
                    self.linear_speed *= 0.9
                    self.update_motion_from_dirs('linear speed decreased')
                elif key == 'z':
                    self.angular_speed *= 1.1
                    self.update_motion_from_dirs('turn speed increased')
                elif key == 'c':
                    self.angular_speed *= 0.9
                    self.update_motion_from_dirs('turn speed decreased')
                elif key == '\x03':
                    break
        finally:
            self.current_linear = 0.0
            self.current_angular = 0.0
            self.publish_twist()
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.settings)


def main():
    rclpy.init()
    node = WasdTeleop()
    try:
        node.spin()
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
