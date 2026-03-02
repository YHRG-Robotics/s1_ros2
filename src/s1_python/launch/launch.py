from launch import LaunchDescription
from launch_ros.actions import Node
import os

from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    # 有问题，执行的代码是install目录下的，更改config不起效
    # 获取包共享路径
    # pkg_share = get_package_share_directory('camera')
    # # 配置文件路径
    # config_file = os.path.join(pkg_share, 'config', 'config.yaml')

    # 绝对路径
    # workspace_dir = os.path.expanduser('~/workspace/ros2_ws')
    # config_file = os.path.join(workspace_dir, 'src', 'camera', 'config', 'config.yaml')

    # 根据install往上查找配置文件路径
    this_dir = os.path.dirname(os.path.realpath(__file__))
    # 基于 launch.py 路径，找到 src/camera/config/config.yaml
    config_file = os.path.abspath(os.path.join(
        this_dir, '..', '..', '..', '..', '..', 'src', 's1_python', 'config', 'config.yaml'
    ))
    print(f"config_file: {config_file}")
    # 检查文件是否存在
    if not os.path.exists(config_file):
        raise RuntimeError(f"Config file not found: {config_file}")

    return LaunchDescription([
        Node(
            package='s1_python',              # 包名
            executable='s1_python',             # setup.py 中 console_scripts 名称
            name='s1_python_publisher',              # 节点名
            output='screen',
            parameters=[config_file],           # 加载参数文件
        )
    ])