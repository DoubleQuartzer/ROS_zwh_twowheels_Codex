# diffbot_gazebo

这是一个 ROS2 + Gazebo Classic 双轮差速小车仿真包，适合课程设计、毕设和论文中的小车运动学解算验证。

## 推荐环境

- Ubuntu 22.04
- ROS2 Humble
- Gazebo Classic 11

## Ubuntu 安装 Git

```bash
sudo apt update
sudo apt install -y git
git --version
```

第一次使用 Git 建议配置用户名和邮箱：

```bash
git config --global user.name "你的名字"
git config --global user.email "你的邮箱"
```

## 安装 ROS2/Gazebo 依赖

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

- `w` 前进
- `s` 后退
- `a` 左转
- `d` 右转
- `space` 停止
- `q/e` 增大/减小线速度
- `z/c` 增大/减小角速度

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
