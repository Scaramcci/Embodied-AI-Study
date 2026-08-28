# Phase 1 阶段总结：机械臂仿真与可执行轨迹

> 完成日期：2026-08-28  
> 阶段状态：已完成  
> 学习对象：KUKA LBR iiwa 7-DoF 机械臂  
> 仿真环境：PyBullet（Windows + CPU）  
> 论文出口：DexTele / ObjRetarget 的手臂重定向 baseline

## 1. 阶段目标与结论

本阶段围绕一个核心问题展开：

> 给定一段参考腕部位姿序列，怎样生成合法、连续、可验证并能够在仿真中执行的机器人关节轨迹？

最终建立了以下完整闭环：

```text
reference wrist pose sequence
    -> frame / unit / quaternion convention check
    -> frame-wise IK candidates
    -> FK validation
    -> reachability / joint-limit / failure checks
    -> joint-trajectory smoothing
    -> position-control rollout
    -> position / orientation / velocity / acceleration / tracking metrics
    -> reproducible report
```

阶段 Gate 已通过。现在能够区分并连接以下变量：

- 人体或任务提供的 reference wrist pose；
- IK 返回的候选关节角 `q_candidate`；
- FK 计算的机器人末端 wrist pose；
- position control 的目标关节状态 `q_target`；
- 仿真中实际产生的关节状态 `q_actual`；
- 运动学误差、时间平滑性和控制跟踪误差。

## 2. 环境与固定机器人配置

实际使用 Conda 环境：`robotics`

| 组件 | 版本 / 配置 |
|---|---|
| Python | 3.11.16 |
| PyBullet | 3.2.5 |
| NumPy | 2.4.6 |
| SciPy | 1.17.1 |
| Matplotlib | 3.11.1 |
| pytest | 9.1.1 |
| BLAS/LAPACK | OpenBLAS |
| 机器人 | `kuka_iiwa/model.urdf` |
| 可动关节 | 7 个 revolute joint |
| joint order | `[0, 1, 2, 3, 4, 5, 6]` |
| end-effector link | `lbr_iiwa_link_7`，link index `6` |

原 MKL 组合在当前 Windows 环境中无法加载 `numpy.linalg` 所需 DLL，已切换到 OpenBLAS；NumPy 线性代数与 Matplotlib 绘图均已恢复。

## 3. 六个 Unit 的学习成果

### Unit 1：关节、连杆与运动链

- 从 PyBullet/URDF 接口读取 joint type、joint index、child link 和关节限位；
- 确认串联运动链中，一个关节影响其 child link 及全部后代 link；
- 建立固定 joint order 与 end-effector 配置；
- 使用 GUI sliders 观察 joint 1、joint 4、joint 7 的影响范围。

核心结论：机器人拓扑决定关节变量如何映射到连杆运动，也是跨机器人动作重定向的结构基础。

### Unit 2：坐标系、旋转表示与 FK

- 区分 world、base 和 end-effector frame；
- 读取 position、quaternion、Euler RPY 和齐次变换；
- 理解 `world_T_link7 = [R, p; 0, 1]` 的语义；
- 掌握 PyBullet 四元数顺序 `xyzw`；
- 区分关节空间 `q` 与任务空间 wrist pose；
- 分别计算位置误差和最短旋转角误差。

核心结论：position 描述末端在哪里，orientation 描述末端朝向；二者共同组成 pose，但必须分别评价误差。

### Unit 3：IK、可达性与 FK 回代

- 比较 position-only IK 与 position+orientation IK；
- 理解 7-DoF 机械臂的冗余性：不同 `q` 可以产生近似相同的完整末端位姿；
- 理解 `restPoses` 是冗余 IK 的软姿态偏好；
- 使用 FK 回代、位置/姿态阈值和 joint limits 验证候选解；
- 比较正常、工作空间边界和不可达目标。

核心结论：`IK()` 返回数组只代表得到候选解，不代表目标可达或求解成功。

### Unit 4：从单点 IK 到参考腕部轨迹

- 生成 121 帧、3 cm 半径的合成腕部圆形轨迹；
- 逐帧求 IK，形成 `q[T, 7]`；
- 比较固定零位偏好和上一帧关节解偏好；
- 计算相邻帧变化 `||q[t]-q[t-1]||`；
- 构造越过工作空间边界的轨迹；
- 显式保留失败帧、候选解、误差和原始 frame index。

核心结论：每帧 IK/FK 成功不保证整段轨迹自然；失败帧不能静默删除，否则时间轴、速度和加速度都会失真。

### Unit 5：平滑、时间指标与 position control

- 为关节轨迹建立固定 60 Hz timestamp；
- 使用 Savitzky–Golay 滤波比较原始与平滑轨迹；
- 计算关节速度和加速度；
- 在 240 Hz PyBullet 物理步下执行 position control；
- 记录 `q_target`、`q_actual` 与 tracking error；
- 比较同一几何轨迹的 2 秒与 0.5 秒执行。

核心结论：几何上平滑、运动学上可达的路径，仍可能因时间尺度过快而无法被控制器准确跟踪。

### Unit 6：论文导向综合实验

- 汇总输入 shape、frame、unit、timestamp 和 quaternion order；
- 汇总 IK/FK 成功率、position/orientation error 与 joint-limit violation；
- 汇总原始/平滑轨迹的速度和加速度；
- 汇总正常/快速 position-control rollout；
- 同时报告可达成功案例、不可达案例和不平滑/边界案例；
- 生成 Markdown 报告和机器可读 JSON 指标。

核心结论：一个可信的重定向 baseline 必须同时保存输入约定、成功结果、失败结果和可复现命令。

## 4. 关键实验结果

### 4.1 可达圆形腕部轨迹

| 指标 | 结果 |
|---|---:|
| 总帧数 | 121 |
| IK/FK 成功帧 | 121 / 121 |
| 最大位置误差 | 0.2025 mm（previous-solution 策略） |
| 最大姿态误差 | 0.0048 deg |
| 最大相邻关节变化 | 0.009415 rad |
| joint-limit violation | 0 帧 |

### 4.2 工作空间边界与失败帧

| 指标 | 结果 |
|---|---:|
| 总帧数 | 121 |
| 失败帧 | 76 |
| 最大位置误差 | 202.676 mm |
| 最大相邻关节变化 | 0.220102 rad |
| 删除失败帧后的最大原始时间缺口 | 76 帧 |

该实验验证了：不可达目标仍可能得到数值 IK 候选关节角；必须通过 FK 误差和 success mask 识别失败。

### 4.3 原始轨迹与平滑轨迹

| 指标 | 原始 | 平滑后 |
|---|---:|---:|
| 最大 FK 位置误差 | 32.8187 mm | 8.7097 mm |
| 最大速度范数 | 2.4346 rad/s | 0.8830 rad/s |
| 最大加速度范数 | 126.4591 rad/s² | 14.0607 rad/s² |

平滑显著降低速度和加速度，但平滑后的最大任务误差仍高于 5 mm，因此平滑后必须重新执行 FK 与限位验证。

### 4.4 正常与快速执行

| 指标 | 2 秒执行 | 0.5 秒执行 |
|---|---:|---:|
| 最大 joint tracking error | 0.005945 rad | 0.031319 rad |
| 平均 joint tracking error | 0.003427 rad | 0.020963 rad |
| 最大末端位置误差 | 1.9762 mm | 9.1352 mm |
| 最大实际速度范数 | 0.8258 rad/s | 2.6218 rad/s |

快速执行的最大关节误差约为正常执行的 5.3 倍，并使末端误差超过 5 mm 阈值。

## 5. 已形成的判断框架

### 单帧 IK 成功条件

```text
position_error < position_threshold
AND orientation_error < orientation_threshold（完整位姿任务）
AND lower_limits <= q_candidate <= upper_limits
```

### 整段轨迹质量

```text
per-frame IK/FK success
+ failed-frame mask
+ ||q[t] - q[t-1]||
+ joint velocity / acceleration
+ joint-limit margin
```

### 控制执行质量

```text
q_target vs q_actual
+ end-effector target vs actual
+ fixed timestep / timestamps
+ normal-speed vs fast-speed rollout
```

这三层分别对应：运动学正确性、时间平滑性和物理执行跟踪，不能互相替代。

## 6. 与 DexTele / ObjRetarget 的关系

本阶段形成的是两篇论文共享的手臂重定向 baseline：

```text
human/reference wrist pose
    -> robot arm q
    -> FK wrist pose
    -> retargeting error
    -> smooth joint trajectory
    -> simulated execution and tracking metrics
```

现在可以带着以下问题阅读论文：

- 论文的 wrist/reference pose 位于哪个 frame，单位和四元数顺序是什么？
- 重定向输出是单帧关节角还是整段轨迹？
- 多个冗余解之间如何选择，是否包含上一帧、自然姿态或 arm-plane 偏好？
- position、orientation、smoothness 和 joint-limit loss 如何加权？
- 论文报告的是 IK/FK 误差、控制 tracking error，还是任务成功率？
- 失败帧、不可达目标和控制延迟如何处理？

这些问题将在 Phase 2 的感知表示和 Phase 3 的动作重定向/轨迹优化中继续展开。

## 7. 证据与主要产物

### 核心代码

- `src/unit01_joint_sliders.py`
- `src/unit02_pose_and_frames.py`
- `src/unit03_ik_validation.py`
- `src/unit04_trajectory_ik.py`
- `src/unit04_failed_waypoints.py`
- `src/unit05_smoothing_metrics.py`
- `src/unit05_position_control.py`
- `src/unit06_build_report.py`

### 图表与报告

- `outputs/unit04_trajectory_summary.png`
- `outputs/unit04_failed_waypoints.png`
- `outputs/unit05_smoothing_metrics.png`
- `outputs/unit05_position_control.png`
- `outputs/unit06_integrated_report.md`
- `outputs/unit06_integrated_metrics.json`

## 8. 可复现命令

```powershell
conda activate robotics
cd "C:\A_Academic\具身智能\Embodied-AI-Study"

python learning\guide_phase01_robot_arm_simulation\src\unit04_trajectory_ik.py
python learning\guide_phase01_robot_arm_simulation\src\unit04_failed_waypoints.py
python learning\guide_phase01_robot_arm_simulation\src\unit05_smoothing_metrics.py
python learning\guide_phase01_robot_arm_simulation\src\unit05_position_control.py
python learning\guide_phase01_robot_arm_simulation\src\unit06_build_report.py
```

## 9. 当前边界与未覆盖内容

本阶段有意保持论文主线所需的最小范围，尚未覆盖：

- 自碰撞和环境碰撞检测；
- 动力学力矩、能耗和电机真实规格；
- 轨迹级约束优化和严格的速度/加速度上限；
- 真实机器人标定、通信、延迟和安全控制；
- ROS 2、MoveIt、Isaac Sim 或真实硬件驱动；
- 人体、手部、物体和相机数据接口；
- arm-plane、手物接触、灵巧手与力调节。

这些内容不会阻碍进入 Phase 2。碰撞与轨迹级约束将在任务需要时补充，感知表示、arm-plane 和手物关系分别属于后续阶段主线。

## 10. 阶段 Gate 结论与下一步

Phase 1 Gate：**通过**。

下一阶段是 Phase 2：人体、手部与物体感知表示。重点从“机器人怎样执行腕部参考轨迹”转向“参考轨迹从哪里来、使用什么 frame/shape/unit 表示，以及感知误差怎样传递到重定向”。

在开始 Phase 2 前，应先根据两篇目标论文进一步收缩感知学习范围，再创建 Phase 2 的详细计划和独立环境配置；不提前安装大型视觉模型或真实硬件依赖。

