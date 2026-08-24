# Phase 1：机械臂仿真与可执行轨迹

> 状态：待开始  
> 前置条件：已读完《机器人学简介》  
> 建议用时：6 次学习，每次 60–90 分钟  
> 实验栈：Python + PyBullet + NumPy + SciPy + Matplotlib + pytest  
> 论文出口：为 DexTele/ObjRetarget 的手臂重定向与轨迹评测建立可运行直觉

## 1. 阶段核心问题

给定一段人体腕部参考位姿序列，怎样生成合法、平滑、可验证的机器人关节轨迹？

```text
reference wrist pose sequence
    -> frame/unit/convention check
    -> IK candidate trajectory
    -> FK validation
    -> joint-limit/reachability/collision check
    -> smoothing and position-control execution
    -> position/orientation/velocity/acceleration evaluation
```

完成后，应能理解两篇论文中以下变量为何不是一回事：

- 人体肩、肘、腕的三维位置与方向；
- 机器人末端参考位姿；
- IK 或重定向得到的机器人关节角；
- 仿真中的实际关节状态和末端位姿；
- 轨迹误差、平滑性与任务可执行性。

## 2. 与论文的直接联系

### DexTele

- URDF/机器人拓扑决定图结构和可控关节；
- FK 将机器人关节角转换为末端及其他关节位置；
- `L_ee`、`L_ori`、`L_norm` 和 dynamics/smoothness 项都依赖正确的运动学与轨迹表示；
- MPJPE、Quat、VE、AE 分别检查空间精度、方向精度和时间平滑性；
- 手臂关节角最终通过位置控制执行，不能把网络输出自动视为安全轨迹。

### ObjRetarget

- 初始重定向提供可行轨迹先验；
- wrist task loss 同时约束位置和 SO(3) 方向；
- arm-plane regularization 使用肩—肘—腕几何改善自然性；
- joint limit 和 temporal smoothness 决定轨迹能否稳定执行；
- Fréchet distance 与任务成功率评价的侧重点不同。

Phase 1 只建立这些模块的底层仿真直觉，不实现 SAG-GCN、多面体手部或力控制。

## 3. 学习范围与删减

本阶段学习：

- URDF、base、link、joint、DoF、end effector 和 joint order；
- revolute/fixed joint 与 joint limit；
- joint space、task space、world/base/end-effector frame；
- position、quaternion、pose 和基本姿态误差；
- FK、IK、FK(IK(target)) 验证；
- workspace、不可达目标、奇异附近行为和限位裕量；
- 参考腕部位姿序列、waypoint 和关节空间轨迹；
- position control、target/actual state 和 tracking error；
- 位置、方向、速度、加速度和平滑性的基础评测。

本阶段明确不学习：

- 电机、减速器、通信总线、嵌入式和机械结构设计；
- ROS 2、MoveIt 2、Gazebo、Isaac Sim 和真机部署；
- 完整刚体动力学推导、参数辨识、力矩/阻抗/导纳控制；
- 灵巧手内部结构、触觉硬件和真实力传感器；
- 相机、点云、人体姿态网络、SAG-GCN、ACT 或 VLA。

碰撞只做基本查询和失败记录，不展开通用运动规划。

## 4. 环境与学习产物

优先复用已有可用环境；只有依赖冲突时才创建独立环境：

```text
environment: eai-sim
Python: 3.10 或 3.11
packages:
  pybullet
  numpy
  scipy
  matplotlib
  pytest
```

本阶段不需要 GPU、CUDA 或 Linux，Windows + CPU 足够。

第一课开始时，在 `learning/` 下建立实际产物目录：

```text
learning/guide_phase01_robot_arm_simulation/
├── README.md
├── PROGRESS.md
├── src/
├── tests/
├── notes/
└── outputs/
```

数据约定从第一天开始固定记录：

```text
joint angles: rad
position: m
orientation: quaternion，必须写明 xyzw/wxyz
time: s
q trajectory: [T, DoF]
wrist pose trajectory: position [T,3] + orientation [T,4]
```

## 5. 六个学习单元

### Unit 1：从 URDF 识别机器人结构

核心问题：论文所说的机器人拓扑、关节配置和末端执行器在仿真里是什么？

学习与操作：

1. 运行 PyBullet GUI smoke test；
2. 加载地面和一台 6–7 DoF 机械臂 URDF；
3. 打印 joint index/name/type/parent link/child link/limit；
4. 筛选可控关节并固定 joint order；
5. 明确用于手臂重定向的 end-effector link；
6. 手动改变单个和多个关节，观察机器人构型变化。

产物：最小加载脚本、关节表、机器人结构截图、joint order 与 end-effector 说明。

通过条件：能把 `q[i]` 对应到具体关节，并解释 URDF 拓扑为何影响跨机器人重定向。

### Unit 2：FK、坐标系与腕部位姿

核心问题：机器人关节角怎样变成论文中的腕部位置与方向？

学习与操作：

1. 设置至少三组关节配置 `q`；
2. 读取末端 position 和 quaternion；
3. 每次只改变一个关节，观察位置与方向变化；
4. 区分 world/base/end-effector frame；
5. 验证 rad/degree 和 quaternion 顺序错误；
6. 绘制或记录三组 `q -> wrist pose`。

产物：FK 观察脚本、位姿表、坐标系示意、两个约定错误案例。

通过条件：能够说明关节空间、任务空间、位置误差和方向误差分别是什么。

### Unit 3：IK、可达性与 FK 回代

核心问题：给定参考腕部位姿，怎样得到可信的机器人关节配置？

学习与操作：

1. 指定只含位置的目标并求 IK；
2. 指定位置 + 方向目标并求 IK；
3. 用 FK 回代候选关节角；
4. 计算位置误差与基础四元数方向误差；
5. 检查 joint limits；
6. 比较正常、边界和不可达目标。

最低验证：

```text
q_candidate = IK(target_pose)
pose_actual = FK(q_candidate)
position_error = ||p_target - p_actual||
orientation_error = quaternion_distance(q_target, q_actual)
```

产物：IK/FK 验证脚本、误差表、至少一个失败案例。

通过条件：不会把 IK 返回值自动当作成功，能结合 FK 误差、限位和 solver 状态作判断。

### Unit 4：从单点 IK 到参考腕部轨迹

核心问题：为什么逐帧都能求解，整段动作仍可能抖动或不可执行？

学习与操作：

1. 生成一段合成腕部轨迹，例如圆弧或多 waypoint 路径；
2. 逐帧求 IK，形成 `q[T,DoF]`；
3. 使用上一帧作为连续性参考；
4. 计算相邻帧关节变化；
5. 观察解分支切换、边界和奇异附近抖动；
6. 显式记录失败帧而不是静默删除。

产物：参考腕部轨迹、原始关节轨迹、失败帧表、轨迹可视化。

通过条件：能解释单帧末端误差小为何不保证整段轨迹自然和平滑。

### Unit 5：平滑、位置控制与时间指标

核心问题：怎样把候选关节序列变成能稳定跟踪的执行轨迹？

学习与操作：

1. 对原始关节轨迹加入或比较简单平滑方法；
2. 使用 position control 执行轨迹；
3. 固定仿真 timestep 和轨迹时间戳；
4. 记录 target/actual joint state；
5. 计算跟踪误差、速度和加速度；
6. 比较“原始轨迹/平滑轨迹”和“正常速度/过快执行”。

产物：轨迹执行脚本、target/actual/error 曲线、速度/加速度曲线、两组对比表。

通过条件：能将 tracking accuracy、temporal smoothness 和 physical executability 分开评价。

### Unit 6：论文导向综合实验

核心问题：能否对一段腕部参考运动生成可重复、可诊断的机器人轨迹？

任务：使用一段固定的合成腕部位置与方向序列，完成：

```text
reference pose sequence
    -> frame/convention validation
    -> per-frame IK baseline
    -> FK validation
    -> joint-limit and failure checks
    -> smooth trajectory
    -> position-control rollout
    -> metrics and report
```

必须报告：

- 输入序列的 shape、frame、unit、timestamp 和 quaternion order；
- 每帧 position/orientation error；
- IK/FK 失败帧与 joint-limit violation；
- target/actual joint tracking error；
- 关节速度与加速度；
- 原始与平滑轨迹对比；
- 至少一个可达成功案例、一个不可达案例和一个不平滑或边界案例。

可选扩展：加入一个虚拟肩点和肘点，计算 shoulder–elbow–wrist arm-plane normal，为 Phase 3 的拟人化约束提前建立直觉。

产物：可重复命令、固定输入、综合结果表、曲线图、失败说明和一页结论。

## 6. 阶段 Gate

全部满足后才进入 Phase 2：

- [ ] 能从 URDF/仿真接口识别 joint topology、joint order 和 end effector；
- [ ] 能说明 `q`、wrist pose、reference pose 和 actual pose 的区别；
- [ ] 能读取 FK，并对 IK 结果进行 FK 回代；
- [ ] 能计算位置与方向误差；
- [ ] 能显式发现不可达目标、joint-limit violation 和失败帧；
- [ ] 能说明逐帧 IK 与整段轨迹质量不是同一个问题；
- [ ] 能生成并执行带时间戳的平滑关节轨迹；
- [ ] 能绘制 target/actual/error、velocity 和 acceleration；
- [ ] 综合实验可以从新终端按记录命令重复运行；
- [ ] 能指出本阶段结果将如何成为 DexTele/ObjRetarget 的手臂重定向 baseline。

## 7. 每次学习的协作流程

1. 助手提出本单元唯一问题、必要概念和停止条件；
2. 学习者先预测机械臂或数值结果；
3. 共同运行最小代码；
4. 学习者用自己的话解释观察；
5. 助手纠正概念或代码问题；
6. 用 2–4 个场景判断题检查理解；
7. 保存代码、输入、输出、失败记录和进度；
8. 只确定下一次唯一优先任务。

单次记录模板：

```text
Date / Unit:
Question:
Prediction:
Observation:
Data convention:
Evidence path:
Failure / confusion:
Gate result:
Relation to DexTele / ObjRetarget:
Next single action:
```

## 8. 当前入口

第一课只做 Unit 1：

1. 检查现有 Conda、Python 与 `pip` 指向；
2. 优先复用已有环境，必要时再创建 `eai-sim`；
3. 安装或验证 PyBullet、NumPy、SciPy、Matplotlib、pytest；
4. 运行 PyBullet GUI smoke test；
5. 加载机械臂并生成 joint table；
6. 固定 joint order 和 end-effector link，作为后续全部实验的机器人配置。

