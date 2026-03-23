import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool
from sensor_msgs.msg import JointState
from control_msgs.msg import GripperCommand
from geometry_msgs.msg import Pose, PoseStamped
from rclpy.action import ActionServer
from control_msgs.action import FollowJointTrajectory

import threading
import time

from S1_SDK import S1_arm,control_mode,S1_slover

class S1_python_Publisher(Node):
    def __init__(self):
        super().__init__('s1_python_publisher')
        self._logger.info('S1_python_Publisher 节点已初始化')
        self.arm = S1_arm(mode=control_mode.only_real,dev="/dev/ttyUSB0",end_effector="gripper")
        self.solver = S1_slover([0.0,0.0,0.0])

        # ================= Publisher =================
        self.joint_pub = self.create_publisher(JointState, 's1/joint_states', 10)
        self.end_pose_pub = self.create_publisher(PoseStamped, 's1/end_pose', 10)

        # ================= Subscriber =================
        self.create_subscription(JointState, 's1/joint_cmd', self.joint_callback, 10)
        self.create_subscription(GripperCommand, 's1/gripper_cmd', self.gripper_callback, 10)
        self.create_subscription(Pose, 's1/pose_cmd', self.pose_callback, 10)
        self.create_subscription(Bool, 's1/enable_status', self.enable_callback, 10)

        # ================= Action Server =================
        self._action_server = ActionServer(self,FollowJointTrajectory,'/arm_controller/follow_joint_trajectory',self.arm_execute_callback)

        # Joint msg
        self.joint_names = [
            '1joint', '2joint', '3joint',
            '4joint', '5joint', '6joint'
        ]

        if self.arm.end_effector == "gripper":
            self.joint_names.append('gripper_joint')

        self.joint_msg = JointState()
        self.joint_msg.name = self.joint_names

        # 启动线程
        self.publisher_thread = threading.Thread(target=self.publish_loop)
        self.publisher_thread.daemon = True
        self.publisher_thread.start()

        self.get_logger().info("S1 ROS2 Node Started")

    # =====================================================
    # 发布循环
    # =====================================================
    def publish_loop(self):
        rate = self.create_rate(100)

        while rclpy.ok():
            # 读取关节状态
            pos = self.arm.get_pos()
            tau = self.arm.get_tau()
            vel = self.arm.get_vel()

            if pos is not None:

                self.joint_msg.header.stamp = self.get_clock().now().to_msg()
                self.joint_msg.position = list(pos)
                # self.joint_msg.position.append(0.0)
                self.joint_msg.effort = list(tau)
                self.joint_msg.velocity = list(vel)

                self.joint_pub.publish(self.joint_msg)

                # FK 计算末端位姿
                fk = self.solver.forward_quat(pos[:6])

                if fk is not None:
                    x, y, z, qx, qy, qz, qw = fk

                    pose_msg = PoseStamped()
                    pose_msg.header.stamp = self.joint_msg.header.stamp

                    pose_msg.pose.position.x = float(x)
                    pose_msg.pose.position.y = float(y)
                    pose_msg.pose.position.z = float(z)

                    pose_msg.pose.orientation.x = float(qx)
                    pose_msg.pose.orientation.y = float(qy)
                    pose_msg.pose.orientation.z = float(qz)
                    pose_msg.pose.orientation.w = float(qw)

                    self.end_pose_pub.publish(pose_msg)

            rate.sleep()

    # =====================================================
    # Joint 控制回调
    # =====================================================
    def joint_callback(self, msg: JointState):
        if len(msg.position) < 6:
            return

        target = list(msg.position[:6])
        self.get_logger().info(f"Joint cmd: {target}")
        self.arm.joint_control(target)
    
    def gripper_callback(self, msg):
        pos = msg.position
        effort = msg.max_effort
        self.arm.control_gripper(pos, effort)

    # =====================================================
    # 笛卡尔控制回调
    # =====================================================
    def pose_callback(self, msg: Pose):

        x = msg.position.x
        y = msg.position.y
        z = msg.position.z

        qx = msg.orientation.x
        qy = msg.orientation.y
        qz = msg.orientation.z
        qw = msg.orientation.w

        self.get_logger().info(f"Pose cmd: {x:.3f},{y:.3f},{z:.3f}")

        ik_sol = self.solver.inverse_quat([x, y, z, qx, qy, qz, qw])
        if ik_sol is not None:
            self.get_logger().info(f"Pose sol: {[f'{x:.2f}' for x in ik_sol]}")
            self.arm.joint_control(ik_sol)

        # self.arm.end_effector_control([x, y, z, qx, qy, qz, qw])

    # =====================================================
    # Enable 回调
    # =====================================================
    def enable_callback(self, msg: Bool):
        if msg.data:
            self.get_logger().info("Enable arm")
            self.arm.enable()
        else:
            self.get_logger().info("Disable arm")
            self.arm.disable()

    def arm_execute_callback(self, goal_handle):
        self.get_logger().info('收到 MoveIt 执行请求，开始驱动 SDK...')
        
        trajectory = goal_handle.request.trajectory
        joint_names = trajectory.joint_names
        points = trajectory.points

        # 结果对象
        result = FollowJointTrajectory.Result()

        try:
            last_time = 0.0
            for i, point in enumerate(points):
                # 检查 Action 是否被取消
                if goal_handle.is_cancel_requested:
                    goal_handle.canceled()
                    self.get_logger().info('动作被取消')
                    return result

                # 提取位置
                pos_list = list(point.positions)
                
                # 计算与上一个点之间的时间间隔
                current_time = point.time_from_start.sec + point.time_from_start.nanosec * 1e-9
                sleep_time = current_time - last_time
                if sleep_time > 0:
                    time.sleep(sleep_time)
                last_time = current_time

                self.arm.refresh()
                self.arm.joint_control(pos_list)

                js_msg = JointState()
                js_msg.header.stamp = self.get_clock().now().to_msg()
                js_msg.name = joint_names            # MoveIt 发来的关节顺序
                js_msg.position = pos_list            # 关节位置
                js_msg.velocity = list(point.velocities) if point.velocities else []
                js_msg.effort = []

                if i % 10 == 0: # 减少日志打印频率
                    self.get_logger().info(f'正在执行: 点 {i}/{len(points)}')

            # 执行成功
            goal_handle.succeed()
            result.error_code = FollowJointTrajectory.Result.SUCCESSFUL
            self.get_logger().info('轨迹执行完毕！')

        except Exception as e:
            self.get_logger().error(f'执行过程中出现错误: {str(e)}')
            result.error_code = FollowJointTrajectory.Result.PATH_TOLERANCE_VIOLATED
            goal_handle.abort()

        return result

# ---------------- 主函数 ----------------
def main(args=None):
    rclpy.init(args=args)
    node = S1_python_Publisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.arm.disable()
        node.destroy_node()
        rclpy.shutdown()
