README.md
🤖 基于 ROS2 + Nav2 自动巡检机器人项目
一个可直接仿真运行的全自主室内巡逻机器人项目，支持多点循环导航、语音播报、到达自动拍照存档。

---
📌 项目简介
本项目基于 ROS 2 Humble 与 Navigation2 实现一套完整的自动巡检机器人仿真系统。
机器人功能流程：
1. 自动读取多个预设巡逻目标点
2. 自主规划路径，依次导航前往每个点位
3. 到达点位后语音播报当前位置
4. 调用摄像头自动拍照并保存到本地
5. 全部点位走完后自动循环巡检

---
📦 功能包说明
功能包名
作用说明
fishbot_description
机器人URDF模型、底盘、雷达、相机仿真模型配置
fishbot_navigation2
Nav2导航全套参数、代价地图、控制器、AMCL定位配置
fishbot_application
Python版导航控制、单点导航、多点路点导航代码
fishbot_application_cpp
C++版本导航应用代码（备用）
autopatrol_interfaces
自定义语音合成服务接口文件
autopatrol_robot
自动巡检核心功能包，整合导航+语音+拍照+循环巡逻

---
💻 开发环境
- 操作系统：Ubuntu 22.04
- ROS 版本：ROS 2 Humble
- 仿真环境：Gazebo Classic
- 导航框架：Navigation2
- 建图算法：SLAM-Toolbox

---
🔧 依赖安装教程
复制逐条运行即可：
1. 安装导航 + 建图依赖
sudo apt install ros-$ROS_DISTRO-nav2-bringup ros-$ROS_DISTRO-slam-toolbox -y
2. 安装仿真与机器人驱动依赖
sudo apt install ros-$ROS_DISTRO-robot-state-publisher ros-$ROS_DISTRO-joint-state-publisher ros-$ROS_DISTRO-gazebo-ros-pkgs ros-$ROS_DISTRO-ros2-controllers ros-$ROS_DISTRO-xacro -y
3. 安装语音、图像、坐标转换工具
sudo apt install python3-pip espeak-ng -y
sudo pip3 install espeakng
sudo apt install ros-$ROS_DISTRO-tf-transformations -y
sudo pip3 install transforms3d

---
🚀 编译与完整运行流程
第一步：编译工作空间
colcon build
source install/setup.bash
第二步：启动 Gazebo 仿真环境
ros2 launch fishbot_description gazebo_sim.launch.py
第三步：启动 Nav2 导航系统
ros2 launch fishbot_navigation2 navigation2.launch.py
第四步：启动自动巡检巡逻任务
ros2 launch autopatrol_robot autopatrol.launch.py

---
✨ 项目亮点
- ✅ 纯仿真环境，零硬件也能跑完整巡检任务
- ✅ 多点循环自动巡逻，无需人工干预
- ✅ 到达点位自动语音播报
- ✅ 实时相机图像自动保存本地
- ✅ 标准Nav2架构，可直接迁移到真实机器人
- ✅ 代码注释完整，适合课程毕设/实训/学习

---
👤 作者信息
项目来源：FishROS 小鱼开源社区
GitHub：https://github.com/fishros
适合：ROS2入门学习、机器人实训、自动化巡检毕设项目