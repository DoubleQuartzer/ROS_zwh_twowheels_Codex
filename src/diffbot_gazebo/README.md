# diffbot_gazebo

这是一个 ROS2 + Gazebo Classic 双轮差速小车仿真包，适合课程设计、毕设和论文中的小车运动学解算验证。

## 模型说明

小车模型包含：

- 双轮差速驱动轮
- 前后两个球形支撑轮
- 加高机体和顶部平台
- 顶部圆柱形雷达外观件
- 前部灯条、侧面装饰条和传感器支架

## 推荐环境

- Ubuntu 22.04
- ROS2 Humble
- Gazebo Classic 11

## 安装依赖

```bash
sudo apt update
sudo apt install -y \
  ros-humble-desktop \
  ros-humble-gazebo-ros-pkgs \
  ros-humble-xacro \
  ros-humble-rviz2 \
  python3-colcon-common-extensions
```

## 编译

```bash
source /opt/ros/humble/setup.bash
cd ~/ros2_diff_drive_ws
colcon build --symlink-install
source install/setup.bash
```

## 启动 Gazebo 仿真

```bash
source /opt/ros/humble/setup.bash
source ~/ros2_diff_drive_ws/install/setup.bash
ros2 launch diffbot_gazebo sim.launch.py
```

## WASD 键盘控制

另开一个终端：

```bash
source /opt/ros/humble/setup.bash
source ~/ros2_diff_drive_ws/install/setup.bash
ros2 run diffbot_gazebo wasd_teleop.py
```

常用按键：

```text
W：前进
S：后退
A：左转
D：右转
空格：停止
Q：线速度加快
E：线速度减慢
Z：转向角速度加快
C：转向角速度减慢
Ctrl+C：退出
```

控制节点每次按键都会打印当前信息：

```text
cmd_linear：本次发给小车的线速度，单位 m/s
cmd_angular：本次发给小车的角速度，单位 rad/s
setting_linear：当前线速度档位，按 Q/E 调整
setting_angular：当前转向速度档位，按 Z/C 调整
```

速度调节规则：

```text
Q：当前线速度乘以 1.1，所以越来越快
E：当前线速度乘以 0.9，所以越来越慢
Z：当前转向角速度乘以 1.1，所以转弯越来越快
C：当前转向角速度乘以 0.9，所以转弯越来越慢
```

初始速度：

```text
线速度 setting_linear = 0.25 m/s
转向角速度 setting_angular = 0.90 rad/s
```

## 运动解算节点

如果要观察小车运动解算结果，再开一个终端：

```bash
source /opt/ros/humble/setup.bash
source ~/ros2_diff_drive_ws/install/setup.bash
ros2 run diffbot_gazebo diff_drive_kinematics.py
```

解算节点订阅 `/cmd_vel`，发布 `/wheel_speed_ref`，数据顺序为：

```text
[left_rad_s, right_rad_s, left_rpm, right_rpm]
```

## 论文中可写的运动学关系

设左右轮角速度分别为 `omega_l`、`omega_r`，轮半径为 `r`，轮距为 `L`：

```text
v = r / 2 * (omega_r + omega_l)
w = r / L * (omega_r - omega_l)
```

其中 `v` 是车体中心线速度，`w` 是绕垂直轴的角速度。反解为：

```text
omega_r = (v + w * L / 2) / r
omega_l = (v - w * L / 2) / r
```

本模型参数：

```text
r = 0.085 m
L = 0.410 m
```

查看仿真里程计：

```bash
ros2 topic echo /odom
```

手动发布速度指令：

```bash
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.25}, angular: {z: 0.5}}"
```
