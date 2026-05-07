# 加载地图 + 加载导航参数 + 启动官方 NAV2 导航栈 + 打开 RViz 可视化，让小车进入自主导航模式。
# 导入Python系统模块，用于文件路径操作
import os
# 导入ROS2 launch核心库，用于编写启动文件
import launch
# 导入ROS2专门用于节点启动的工具库
import launch_ros
# 导入功能包路径查找工具：可以找到任意ROS2功能包的安装路径
from ament_index_python.packages import get_package_share_directory
# 导入启动文件描述器：用于包含（调用）其他的launch.py文件
from launch.launch_description_sources import PythonLaunchDescriptionSource

# 所有ROS2 launch文件必须有的入口函数：生成启动描述
def generate_launch_description():
    # ====================== 1. 路径配置区 ======================
    # 获取 fishbot_navigation2 这个功能包的共享目录（存放地图、配置文件）
    fishbot_navigation2_dir = get_package_share_directory(
        'fishbot_navigation2')
    # 获取 nav2_bringup 功能包路径（官方导航启动包）
    nav2_bringup_dir = get_package_share_directory('nav2_bringup')
    # 拼接RViz配置文件路径：使用导航包自带的默认配置
    rviz_config_dir = os.path.join(
        nav2_bringup_dir, 'rviz', 'nav2_default_view.rviz')
    # ====================== 2. 定义可配置的启动参数 ======================
    # 是否使用仿真时间（Gazebo仿真时必须为true，真机为false）
    use_sim_time = launch.substitutions.LaunchConfiguration(
        'use_sim_time', default='true')
    # 地图yaml文件路径，默认使用room.yaml
    map_yaml_path = launch.substitutions.LaunchConfiguration(
        'map', default=os.path.join(fishbot_navigation2_dir, 'maps', 'room.yaml'))
    # 导航参数文件路径（包含传感器、控制器、规划器配置）
    nav2_param_path = launch.substitutions.LaunchConfiguration(
        'params_file', default=os.path.join(fishbot_navigation2_dir, 'config', 'nav2_params.yaml'))
    # ====================== 3. 组装并返回所有启动动作 ======================
    return launch.LaunchDescription([
        # 声明参数1：是否使用仿真时间
        launch.actions.DeclareLaunchArgument('use_sim_time', default_value=use_sim_time,
                                             description='Use simulation (Gazebo) clock if true'),
        # 声明参数2：地图文件路径
        launch.actions.DeclareLaunchArgument('map', default_value=map_yaml_path,
                                             description='Full path to map file to load'),
        # 声明参数3：导航参数文件路径
        launch.actions.DeclareLaunchArgument('params_file', default_value=nav2_param_path,
                                             description='Full path to param file to load'),
        # ====================== 核心：调用官方导航启动文件 ======================
        launch.actions.IncludeLaunchDescription(
            # 包含 nav2_bringup 里的 bringup_launch.py（官方导航总启动文件）
            PythonLaunchDescriptionSource(
                [nav2_bringup_dir, '/launch', '/bringup_launch.py']), 
            # 把我们上面定义的 地图、仿真时间、参数文件 传给官方导航启动脚本
            launch_arguments={
                'map': map_yaml_path,
                'use_sim_time': use_sim_time,
                'params_file': nav2_param_path}.items(),
        ),
        # ====================== 启动 RViz2 可视化工具 ======================
        launch_ros.actions.Node(
            package='rviz2',        # 功能包名
            executable='rviz2',    # 可执行文件
            name='rviz2',          # 节点名
            arguments=['-d', rviz_config_dir],  # 加载默认导航配置界面
            parameters=[{'use_sim_time': use_sim_time}],  # 使用仿真时间
            output='screen'),      # 日志输出到终端
    ])
