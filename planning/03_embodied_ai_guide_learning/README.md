# Embodied-AI-Guide 论文导向学习总计划

> 状态：当前学习主线  
> 建立日期：2026-08-24  
> 学习资料：以 [`Embodied-AI-Guide-main`](../../Embodied-AI-Guide-main/README.md) 为知识索引  
> 目标论文：DexTele（动作重定向与自适应力控制）、ObjRetarget（物体感知动作重定向）

## 1. 总目标

本计划不是依次学完 Guide 的全部条目，而是从 Guide 中抽取理解两篇目标论文所需的最短主线：

```text
机器人模型与可执行运动
    -> 人体、手部、相机与物体表示
    -> 人到机器人动作重定向与轨迹优化
    -> 手物接触、灵巧手与自适应力调节
    -> 示范数据、模仿学习与可复现评测
    -> 两篇论文精读、对比与最小实验
```

最终应能独立解释并验证两篇论文的共同系统链路：

```text
RGB / RGB-D human demonstration
    -> 3D body/hand pose + object pose/point cloud
    -> graph/geometric representation
    -> retargeting + constrained trajectory optimization
    -> arm/hand synchronized execution
    -> contact/force adaptation
    -> trajectory and task evaluation
```

## 2. 论文侧重点与学习取舍

两篇论文共同关注上肢、双臂、灵巧手、人体示范和物体交互，所需能力集中在以下方面：

- URDF、关节拓扑、FK/IK、关节限位与位置控制；
- RGB/RGB-D、三维人体/手部关键点、四元数、骨架图；
- 相机坐标系、物体点云、6D 位姿、跟踪与接触事件；
- 人机尺度和拓扑差异、图表示、潜在空间或几何优化；
- 末端位置/方向、arm-plane、平滑性和接触几何约束；
- 灵巧手接触、力反馈、关节角—力模型和滚动优化；
- MPJPE、Quat、VE、AE、Fréchet、滑移、几何一致性与成功率；
- 人类示范如何生成可用于后续技能学习的数据。

以下内容与当前论文关系较弱，暂不进入主线：

- STM32、电机驱动、嵌入式 Linux、CAD 和机械制造；
- ROS 2 系统集成、真机通信、线缆、急停和硬件标定；
- 移动机器人导航、里程计、SLAM 系统实现；
- 四足、人形行走、无人机和自动驾驶；
- 完整强化学习课程和大规模端到端 VLA 训练；
- 触觉传感器结构设计与制作。

其中 ROS、SLAM、VLM、MPC 和触觉只学习论文中实际使用的接口与作用，不扩展成独立完整课程。

## 3. 修订后的六阶段路线

| 阶段 | 主题 | 对应论文问题 | 最低完成证据 | 详细计划 |
|---|---|---|---|---|
| 1 | 机械臂仿真与可执行轨迹 | 机器人关节角、末端位姿和参考腕部轨迹怎样对应？怎样判断轨迹可执行？ | PyBullet 腕部参考轨迹跟随程序、FK/IK 误差、限位与平滑性报告 | [PHASE_01_ROBOT_ARM_SIMULATION.md](PHASE_01_ROBOT_ARM_SIMULATION.md) |
| 2 | 人体、手部与物体感知表示 | FrankMocap/SLAHMR、RGB-D、骨架图和物体跟踪向后续模块提供什么？ | 一份带 frame/unit/timestamp 的上肢与手部序列、深度反投影和物体位姿示例 | [PHASE_02_PERCEPTION_REPRESENTATION.md](PHASE_02_PERCEPTION_REPRESENTATION.md) |
| 3 | 动作重定向与轨迹优化 | 人和机器人拓扑不同时怎样映射？DexTele/ObjRetarget 的损失和约束各解决什么？ | 人体腕部参考轨迹到机器人轨迹的 baseline、约束优化与消融 | 开始本阶段时创建 |
| 4 | 手物接触、灵巧手与力调节 | 多面体接触几何、阶段切换、力反馈和 MPC 类滚动优化怎样工作？ | 简化接触几何实验、接触状态机和目标力跟踪仿真 | 开始本阶段时创建 |
| 5 | 示范数据、模仿学习与评测 | 重定向轨迹怎样成为训练数据？策略 loss 与真实任务成功率为何不同？ | 小型 demonstration schema、BC/ACT 概念实验和指标实现 | 开始本阶段时创建 |
| 6 | 论文精读、对比与最小实验 | 两篇论文的输入、表示、优化、控制和评测如何对应，哪些结论可以复核？ | 两张完整方法图、一张对比表、指标测试和一个最小消融实验 | 开始本阶段时创建 |

主依赖关系：

```text
Phase 1 -> Phase 2 -> Phase 3 -> Phase 4 -> Phase 5 -> Phase 6
```

Phase 5 不以完整 RoboTwin/ACT 训练为强制前置。如果计算资源和时间允许，可用 RoboTwin 做一次数据—训练—评测闭环；否则优先保证重定向、接触和论文指标主线。

## 4. 各阶段边界

### Phase 1：机械臂仿真与可执行轨迹

用 PyBullet 和现成 URDF 把 joint/link/DoF、FK、IK、pose、joint limit、轨迹平滑和 position control 串起来。出口不是泛化的“控制机械臂到点”，而是让机械臂跟随一段合成的人体腕部参考轨迹，并输出论文会使用的误差与可执行性信息。

### Phase 2：人体、手部与物体感知表示

学习两篇论文感知模块的输入输出：RGB 与 RGB-D、2D/3D keypoints、位置与四元数、skeleton graph、相机内外参、depth/point cloud、object pose、tracking confidence、时间同步和 contact event。只理解 FrankMocap、SLAHMR、VLM 物体识别和跟踪器的接口与误差来源，不训练大型视觉模型。

### Phase 3：动作重定向与轨迹优化

从运动学 baseline 进入两篇论文核心：尺度归一化、root/frame 对齐、人机拓扑差异、图消息传递的作用、末端/方向/arm-plane/平滑/关节限位损失、逐帧 IK 与整段轨迹优化、潜在空间优化和约束消融。

### Phase 4：手物接触、灵巧手与力调节

围绕 ObjRetarget 的指尖—掌心—物体接触点、多面体簇、边长与相对位姿不变量，以及 DexTele 的目标抓取力、关节角—力预测和滚动优化学习。采用简化数值模型，不要求购买灵巧手、力传感器或触觉硬件。

### Phase 5：示范数据、模仿学习与评测

学习 demonstration、trajectory、observation、action、policy、Behavior Cloning、ACT/action chunk、distribution shift 和 rollout evaluation。重点理解重定向怎样为技能学习提供数据；强化学习只比较范式，不完整展开。实现论文相关指标并建立可复现实验记录。

### Phase 6：论文精读、对比与最小实验

正式逐模块精读 DexTele 与 ObjRetarget，整理 input -> representation -> retargeting -> control -> evaluation，核对公式、指标、消融和复现缺口。最小实验优先验证 tracking、joint limit、smoothness 和 arm-plane；有余力再加入手物几何或简化力调节。

## 5. 环境分层原则

不建立一个包含所有依赖的环境：

| 环境 | 用途 | 建立时机 |
|---|---|---|
| `eai-sim` | Phase 1：PyBullet、NumPy、SciPy、Matplotlib、pytest | 现在 |
| `eai-retarget` | Phase 2–4：PyTorch、图结构、优化、Open3D、数据接口 | Phase 2 开始时 |
| 策略/视觉专用环境 | ACT、特定姿态模型或论文遗留依赖 | Phase 5–6 确认确实需要时 |

Phase 1 在 Windows + CPU 上即可完成，不需要 CUDA。现代姿态估计、PyG 或策略训练到对应阶段再配置。不要为了本计划提前安装 ROS 2、Isaac Sim、真实机器人驱动或老版 FrankMocap/SLAHMR 依赖。

## 6. 通用执行规则

1. 每次只设置一个可验证问题和一个停止条件。
2. 理论讲解后立刻运行最小数值或仿真实验。
3. 任何数组必须说明 shape、字段、frame、unit、timestamp；姿态还要说明四元数顺序。
4. 同时保存成功和失败案例，不隐藏不可达、未收敛、越界或接触误判。
5. 每个阶段至少形成代码、测试、图表、结构化笔记和可重复命令中的三类证据。
6. 只有当前阶段 Gate 通过后，才创建下一阶段的详细计划文件。
7. Guide 是知识索引；学习深度由两篇论文的实际需求决定。

## 7. 当前状态与下一步

- 已完成：《机器人学简介》阅读。
- 已完成：Phase 1 — 机械臂仿真与可执行轨迹（阶段 Gate 通过）。
- 当前阶段：Phase 2 — 人体、手部与物体感知表示。
- 当前入口：[第二阶段详细计划](PHASE_02_PERCEPTION_REPRESENTATION.md)。
- 下一行动：创建并验证 `eai-retarget` 环境，进入 Unit 1 的 canonical schema 与 validator。
