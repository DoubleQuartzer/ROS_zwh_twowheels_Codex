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
Q/E   : increase / decrease linear speed
Z/C   : increase / decrease angular speed
Ctrl+C: quit
"""


class WasdTeleop(Node):
    def __init__(self):
        super().__init__('wasd_teleop')
        self.publisher = self.create_publisher(Twist, 'cmd_vel', 10)
        self.linear_speed = 0.25
        self.angular_speed = 0.9
        self.settings = termios.tcgetattr(sys.stdin)
        self.get_logger().info('WASD teleop ready. Focus this terminal and press W/A/S/D.')
        print(HELP_TEXT)

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

    def spin(self):
        try:
            while rclpy.ok():
                key = self.read_key()

                if key == 'w':
                    self.publish_twist(self.linear_speed, 0.0)
                elif key == 's':
                    self.publish_twist(-self.linear_speed, 0.0)
                elif key == 'a':
                    self.publish_twist(0.0, self.angular_speed)
                elif key == 'd':
                    self.publish_twist(0.0, -self.angular_speed)
                elif key == ' ':
                    self.publish_twist()
                elif key == 'q':
                    self.linear_speed *= 1.1
                    self.get_logger().info(f'linear speed: {self.linear_speed:.2f} m/s')
                elif key == 'e':
                    self.linear_speed *= 0.9
                    self.get_logger().info(f'linear speed: {self.linear_speed:.2f} m/s')
                elif key == 'z':
                    self.angular_speed *= 1.1
                    self.get_logger().info(f'angular speed: {self.angular_speed:.2f} rad/s')
                elif key == 'c':
                    self.angular_speed *= 0.9
                    self.get_logger().info(f'angular speed: {self.angular_speed:.2f} rad/s')
                elif key == '\x03':
                    break
        finally:
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
