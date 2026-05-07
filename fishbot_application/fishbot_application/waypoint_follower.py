# 导入位姿消息类型，用于定义导航目标点
from geometry_msgs.msg import PoseStamped
# 导入Nav2导航器与任务结果类
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
# 导入ROS2 Python核心库
import rclpy
# 导入ROS2时间工具
from rclpy.duration import Duration

# 主函数
def main():
    # 初始化ROS2客户端
    rclpy.init()
    # 创建导航器实例
    navigator = BasicNavigator()
    # 等待Nav2导航系统全部启动完成
    navigator.waitUntilNav2Active()
    # 创建目标点列表，用于存储多个路点
    goal_poses = []
    # 定义第一个目标点
    goal_pose1 = PoseStamped()
    goal_pose1.header.frame_id = 'map'
    goal_pose1.header.stamp = navigator.get_clock().now().to_msg()
    goal_pose1.pose.position.x = 0.0
    goal_pose1.pose.position.y = 0.0
    goal_pose1.pose.orientation.w = 1.0
    # 将第一个点加入列表
    goal_poses.append(goal_pose1)
    # 定义第二个目标点
    goal_pose2 = PoseStamped()
    goal_pose2.header.frame_id = 'map'
    goal_pose2.header.stamp = navigator.get_clock().now().to_msg()
    goal_pose2.pose.position.x = 2.0
    goal_pose2.pose.position.y = 0.0
    goal_pose2.pose.orientation.w = 1.0
    # 将第二个点加入列表
    goal_poses.append(goal_pose2)
    # 定义第三个目标点
    goal_pose3 = PoseStamped()
    goal_pose3.header.frame_id = 'map'
    goal_pose3.header.stamp = navigator.get_clock().now().to_msg()
    goal_pose3.pose.position.x = 2.0
    goal_pose3.pose.position.y = 2.0
    goal_pose3.pose.orientation.w = 1.0
    # 将第三个点加入列表
    goal_poses.append(goal_pose3)
    # 调用Nav2路点导航功能，按顺序走完全部点
    navigator.followWaypoints(goal_poses)
    # 循环等待路点导航任务完成
    while not navigator.isTaskComplete():
        # 获取导航实时反馈
        feedback = navigator.getFeedback()
        # 打印当前正在前往的目标点编号
        navigator.get_logger().info(f'当前目标编号：{feedback.current_waypoint}')
    # 获取导航任务最终结果
    result = navigator.getResult()
    # 根据结果类型输出对应日志
    if result == TaskResult.SUCCEEDED:
        navigator.get_logger().info('导航结果：成功')
    elif result == TaskResult.CANCELED:
        navigator.get_logger().warn('导航结果：被取消')
    elif result == TaskResult.FAILED:
        navigator.get_logger().error('导航结果：失败')
    else:
        navigator.get_logger().error('导航结果：返回状态无效')

# 程序入口
if __name__ == '__main__':
    main()