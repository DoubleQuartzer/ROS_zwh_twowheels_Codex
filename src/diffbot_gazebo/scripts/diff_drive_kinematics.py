#!/usr/bin/env python3
import math

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray


class DiffDriveKinematics(Node):
    def __init__(self):
        super().__init__('diff_drive_kinematics')
        self.declare_parameter('wheel_radius', 0.085)
        self.declare_parameter('wheel_separation', 0.410)

        self.wheel_radius = float(self.get_parameter('wheel_radius').value)
        self.wheel_separation = float(self.get_parameter('wheel_separation').value)

        self.publisher = self.create_publisher(Float64MultiArray, 'wheel_speed_ref', 10)
        self.subscription = self.create_subscription(Twist, 'cmd_vel', self.cmd_vel_callback, 10)

        self.get_logger().info(
            f'diff drive kinematics ready: r={self.wheel_radius:.3f} m, '
            f'L={self.wheel_separation:.3f} m'
        )

    def cmd_vel_callback(self, msg: Twist):
        v = msg.linear.x
        w = msg.angular.z

        omega_r = (v + w * self.wheel_separation / 2.0) / self.wheel_radius
        omega_l = (v - w * self.wheel_separation / 2.0) / self.wheel_radius

        rpm_r = omega_r * 60.0 / (2.0 * math.pi)
        rpm_l = omega_l * 60.0 / (2.0 * math.pi)

        out = Float64MultiArray()
        out.data = [omega_l, omega_r, rpm_l, rpm_r]
        self.publisher.publish(out)

        self.get_logger().info(
            f'v={v:.3f} m/s, w={w:.3f} rad/s -> '
            f'left={omega_l:.3f} rad/s ({rpm_l:.1f} rpm), '
            f'right={omega_r:.3f} rad/s ({rpm_r:.1f} rpm)'
        )


def main():
    rclpy.init()
    node = DiffDriveKinematics()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
