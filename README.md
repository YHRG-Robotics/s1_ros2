# 意海融硅 S1 机械臂 ROS2 支持

>🤖 本 SDK 提供基于 ROS2 humble 版本的 S1 机械臂控制与状态读取接口，包含moveit规划与gazebo仿真。

---
## 使用准备
- 需提前安装S1本体机械臂SDK，参考[这里](https://github.com/YHRG-Robotics/S1_SDK)
---

---
## 系统要求

| 操作系统     | ROS 2 版本 | 说明       |
|------------|------------|------------|
| Ubuntu 22.04 | Humble    | ✅ 推荐    |
---

---
## 安装依赖

### 1. 安装 ROS 2（以 Humble 为例）
- 推荐小鱼ros一键安装，选择安装ros2 humble版本
```bash
wget http://fishros.com/install -O fishros && . fishros
```

### 2. 安装 MoveIt2

```bash
sudo apt update
sudo apt install ros-humble-moveit

sudo apt install ros-humble-joint-trajectory-controller \
                 ros-humble-joint-state-controller \
                 ros-humble-joint-state-broadcaster \
                 ros-humble-controller-manager \
                 ros-humble-gripper-controllers \
                 ros-humble-trajectory-msgs
```


### 3. 安装 Gazebo

```bash
sudo apt install gazebo ros-humble-gazebo-ros-pkgs
```

## 项目结构

```
.
├── src/
│   ├── s1_description/          # 机械臂 URDF 模型描述
│   │   └── urdf/
│   │       ├── s1_description_with_gripper.urdf    # 带夹爪的模型
│   │       └── s1_description_no_gripper.urdf      # 无夹爪的模型
│   │
│   ├── s1_sdk/                  # C++ SDK 控制节点
│   │   ├── src/
│   │   │   ├── arm_node.cpp     # 机械臂控制节点实现
│   │   │   └── main.cpp         # 主程序入口
│   │   └── launch/
│   │       └── s1_sdk.launch.py # SDK 启动文件
│   │
│   ├── s1_python/               # Python 控制节点
│   │   └── s1_python/
│   │       └── s1_python.py     # Python 机械臂控制实现
│   │
│   ├── s1_gazebo/               # Gazebo 仿真支持
│   │   ├── launch/
│   │   │   ├── s1_with_gripper/
│   │   │   │   └── s1_gazebo.launch.py      # 带夹爪仿真启动
│   │   │   └── s1_no_gripper/
│   │   │       └── s1_no_gripper_gazebo.launch.py  # 无夹爪仿真启动
│   │   └── scripts/
│   │       └── joint8_ctrl.py   
│   │
│   ├── s1_moveit2/              # MoveIt2 运动规划配置
│      ├── s1_moveit_with_gripper/    # 带夹爪配置
│      │   ├── config/
│      │   │   └── s1_description.urdf.xacro
│      │   └── launch/
│      │       ├── demo.launch.py
│      │       └── s1_moveit.launch.py
│      │
│      └── s1_moveit_no_gripper/      # 无夹爪配置
│          ├── config/
│          │   └── s1_description.urdf.xacro
│          └── launch/
│              ├── demo.launch.py
│              └── s1_moveit.launch.py
│
└── README.md                    # 本文件
```

## 消息接口说明

### 控制类 Topic

| Topic | 类型 | 说明 |
|------|------|------|
| `/s1/enable_status` | `std_msgs.msg/Bool` | SDK 使能/失能机械臂 |
| `/s1/joint_cmd` | `sensor_msgs/msg/JointState` | SDK 关节角度控制指令 |
| `/s1/gripper_cmd` | `control_msgs/msg/GripperCommand` | SDK 夹爪控制 |
| `/s1/pose_cmd` | `geometry_msgs/msg/Pose` | SDK 末端位置控制 |

### 状态类 Topic

| Topic | 类型 | 说明 |
|------|------|------|
| `/s1/joint_states` | `sensor_msgs/msg/JointState` | 所有关节位置，速度，力矩 |
| `/s1/end_pose` | `geometry_msgs/msg/Pose` | 机械臂末端位姿 |

### Action 接口

| Action | 类型 | 说明 |
|------|------|------|
| `control_msgs/action/FollowJointTrajectory` | `/arm_controller/follow_joint_trajectory` | 关节轨迹执行 Action 接口 |

---

## 编译与运行

### 1. 编译工作区

```bash
cd ~/s1_ros2
colcon build
source install/setup.bash
```

### 2. 启动机械臂节点

#### 连接机械臂
- 注意接口连接，修改位置在src/s1_python/s1_python/s1_python.py
- 给予权限
```bash
sudo chmod 777 /dev/ttyUSB0
```

```bash
self.arm = S1_arm(mode=control_mode.only_sim,dev="/dev/ttyUSB0",end_effector="gripper")
```

```bash
ros2 launch s1_python launch.py
```

#### 快速测试

在终端中依次执行以下命令即可控制机械臂：

#### 使能机械臂

```bash
ros2 topic pub /s1/enable_status std_msgs/msg/Bool "{data: true}" -1
```

#### 失能机械臂

```bash
ros2 topic pub /s1/enable_status std_msgs/msg/Bool "{data: false}" -1
```

#### 发送关节控制指令

```bash
ros2 topic pub /s1/joint_cmd sensor_msgs/msg/JointState \
"{position: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]}" -1
```

#### 发布末端位姿指令
- 一定要注意求解的结果，尤其在近原点处求解的突变，使用注意安全，可以先仿真或者SDK查看求解结果
```bash
ros2 topic pub --once /s1/pose_cmd geometry_msgs/msg/Pose "
position:
  x: -0.2
  y: 0.0
  z: 0.3
orientation:
  x: 0.5
  y: -0.5
  z: -0.5
  w: 0.5
"
```

#### 发送夹爪控制指令

```bash
ros2 topic pub /s1/gripper_cmd control_msgs/msg/GripperCommand \
"{position: 0.0, max_effort: 0.5}" -1
```


#### 查看实时反馈

```bash
# 查看所有关节位置
ros2 topic echo /s1/joint_states

# 查看末端位姿
ros2 topic echo /s1/end_pose

```

---

### 3. 启动 Gazebo 仿真

**带夹爪版本：**
```bash
ros2 launch s1_gazebo s1_gazebo.launch.py 
```

**无夹爪版本：**
```bash
ros2 launch s1_gazebo s1_no_gripper_gazebo.launch.py
```

### 4. 启动 MoveIt2
注意：
- 若此前已经启动了实体机械臂节点并使能机械臂，此时执行以下脚本后，点击plan & execute实体机械臂会运动

**带夹爪版本：**
```bash
ros2 launch s1_moveit_with_gripper demo.launch.py

# 若要与gazebo联动，执行
ros2 launch s1_moveit_with_gripper s1_moveit.launch.py
```

**无夹爪版本：**
```bash
ros2 launch s1_moveit_no_gripper demo.launch.py

# 若要与gazebo联动，执行
ros2 launch s1_moveit_no_gripper s1_moveit.launch.py
```

---

## 注意事项

1. 使用真实机械臂前，请确保通信接口正确配置
2. 首次使用前建议先在 Gazebo 仿真环境中测试
3. 执行运动规划时，请确保机械臂周围无障碍物
4. 使用夹爪时，注意调整夹持力度，避免损坏物体

---
