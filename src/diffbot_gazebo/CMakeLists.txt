cmake_minimum_required(VERSION 3.8)
project(diffbot_gazebo)

find_package(ament_cmake REQUIRED)

install(DIRECTORY launch urdf worlds rviz
  DESTINATION share/${PROJECT_NAME}
)

install(PROGRAMS
  scripts/diff_drive_kinematics.py
  scripts/wasd_teleop.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
