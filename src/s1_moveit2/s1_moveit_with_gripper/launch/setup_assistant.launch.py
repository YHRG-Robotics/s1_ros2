from moveit_configs_utils import MoveItConfigsBuilder
from moveit_configs_utils.launches import generate_setup_assistant_launch


def generate_launch_description():
    moveit_config = MoveItConfigsBuilder("S1_urdf", package_name="s1_moveit_with_gripper").to_moveit_configs()
    return generate_setup_assistant_launch(moveit_config)
