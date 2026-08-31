# Phase 3：动作重定向与轨迹优化

> 状态：已完成（2026-08-31，阶段 Gate 通过）  
> 前置条件：Phase 1、加速版 Phase 2 Gate 已通过  
> 优先级：六阶段中最高  
> 建议节奏：4 个核心单元，每单元 60–90 分钟  
> 论文出口：读懂 DexTele/ObjRetarget 的重定向变量、复合损失、轨迹约束、消融与失败模式

## 1. 阶段核心问题

给定时间同步的人体肩—肘—腕/手部运动，怎样生成具有不同长度、关节数、拓扑和限位的机器人轨迹，同时保留任务意图、动作连续性与必要的拟人结构？

```text
human skeleton / wrist reference / object context
    -> root, scale, frame and semantic correspondence
    -> geometric or learned initial retargeting
    -> robot FK and task-space losses
    -> joint-limit, arm-plane and temporal constraints
    -> whole-trajectory refinement
    -> FK metrics, ablation and failure report
```

本阶段始终区分：

- 人体关节观测 `human pose`；
- 机器人优化变量 `q[0:T]`；
- `FK(q)` 得到的机器人关键点/末端位姿；
- 参考任务、软 loss、硬 constraint 与执行后的真实状态；
- 初始化方法、轨迹细化方法和最终控制器。

## 2. 与两篇论文的直接对应

### DexTele

- 人体和不同机器人是拓扑、尺度和 DoF 不同的骨架图；
- SAG-GCN 以节点 `[position, quaternion]` 和边向量编码局部几何；
- 双流分别处理手臂的粗粒度运动与手部的细粒度运动，再融合；
- 复合目标包括末端位置、方向、手臂法向、动态和手指项；
- 网络输出仍需经过 FK 和 MPJPE、Quat、VE、AE 等指标验证；
- 本阶段理解方法和训练接口，完整小规模训练放到后续论文复现轨。

### ObjRetarget

- 初始重定向只提供可行且结构一致的参考轨迹，不等于最终轨迹；
- `L_task` 保持腕部位置与 SO(3) 姿态任务；
- `L_plane` 使用肩—肘—腕平面法向抑制翻肘、异常抬肘与不自然构型；
- `||q(t)-q(t-1)||²` 约束时间连续性；
- 总体优化以整段 `q(t)` 为变量，在任务精度、拟人先验与平滑之间折中；
- 物体接触多面体留到 Phase 4，本阶段只保留 object-relative loss 接口。

## 3. 学习取舍

### 必学并实验

- 人机 link length、DoF、joint axis、topology 与 joint limit 差异；
- joint-space copying、task-space retargeting 与 object-relative retargeting；
- root/frame 对齐与尺度处理保留、丢失了什么；
- FK 作为优化变量 `q` 与任务误差之间的桥梁；
- position/orientation、limb direction、arm-plane、joint-limit、smoothness loss；
- loss 的单位、归一化与权重变化造成的具体失败；
- frame-wise IK/optimization 与 whole-trajectory optimization；
- warm start、冗余解、可达性、奇异与失败帧；
- baseline/消融必须使用同一输入、初始化和指标。

### 概念 + 一个例子

- 图编码器、消息传递、attention、GRB、latent optimization；
- SO(3) 对数映射；
- 软约束、硬约束、penalty 和正则化；
- 一阶/二阶差分与 VE/AE；
- 自动微分、SciPy 与 PyTorch 优化器的接口差异。

### 暂不展开

- 通用深度学习、图神经网络或非线性优化完整课程；
- 完整 FrankMocap/SLAHMR 视觉管线；
- 全身 humanoid retargeting、动力学可行性和接触动力学；
- 真机自碰撞规划、MoveIt/ROS 集成和实时控制；
- DexTele 全量训练、全部机器人平台与真实遥操作硬件。

## 4. 环境与数据约定

优先复用：

| 环境 | 用途 |
|---|---|
| `eai-retarget` | NumPy/SciPy 数值重定向、损失、轨迹优化和绘图 |
| `robotics` | 需要 KUKA/PyBullet 做三维 FK/执行验证时使用 |

PyTorch/PyG 在进入 DexTele 单 batch/训练复现前再安装到独立的 `eai-dextele-repro`，不让论文遗留依赖污染当前环境。

本阶段统一接口：

```text
timestamp                 [T]          s
human_arm_points          [T,3,3]      shoulder, elbow, wrist; m
human_wrist_quat_xyzw     [T,4]
robot_q                   [T,Nq]       rad
robot_arm_points          [T,3,3]      shoulder, elbow, wrist; m
robot_wrist_pose          position [T,3] + quaternion [T,4]
object_pose               [T,7]        optional
loss_terms                [T,K] or scalar summary
valid/failure_reason      [T]
```

每次必须记录 robot joint order、limits、frame、单位、时间步、初始化与 loss 权重。

## 5. 四个核心单元

### P3-1：人机差异与几何重定向 baseline

核心问题：为什么人体关节角不能直接复制给机器人？重定向究竟应保留什么？

实验：

1. 用二维两关节人体臂和三关节机器人臂制造 DoF、长度和拓扑差异；
2. 将 `q_human` 补零复制给机器人，作为故意粗糙的 joint-copy baseline；
3. 从人体提取经 root/scale 对齐的腕部位置与方向任务；
4. 通过 robot FK 和有界优化求 `q_robot`；
5. 比较腕部位置/方向误差、轨迹连续性和限位。

产物：joint-copy 与 task-space retargeting 对比图、轨迹数组和指标。

通过条件：能说明 joint 数组没有天然语义对应；task-space 方法保留的是选定任务，不会自动保留全部人体姿态。

### P3-2：复合损失与约束字典

核心问题：论文中的每一项 loss 在阻止哪一种机器人失败？

围绕以下目标建立数值实验：

```text
L = w_pos L_pos
  + w_ori L_ori
  + w_dir L_limb_direction
  + w_plane L_arm_plane
  + w_limit L_joint_limit
  + w_smooth L_temporal
```

重点：

- `L_pos` 与 `L_ori` 不能裸相加，必须通过容差或权重形成可比较尺度；
- arm-plane 法向来自叉乘，手臂近共线时需要处理退化；
- joint limit 可用 bounds 做硬约束，也可用 margin penalty 做软保护；
- smoothness 可能牺牲局部跟踪精度，权重不是越大越好。

产物：loss 字典、单位/尺度表和单项权重扫描图。

### P3-3：逐帧解与整段轨迹优化

核心问题：为什么每帧任务误差很小，轨迹仍会抖动或翻肘？

实验：

1. 对同一参考腕部序列独立逐帧求解；
2. 使用上一帧 warm start；
3. 以 `q[0:T]` 为整体变量加入速度/加速度或一阶差分项；
4. 保留不可达/退化帧，不删除原始索引；
5. 比较 FK position/orientation error、相邻 `q`、VE/AE、limit margin 和 arm-plane change。

产物：三种求解策略、完整指标表和失败帧可视化。

### P3-4：论文映射与最小消融

核心问题：DexTele 与 ObjRetarget 分别用学习和几何优化解决了哪一部分？

实验与阅读：

- 把本阶段数组和 loss 映射到 DexTele 的 graph -> latent -> robot q -> FK -> metrics；
- 把整段优化映射到 ObjRetarget 的初始化、`L_task`、`L_plane` 和 smoothness；
- 只做受控消融：去掉 smoothness、plane 或 limit 中的一项；
- 明确论文作者数值与本项目实验数值不能直接比较。

产物：方法映射表、至少一个消融图和 Phase 3 报告。

## 6. 阶段 Gate

- [x] 能解释人体 `q` 为什么不能按索引复制给不同机器人；
- [x] 能区分 joint-space、task-space、graph/geometric 与 object-relative 表示；
- [x] 能写出 `q -> FK(q) -> loss` 的优化链；
- [x] 能说明主要 loss 的单位、权重和对应失败行为；
- [x] 能计算并解释 shoulder–elbow–wrist arm-plane normal；
- [x] 能区分逐帧成功、整段平滑和控制可执行性；
- [x] 能用相同输入完成一个受控消融；
- [x] 能把实验模块逐项映射到 DexTele 与 ObjRetarget；
- [x] 能确定 DexTele 小规模训练复现的输入、loss、checkpoint 和评测接口。

通过后进入 Phase 4，并启动 DexTele 论文代码的 R0/R1 审计。

## 7. 当前入口

运行 P3-1 二维异构手臂实验，先比较“关节角补零复制”和“任务空间重定向”，不要提前进入神经网络。
