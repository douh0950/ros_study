# 初始化机器人初始位置和姿态
# 导入ROS2位姿消息类型，用于设置机器人初始位置和姿态
from geometry_msgs.msg import PoseStamped
# 导入Nav2官方提供的简易导航API，方便控制导航
from nav2_simple_commander.robot_navigator import BasicNavigator
# 导入ROS2 Python客户端库
import rclpy

def main():
    # 初始化ROS2 Python通信上下文
    rclpy.init()
    # 创建导航器实例，用于与Nav2导航栈交互
    navigator = BasicNavigator()
    # 创建带时间戳的位姿对象，存储机器人初始位姿
    initial_pose = PoseStamped()
    # 指定坐标系为地图坐标系（map），全局定位基准
    initial_pose.header.frame_id = 'map'
    # 设置消息时间戳为当前ROS时钟时间
    initial_pose.header.stamp = navigator.get_clock().now().to_msg()
    # 设置机器人初始X坐标：地图原点
    initial_pose.pose.position.x = 0.0
    # 设置机器人初始Y坐标：地图原点
    initial_pose.pose.position.y = 0.0
    # 设置初始朝向（四元数），w=1表示无旋转，朝向正前方
    initial_pose.pose.orientation.w = 1.0
    # 向AMCL发送机器人初始位姿，完成定位初始化
    navigator.setInitialPose(initial_pose)
    # 阻塞等待，直到Nav2导航系统所有节点启动完成
    navigator.waitUntilNav2Active()
    # 保持节点运行，处理ROS2回调事件
    rclpy.spin(navigator)
    # 关闭ROS2通信上下文，释放资源
    rclpy.shutdown()

if __name__ == '__main__':
    # 程序入口，执行主函数
    main()