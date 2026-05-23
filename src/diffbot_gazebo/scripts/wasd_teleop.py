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
A/D   : turn left / turn right
Space : stop
Q/E   : linear speed faster / slower
Z/C   : turn speed faster / slower
Ctrl+C: quit
"""


class WasdTeleop(Node):
    def __init__(self):
        super().__init__('wasd_teleop')
        self.publisher = self.create_publisher(Twist, 'cmd_vel', 10)
        self.linear_speed = 0.25
        self.angular_speed = 0.9
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

    def set_motion(self, action, linear_x=0.0, angular_z=0.0):
        self.current_linear = linear_x
        self.current_angular = angular_z
        self.publish_current_twist()
        self.print_status(action, linear_x, angular_z)

    def print_status(self, action, linear_x=0.0, angular_z=0.0):
        self.get_logger().info(
            f'{action}: cmd_linear={linear_x:.2f} m/s, cmd_angular={angular_z:.2f} rad/s, '
            f'setting_linear={self.linear_speed:.2f} m/s, setting_angular={self.angular_speed:.2f} rad/s'
        )

    def spin(self):
        try:
            while rclpy.ok():
                key = self.read_key()
                rclpy.spin_once(self, timeout_sec=0.0)

                if key == 'w':
                    self.set_motion('forward', self.linear_speed, 0.0)
                elif key == 's':
                    self.set_motion('backward', -self.linear_speed, 0.0)
                elif key == 'a':
                    self.set_motion('turn left', 0.0, self.angular_speed)
                elif key == 'd':
                    self.set_motion('turn right', 0.0, -self.angular_speed)
                elif key == ' ':
                    self.set_motion('stop')
                elif key == 'q':
                    self.linear_speed *= 1.1
                    self.print_status('linear speed increased', self.current_linear, self.current_angular)
                elif key == 'e':
                    self.linear_speed *= 0.9
                    self.print_status('linear speed decreased', self.current_linear, self.current_angular)
                elif key == 'z':
                    self.angular_speed *= 1.1
                    self.print_status('turn speed increased', self.current_linear, self.current_angular)
                elif key == 'c':
                    self.angular_speed *= 0.9
                    self.print_status('turn speed decreased', self.current_linear, self.current_angular)
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
