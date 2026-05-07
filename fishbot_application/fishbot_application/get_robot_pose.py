# 实时监听 map → base_footprint 坐标变换（机器人在地图中的实时位姿）
# 导入ROS2 Python核心库
import rclpy
# 导入ROS2节点基类
from rclpy.node import Node
# 导入TF2坐标变换监听相关类
from tf2_ros import TransformListener, Buffer
# 导入四元数转欧拉角的工具函数
from tf_transformations import euler_from_quaternion

# 定义TF监听节点类，继承Node
class TFListener(Node):
    # 构造函数
    def __init__(self):
        # 调用父类构造函数，节点名称为tf2_listener
        super().__init__('tf2_listener')
        # 创建TF缓存，存储坐标变换数据
        self.buffer = Buffer()
        # 创建TF监听器，订阅TF话题并将数据存入缓存
        self.listener = TransformListener(self.buffer, self)
        # 创建定时器，每隔1秒执行一次get_transform函数
        self.timer = self.create_timer(1, self.get_transform)

    # 获取坐标变换的回调函数
    def get_transform(self):
        try:
            # 查找map到base_footprint的坐标变换，超时时间1秒
            tf = self.buffer.lookup_transform('map', 'base_footprint', rclpy.time.Time(seconds=0), rclpy.time.Duration(seconds=1))
            # 提取坐标变换数据（平移+旋转）
            transform = tf.transform
            # 将四元数姿态转换为欧拉角（roll,pitch,yaw）
            rotation_euler = euler_from_quaternion([transform.rotation.x,transform.rotation.y,transform.rotation.z,transform.rotation.w])
            # 打印输出平移、四元数、欧拉角信息
            self.get_logger().info(f'平移:{transform.translation},旋转四元数:{transform.rotation}:旋转欧拉角:{rotation_euler}')
        # 捕获获取坐标变换失败的异常
        except Exception as e:
            # 打印警告信息
            self.get_logger().warn(f'不能够获取坐标变换，原因: {str(e)}')

# 主函数
def main():
    # 初始化ROS2 Python上下文
    rclpy.init()
    # 创建TF监听节点实例
    node = TFListener()
    # 循环运行节点，处理回调
    rclpy.spin(node)
    # 关闭ROS2
    rclpy.shutdown()

# 程序入口
if __name__ == '__main__':
    main()