from launch import LaunchDescription
from launch_ros.actions import Node
import os

from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    pkg_share = get_package_share_directory('s1_python')

    config_file = os.path.join(pkg_share, 'config', 'config.yaml')

    return LaunchDescription([
        Node(
            package='s1_python',              # 包名
            executable='s1_python',             # setup.py 中 console_scripts 名称
            name='s1_python_publisher',              # 节点名
            output='screen',
            parameters=[config_file],           # 加载参数文件
        )
    ])