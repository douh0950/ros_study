# 导入ROS2 Python客户端库，用于创建节点、通信等
import rclpy
# 导入位姿消息类型
# PoseStamped：带时间戳和坐标系的位姿，Nav2导航目标必须使用它
# Pose：普通位姿类型
from geometry_msgs.msg import PoseStamped, Pose
# 导入Nav2提供的高级导航API
# BasicNavigator：封装导航控制
# TaskResult：导航结果枚举
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
# 导入TF坐标变换工具
# TransformListener：监听TF数据
# Buffer：缓存TF坐标变换
from tf2_ros import TransformListener, Buffer
# 导入欧拉角与四元数互相转换工具
# euler_from_quaternion：四元数转欧拉角
# quaternion_from_euler：欧拉角转四元数
from tf_transformations import euler_from_quaternion, quaternion_from_euler
# 导入ROS2时间工具
from rclpy.duration import Duration
# 导入自定义语音服务接口
from autopatrol_interfaces.srv import SpeachText
# 导入图像消息类型
from sensor_msgs.msg import Image
# 导入ROS图像与OpenCV图像转换工具
from cv_bridge import CvBridge
# 导入OpenCV库，用于保存图像
import cv2
# 定义巡逻节点类
# 继承BasicNavigator，表示该类拥有Nav2导航能力
class PatrolNode(BasicNavigator):
    # 构造函数
    def __init__(self, node_name='patrol_node'):
        # 调用父类构造函数
        # 初始化ROS2节点和Nav2导航器
        super().__init__(node_name)
        # 声明机器人初始位置参数
        # 参数格式：[x, y, yaw]
        self.declare_parameter('initial_point', [0.0, 0.0, 0.0])
        # 声明目标点参数
        # 每三个数字表示一个目标点：[x, y, yaw]
        self.declare_parameter('target_points', [0.0, 0.0, 0.0, 1.0, 1.0, 1.57])
        # 获取初始位置参数
        self.initial_point_ = self.get_parameter('initial_point').value
        # 获取目标点参数
        self.target_points_ = self.get_parameter('target_points').value
        # 创建TF缓存对象
        # 用于保存TF坐标变换数据
        self.buffer_ = Buffer()
        # 创建TF监听器
        # 自动订阅/tf和/tf_static
        self.listener_ = TransformListener(self.buffer_, self)
        # 创建语音服务客户端
        # 服务名称：speech_text
        self.speach_client_ = self.create_client(SpeachText, 'speech_text')
        # 声明图像保存路径参数
        self.declare_parameter('image_save_path', '')
        # 获取图像保存路径
        self.image_save_path = self.get_parameter('image_save_path').value
        # 创建CvBridge对象
        # 用于ROS图像与OpenCV图像格式转换
        self.bridge = CvBridge()
        # 用于保存最新图像
        self.latest_image = None
        # 创建图像订阅者
        # 订阅摄像头话题
        self.subscription_image = self.create_subscription(Image, '/camera_sensor/image_raw', self.image_callback, 10)
    # 图像回调函数
    # 每收到一帧图像都会执行
    def image_callback(self, msg):
        # 保存最新图像
        self.latest_image = msg
    # 保存当前图像
    def record_image(self):
        # 判断是否收到过图像
        if self.latest_image is not None:
            # 获取机器人当前位姿
            pose = self.get_current_pose()
            # ROS图像转OpenCV图像
            cv_image = self.bridge.imgmsg_to_cv2(self.latest_image)
            # 保存图像
            # 文件名中包含机器人当前坐标
            cv2.imwrite(f'{self.image_save_path}image_{pose.translation.x:3.2f}_{pose.translation.y:3.2f}.png', cv_image)
    # 调用语音合成服务
    def speach_text(self, text):
        # 如果服务未启动，则循环等待
        while not self.speach_client_.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('语音合成服务未上线，等待中。。。')
        # 创建服务请求对象
        request = SpeachText.Request()
        # 设置播报文本
        request.text = text
        # 异步发送服务请求
        future = self.speach_client_.call_async(request)
        # 阻塞等待服务返回
        rclpy.spin_until_future_complete(self, future)
        # 判断服务是否成功返回
        if future.result() is not None:
            # 获取服务返回结果
            result = future.result().result
            # 判断语音是否合成成功
            if result:
                self.get_logger().info(f'语音合成成功：{text}')
            else:
                self.get_logger().warn(f'语音合成失败：{text}')
        else:
            self.get_logger().warn('语音合成服务请求失败')
    # 根据x、y、yaw生成目标位姿
    def get_pose_by_xyyaw(self, x, y, yaw):
        # 创建PoseStamped对象
        pose = PoseStamped()
        # 设置坐标系
        pose.header.frame_id = 'map'
        # 设置位置
        pose.pose.position.x = x
        pose.pose.position.y = y
        # 欧拉角转四元数
        rotation_quat = quaternion_from_euler(0, 0, yaw)
        # 设置四元数姿态
        pose.pose.orientation.x = rotation_quat[0]
        pose.pose.orientation.y = rotation_quat[1]
        pose.pose.orientation.z = rotation_quat[2]
        pose.pose.orientation.w = rotation_quat[3]
        # 返回目标位姿
        return pose
    # 初始化机器人位姿
    def init_robot_pose(self):
        # 重新获取参数
        self.initial_point_ = self.get_parameter('initial_point').value
        # 设置机器人初始位姿
        # 相当于RViz里的2D Pose Estimate
        self.setInitialPose(self.get_pose_by_xyyaw(self.initial_point_[0], self.initial_point_[1], self.initial_point_[2]))
        # 等待Nav2激活
        self.waitUntilNav2Active()
    # 获取所有目标点
    def get_target_points(self):
        # 用于保存目标点列表
        points = []
        # 获取目标点参数
        self.target_points_ = self.get_parameter('target_points').value
        # 每3个数字表示一个目标点
        for index in range(int(len(self.target_points_) / 3)):
            # 获取x
            x = self.target_points_[index * 3]
            # 获取y
            y = self.target_points_[index * 3 + 1]
            # 获取yaw
            yaw = self.target_points_[index * 3 + 2]
            # 添加到目标点列表
            points.append([x, y, yaw])
            # 打印日志
            self.get_logger().info(f'获取到目标点: {index}->({x},{y},{yaw})')
        # 返回目标点列表
        return points
    # 导航到指定目标点
    def nav_to_pose(self, target_pose):
        # 等待Nav2激活
        self.waitUntilNav2Active()
        # 发送导航目标
        result = self.goToPose(target_pose)
        # 持续检查导航是否完成
        while not self.isTaskComplete():
            # 获取导航反馈
            feedback = self.getFeedback()
            # 如果收到反馈
            if feedback:
                # 打印预计剩余时间
                self.get_logger().info(f'预计: {Duration.from_msg(feedback.estimated_time_remaining).nanoseconds / 1e9} s 后到达')
        # 获取导航结果
        result = self.getResult()
        # 判断导航状态
        if result == TaskResult.SUCCEEDED:
            self.get_logger().info('导航结果：成功')
        elif result == TaskResult.CANCELED:
            self.get_logger().warn('导航结果：被取消')
        elif result == TaskResult.FAILED:
            self.get_logger().error('导航结果：失败')
        else:
            self.get_logger().error('导航结果：返回状态无效')
    # 获取机器人当前位姿
    def get_current_pose(self):
        # ROS2运行时持续循环
        while rclpy.ok():
            try:
                # 查询TF变换
                # map -> base_footprint
                tf = self.buffer_.lookup_transform('map', 'base_footprint', rclpy.time.Time(seconds=0), rclpy.time.Duration(seconds=1))
                # 获取变换数据
                transform = tf.transform
                # 四元数转欧拉角
                rotation_euler = euler_from_quaternion([transform.rotation.x, transform.rotation.y, transform.rotation.z, transform.rotation.w])
                # 打印当前位姿
                self.get_logger().info(f'平移:{transform.translation},旋转四元数:{transform.rotation},旋转欧拉角:{rotation_euler}')
                # 返回当前位姿
                return transform
            except Exception as e:
                # TF查询失败时打印警告
                self.get_logger().warn(f'不能获取坐标变换，原因: {str(e)}')
# 主函数
def main():
    # 初始化ROS2
    rclpy.init()
    # 创建巡逻节点
    patrol = PatrolNode()
    # 播报初始化语音
    patrol.speach_text(text='正在初始化位置')
    # 初始化机器人位姿
    patrol.init_robot_pose()
    # 播报初始化完成
    patrol.speach_text(text='位置初始化完成')
    # ROS2运行时循环执行
    while rclpy.ok():
        # 遍历所有目标点
        for point in patrol.get_target_points():
            # 获取目标点参数
            x, y, yaw = point[0], point[1], point[2]
            # 生成目标位姿
            target_pose = patrol.get_pose_by_xyyaw(x, y, yaw)
            # 播报准备导航
            patrol.speach_text(text=f'准备前往目标点{x},{y}')
            # 开始导航
            patrol.nav_to_pose(target_pose)
            # 到达后播报
            patrol.speach_text(text=f'已到达目标点{x},{y},准备记录图像')
            # 保存图像
            patrol.record_image()
            # 播报图像保存完成
            patrol.speach_text(text='图像记录完成')
    # 关闭ROS2
    rclpy.shutdown()
# Python程序入口
if __name__ == '__main__':
    # 执行主函数
    main()