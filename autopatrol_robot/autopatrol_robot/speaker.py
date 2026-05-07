# 导入ROS2 Python客户端库
import rclpy
# 导入ROS2节点基类
from rclpy.node import Node
# 导入自定义语音服务接口
from autopatrol_interfaces.srv import SpeachText
# 导入espeak-ng语音合成库
import espeakng
# 定义语音播报节点类
# 继承ROS2 Node节点
class Speaker(Node):
    # 构造函数
    def __init__(self, node_name):
        # 调用父类构造函数
        # 创建ROS2节点
        super().__init__(node_name)
        # 创建ROS2服务
        # 服务类型：SpeachText
        # 服务名称：speech_text
        # 回调函数：speak_text_callback
        self.speech_service = self.create_service(SpeachText,'speech_text',self.speak_text_callback)
        # 创建espeak-ng语音播报对象
        self.speaker = espeakng.Speaker()
        # 设置语音类型为中文
        self.speaker.voice = 'zh'
    # 服务回调函数
    # 当收到语音请求时自动执行
    def speak_text_callback(self, request, response):
        # 在终端打印收到的文本
        self.get_logger().info('正在朗读 %s' % request.text)
        # 调用espeak-ng开始语音播报
        self.speaker.say(request.text)
        # 等待语音播放完成
        self.speaker.wait()
        # 设置服务返回结果为True
        # 表示语音播放成功
        response.result = True
        # 返回服务响应
        return response
# 主函数
def main(args=None):
    # 初始化ROS2
    rclpy.init(args=args)
    # 创建语音节点
    node = Speaker('speaker')
    # 保持节点运行
    # 持续等待服务请求
    rclpy.spin(node)
    # 关闭ROS2
    rclpy.shutdown()
# Python程序入口
if __name__ == '__main__':
    # 执行主函数
    main()