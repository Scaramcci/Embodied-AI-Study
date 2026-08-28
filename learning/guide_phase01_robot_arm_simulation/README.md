# 阶段一：机械臂仿真与可执行轨迹

本目录用于配合 `Embodied-AI-Guide-main` 完成机械臂仿真巩固。当前使用
PyBullet 自带的 KUKA LBR iiwa（7 自由度）作为统一实验对象。

## 当前任务：Unit 1——关节、连杆与运动链

你已经完成 GUI smoke test，并确认：

- 机器人共有 7 个可动关节，全部是 revolute joint；
- 关节索引按 `[0, 1, 2, 3, 4, 5, 6]` 排列；
- joint 0 的 child link 是 `lbr_iiwa_link_1`；
- 当前使用的末端 link 是 `lbr_iiwa_link_7`，link index 为 `6`。

下一步通过滑块分别改变 7 个关节，建立对串联机械臂运动链的直观认识。

## 运行方法

在 Miniconda Prompt 或已初始化 conda 的 PowerShell 中执行：

```powershell
conda activate robotics
cd "C:\A_Academic\具身智能\Embodied-AI-Study"
python learning\guide_phase01_robot_arm_simulation\src\unit01_joint_sliders.py
```

运行后，PyBullet 窗口的调试面板中会出现 7 个关节滑块。程序终端会打印
关节表和末端 link 信息。关闭 GUI 窗口或在终端按 `Ctrl+C` 即可退出。

## 本次观察任务

按顺序完成下面的操作，每次观察后把滑块恢复到 `0`：

1. 缓慢移动 `joint_1 (index 0)`，观察它后面的机械臂是否整体随之运动。
2. 移动 `joint_4 (index 3)`，比较它与 joint 1 所影响的连杆范围。
3. 移动 `joint_7 (index 6)`，观察最后一节的变化。它绕自身轴旋转时，外形变化可能不明显，但末端坐标系的姿态仍然改变。
4. 同时设置两个关节，观察机械臂最终姿态是多个关节变换逐级累积的结果。

重点先记住一条规则：在串联运动链中，改变某个关节会影响该关节的 child
link 以及其后的所有后代 link，不会改变它之前的祖先 link。

## 完成标准

完成滑块实验后，你应该能用自己的话回答：

1. 为什么 joint 1 通常比 joint 7 影响的连杆更多？
2. joint index 和 child link 之间是什么关系？
3. 为什么 `lbr_iiwa_link_7` 可作为当前模型的末端 link？

暂时不要求推导变换矩阵；下一步会在 Unit 2 中把这些观察转成坐标系与齐次变换。

## Unit 2 脚本

- `src/unit02_pose_and_frames.py`：在 GUI 中观察世界坐标系、末端坐标系和实时位姿。
- `src/unit02_fk_cases.py`：生成三组 `q -> wrist pose`，并演示角度单位和四元数顺序错误。
- `src/unit02_pose_error.py`：分别计算位置与姿态误差，并用任务阈值判定是否通过。

## Unit 3 脚本

- `src/unit03_ik_validation.py`：比较位置 IK、完整位姿 IK 与不可达目标，并使用 FK 和关节限位验证候选解。
- `src/unit03_redundancy_and_limits.py`：对同一目标使用不同 rest pose，比较冗余 IK 解和关节限位余量。
- `src/unit03_workspace_boundary.py`：把位置目标逐步推向工作空间边界，用 FK 误差识别可达与不可达目标。

## Unit 4 脚本

- `src/unit04_trajectory_ik.py`：对合成腕部轨迹逐帧求 IK，记录 FK 误差、失败帧和相邻帧关节变化。
- `src/unit04_failed_waypoints.py`：构造越过工作空间边界的轨迹，保留失败帧及其原始时间索引。

## Unit 5 脚本

- `src/unit05_smoothing_metrics.py`：比较原始与平滑关节轨迹的 FK 误差、速度和加速度。
- `src/unit05_position_control.py`：用位置控制以正常和四倍速度执行同一轨迹，比较 target/actual 跟踪误差。

## Unit 6 脚本

- `src/unit06_build_report.py`：整合 Unit 4–5 的可达、失败、平滑和控制实验，生成论文式 Markdown/JSON 报告。
