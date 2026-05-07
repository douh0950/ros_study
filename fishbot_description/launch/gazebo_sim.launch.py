import launch
import launch_ros
from ament_index_python.packages import get_package_share_directory
from launch.launch_description_sources import PythonLaunchDescriptionSource
def generate_launch_description():
    # Gazebo 中机器人实体的名称
    robot_name_in_model = "fishbot"
    # 获取 fishbot_description 功能包的 share 路径
    urdf_tutorial_path = get_package_share_directory('fishbot_description')
    # FishBot 总装 xacro 文件路径
    default_model_path = urdf_tutorial_path + '/urdf/fishbot/fishbot.urdf.xacro'
    # Gazebo 仿真世界文件路径
    default_world_path = urdf_tutorial_path + '/world/custom_room.world'
    # 声明 model 参数，默认使用 FishBot 的 xacro 模型文件
    action_declare_arg_mode_path = launch.actions.DeclareLaunchArgument(
        name='model',
        default_value=str(default_model_path),
        description='URDF 的绝对路径'
    )
    # 使用 xacro 命令将 .urdf.xacro 文件转换为 robot_description 参数
    robot_description = launch_ros.parameter_descriptions.ParameterValue(
        launch.substitutions.Command(
            ['xacro ', launch.substitutions.LaunchConfiguration('model')]
        ),
        value_type=str
    )
    # 启动 robot_state_publisher，用于根据 robot_description 和 /joint_states 发布 TF
    robot_state_publisher_node = launch_ros.actions.Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{
            'robot_description': robot_description
        }]
    )
    # 启动 Gazebo，并加载自定义 world 文件
    launch_gazebo = launch.actions.IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            get_package_share_directory('gazebo_ros'),
            '/launch',
            '/gazebo.launch.py'
        ]),
        launch_arguments=[
            ('world', default_world_path),
            ('verbose', 'true')
        ]
    )
    # 将机器人模型从 /robot_description 加载到 Gazebo 中
    spawn_entity_node = launch_ros.actions.Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-topic',
            '/robot_description',
            '-entity',
            robot_name_in_model,
        ]
    )
    # 加载并激活 joint_state_broadcaster，用于发布 /joint_states
    load_joint_state_controller = launch.actions.ExecuteProcess(
        cmd=[
            'ros2',
            'control',
            'load_controller',
            '--set-state',
            'active',
            'fishbot_joint_state_broadcaster'
        ],
        output='screen'
    )
    # 加载并激活 effort_controller，用于力矩控制左右轮；当前未加入 LaunchDescription，因此不会启动
    load_fishbot_effort_controller = launch.actions.ExecuteProcess(
        cmd=[
            'ros2',
            'control',
            'load_controller',
            '--set-state',
            'active',
            'fishbot_effort_controller'
        ],
        output='screen'
    )
    # 加载并激活 diff_drive_controller，用于接收 /cmd_vel 并控制左右轮差速运动
    load_fishbot_diff_drive_controller = launch.actions.ExecuteProcess(
        cmd=[
            'ros2',
            'control',
            'load_controller',
            '--set-state',
            'active',
            'fishbot_diff_drive_controller'
        ],
        output='screen'
    )
    # 返回 LaunchDescription，按顺序启动各个节点和事件
    return launch.LaunchDescription([
        # 声明 model 参数
        action_declare_arg_mode_path,
        # 启动 robot_state_publisher
        robot_state_publisher_node,
        # 启动 Gazebo
        launch_gazebo,
        # 在 Gazebo 中生成 FishBot 模型
        spawn_entity_node,
        # 当机器人模型加载完成后，再加载 joint_state_broadcaster
        launch.actions.RegisterEventHandler(
            event_handler=launch.event_handlers.OnProcessExit(
                target_action=spawn_entity_node,
                on_exit=[
                    load_joint_state_controller
                ],
            )
        ),
        # 当 joint_state_broadcaster 加载完成后，再加载 diff_drive_controller
        launch.actions.RegisterEventHandler(
            event_handler=launch.event_handlers.OnProcessExit(
                target_action=load_joint_state_controller,
                on_exit=[
                    load_fishbot_diff_drive_controller
                ],
            )
        ),
    ])