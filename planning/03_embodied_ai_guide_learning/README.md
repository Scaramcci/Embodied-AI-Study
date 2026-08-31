# Embodied-AI-Guide 论文导向学习总计划

> 状态：当前学习主线（2026-08-30 起采用论文优先加速版）
> 建立日期：2026-08-24  
> 学习资料：以 [`Embodied-AI-Guide-main`](../../Embodied-AI-Guide-main/README.md) 为知识索引  
> 目标论文：DexTele（动作重定向与自适应力控制）、ObjRetarget（物体感知动作重定向）

> **当前权威执行路线：**[论文优先加速路线](ACCELERATED_PAPER_FIRST_ROUTE.md)。下方六阶段仍用于组织知识，但论文第一遍从现在并行开始，基础数据处理不再逐项设置实验与 Gate。

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

## 3. 论文优先的六阶段路线

| 阶段 | 主题 | 对应论文问题 | 最低完成证据 | 详细计划 |
|---|---|---|---|---|
| 1 | 机械臂仿真与可执行轨迹 | 机器人关节角、末端位姿和参考腕部轨迹怎样对应？怎样判断轨迹可执行？ | PyBullet 腕部参考轨迹跟随程序、FK/IK 误差、限位与平滑性报告 | [PHASE_01_ROBOT_ARM_SIMULATION.md](PHASE_01_ROBOT_ARM_SIMULATION.md) |
| 2 | 感知表示最小桥梁（压缩） | RGB-D、骨架、手部关键点和物体点云怎样形成接触/重定向输入？ | object local/world cloud、palm+fingertips 与 contact distance 示例 | [PHASE_02_PERCEPTION_REPRESENTATION.md](PHASE_02_PERCEPTION_REPRESENTATION.md) |
| 3 | 动作重定向与轨迹优化（最高优先级） | 人和机器人拓扑不同时怎样映射？两文的损失和约束各防止什么失败？ | geometric baseline、整段约束优化和关键 loss 消融 | [PHASE_03_MOTION_RETARGETING_OPTIMIZATION.md](PHASE_03_MOTION_RETARGETING_OPTIMIZATION.md) |
| 4 | 手物接触、灵巧手与力调节（高优先级） | 接触几何、阶段切换、力反馈和滚动优化怎样工作？ | polyhedral contact 几何与简化目标力闭环 | [PHASE_04_CONTACT_FORCE_CONTROL.md](PHASE_04_CONTACT_FORCE_CONTROL.md) |
| 5 | 示范数据与评测（压缩） | 重定向轨迹怎样成为训练数据？离线 loss 与真实成功率为何不同？ | demonstration 接口、BC/ACT 概念和论文指标 | 开始本阶段时创建 |
| 6 | 论文综合与小规模复现 | 两文的方法、控制、评测和复现结果如何对应？ | 方法图、对比表；DexTele 小规模训练优先，ObjRetarget 方法级实验作为互补/备用 | [PAPER_REPRODUCTION_PLAN.md](PAPER_REPRODUCTION_PLAN.md) |

主依赖关系：

```text
Paper Pass 1 从现在开始并行
                 |
Phase 1 -> 压缩 Phase 2 -> 核心 Phase 3 -> 核心 Phase 4 -> 压缩 Phase 5 -> Phase 6 综合
```

Phase 5 不以完整 RoboTwin/ACT 训练为前置。训练实战集中到论文复现轨：优先缩小复现 DexTele 官方训练代码，而不是额外训练一个与目标论文无关的大型策略。

## 4. 各阶段边界

### Phase 1：机械臂仿真与可执行轨迹

用 PyBullet 和现成 URDF 把 joint/link/DoF、FK、IK、pose、joint limit、轨迹平滑和 position control 串起来。出口不是泛化的“控制机械臂到点”，而是让机械臂跟随一段合成的人体腕部参考轨迹，并输出论文会使用的误差与可执行性信息。

### Phase 2：人体、手部与物体感知表示

只保留论文下游真正消费的表示：相机/世界 frame、上肢 skeleton graph、palm + five fingertips、object local/world cloud、6D pose 和 contact distance/event。中心化、缺失值、confidence、插值等常规处理只讲概念与一个例子，不再做独立练习；不训练大型视觉模型。

### Phase 3：动作重定向与轨迹优化

作为最高优先级，从 geometric/IK baseline 进入人机拓扑差异、root/frame 对齐、图表示作用、末端/方向/arm-plane/平滑/关节限位/object-relative loss、逐帧 IK 与整段轨迹优化和关键约束消融。通用优化数学按需补充。

### Phase 4：手物接触、灵巧手与力调节

围绕 ObjRetarget 的指尖—掌心—物体接触点、多面体簇、边长与相对位姿不变量，以及 DexTele 的目标抓取力、关节角—力预测和滚动优化学习。采用简化数值模型，不要求购买灵巧手、力传感器或触觉硬件。

### Phase 5：示范数据、模仿学习与评测

压缩为 demonstration/observation/action 接口、BC/ACT/action chunk 各一个例子、distribution shift 与 rollout evaluation。重点读懂论文指标和消融，不要求大型策略训练。

### Phase 6：论文精读、对比与小规模复现

论文粗读已从 Phase 2 并行开始；本阶段完成最终综合和复现报告。DexTele 以官方代码的小数据短程训练为主，走通数据、训练、checkpoint、评测和受控消融；ObjRetarget 在无公开代码时复现 arm-plane/平滑约束与简化接触几何。两者均不要求真实机器人或论文全部规模。

## 5. 环境分层原则

不建立一个包含所有依赖的环境：

| 环境 | 用途 | 建立时机 |
|---|---|---|
| `robotics` | Phase 1：PyBullet、NumPy、SciPy、Matplotlib、pytest | 已建立 |
| `eai-retarget` | Phase 2–4：PyTorch、图结构、优化、Open3D、数据接口 | Phase 2 开始时 |
| `eai-dextele-repro` | DexTele 作者代码、PyTorch/CUDA/PyG 与训练评测 | 完成 Phase 3 并审计仓库版本后 |
| 其他论文专用环境 | 特定姿态模型或论文遗留依赖 | 复现审计确认确实需要时 |

Phase 1 在 Windows + CPU 上即可完成，不需要 CUDA。现代姿态估计、PyG 或策略训练到对应阶段再配置。不要为了本计划提前安装 ROS 2、Isaac Sim、真实机器人驱动或老版 FrankMocap/SLAHMR 依赖。

## 6. 通用执行规则

1. 每次只设置一个可验证问题和一个停止条件。
2. 理论讲解后立刻运行最小数值或仿真实验。
3. 任何数组必须说明 shape、字段、frame、unit、timestamp；姿态还要说明四元数顺序。
4. 同时保存成功和失败案例，不隐藏不可达、未收敛、越界或接触误判。
5. A档核心概念必须有最小实验；B档只需概念和一个例子；C档不设独立实验。
6. 不再等待全部阶段完成才读论文；论文粗读、技术补课和回读并行。
7. 阶段 Gate 只检查是否还存在阻塞论文理解的关键缺口，不以完成所有练习为标准。
8. Guide 是知识索引；学习深度由两篇论文的实际需求决定。
9. 论文复现必须区分作者报告与本机结果，并固定代码版本、数据子集、随机种子、配置和环境。

## 7. 当前状态与下一步

- 已完成：《机器人学简介》阅读。
- 已完成：Phase 1 — 机械臂仿真与可执行轨迹（阶段 Gate 通过）。
- 已完成：加速 Phase 2 — hand/object 已统一到 world frame，并完成 contact distance/event 与 timestamp 失败案例。
- 已完成：Phase 3 — task-space baseline、arm-plane/smoothness、whole-trajectory optimization 与论文映射。
- 当前阶段：Phase 4 — 手物接触、灵巧手与力调节。
- 当前入口：[第四阶段详细计划](PHASE_04_CONTACT_FORCE_CONTROL.md)。
- 并行入口：[论文优先加速路线](ACCELERATED_PAPER_FIRST_ROUTE.md)。
- 后续实战入口：[论文小规模复现计划](PAPER_REPRODUCTION_PLAN.md)。
- 下一行动：立即进行论文第一遍，并学习 object local/world cloud、palm/fingertips 与 contact distance。
