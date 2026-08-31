# ObjRetarget 2026 导读笔记

原文：`planning/01_teacher_papers/papers/ObjRetarget_2026.pdf`

## 阅读策略

- 第一遍只建立问题、输入、模块、输出和实验地图；
- 第二遍按模块理解表示和 loss；
- 公式只要求说清优化变量、目标和约束，不要求手算；
- 论文中的实验结果先记作作者报告，未独立复现前不当作已验证事实。

## Session 001：标题、摘要与 Figure 1

### 论文要解决的问题

输入一段人类操作物体的 RGB-D 视频，生成可由双臂灵巧手机器人执行的动作。困难不只是
让机器人的姿势像人，还要在抓取、移动和操作过程中维持正确的手—物体接触。

### 标题拆解

- `ObjRetarget`：把人体动作重新映射到不同身体结构的机器人上。
- `Object-Aware`：优化时显式考虑物体、物体位姿和手—物体接触，而不只看人体姿态。
- `Anthropomorphic Arm Constraints`：约束机器人手臂的弯曲趋势，减少翻肘、抖动和异常
  抬肘，同时保留冗余自由度。
- `Polyhedral Hand Modeling`：用手掌、指尖和物体接触点组成局部多面体单元，保留接触
  附近的相对几何，而不是逐项复制人体手指关节角。

### 最重要的设计选择：arm/hand 解耦

```text
人体 RGB-D 操作视频
  -> 人体动作、手部关键点、物体轨迹与接触事件
  -> 初始重定向轨迹
       |-> arm：末端任务 + 拟人 arm-plane + 平滑约束
       |-> hand：非接触时跟随初始轨迹；接触时保持局部接触几何
  -> 时间调度器同步双臂和双手
  -> 机器人控制命令
```

- arm 负责大范围接近、搬运和空间定位；
- hand 负责小尺度、接触敏感的抓持和操作；
- 如果把二者用同一目标直接优化，手臂平滑性与手部接触稳定性可能互相冲突。

### 这篇论文不是什么

- 不是从视频直接输出电机命令的端到端网络；
- 不是主要依靠强化学习反复试错；
- 不是完整的自主视觉策略学习；
- 它是感知模块、初始重定向、几何约束优化和机器人控制组成的系统流水线。

### 第一遍的五项地图

| 项目 | 当前答案 |
|---|---|
| Input | 人类操作物体的 RGB-D 视频 |
| Representation | 人体/手部关键点、物体点云与位姿、接触距离/事件、参考轨迹 |
| Retargeting | 初始 human-to-robot trajectory，再分别优化 arm 与 hand |
| Output | 双臂关节轨迹和灵巧手关节命令 |
| Evaluation | 六种真实双臂灵巧操作任务，每任务 20 次；比较成功率并做 arm/hand 消融 |

### 论文报告的主要实验结论

- 硬件：RealMan 双臂平台，每臂 6 DoF，配 Inspire 6-DoF 灵巧手；视觉使用 RealSense
  D435i。
- 任务：放置、倒水、关抽屉、双臂放置等六类任务。
- 作者报告平均成功率：ObjRetarget `75.8%`，OKAMI `61.6%`，ORION `50.8%`。
- 这些是论文作者报告的结果，目前尚未独立复现。

### 当前暂时跳过

- SLAHMR 的内部优化过程；
- skeleton graph encoder/decoder 的网络细节；
- SO(3) 李代数的具体计算；
- polytope loss 的逐项推导；
- 完整作者代码和真实硬件复现。

### 下一步

读 Figure 2 的 reference plan generation：RGB-D 视频如何变成人体轨迹、物体轨迹和接触
事件，并明确哪些是实测、哪些是模型估计。

## 问题记录

## Session 003：Figure 2 的参考计划输入

ObjRetarget 的感知输出不是机器人命令，而是一份时间同步的几何参考计划：

```text
RGB-D video
  -> SLAHMR human body/hand motion
  -> object identity + tracked object pose
  -> object surface point cloud
  -> palm + five fingertips
  -> hand/object distance and contact phase
  -> arm/hand retargeting and unified scheduler
```

本阶段最重要的接口是：手部点和物体表面必须转换到同一个 world frame，才能计算距离；
`object_cloud_local` 保存物体自身形状，`world_T_object[t]` 决定每帧物体在场景中的位置和朝向。

论文选择掌心加五指尖，并不是认为其他手部关节无用，而是因为后续多面体接触模型需要紧凑、
跨人手/机器人手形态都能对应的局部几何锚点。完整复制人体手指关节角反而会受到自由度、关节轴和
指长差异影响。

接下来只做两个最小验证：物体 local/world cloud 变换，以及 fingertip—object distance/contact event。
confidence、missing 和通用同步算法只保留接口说明。

### 学习者回答 1

- 人和机器人的手指长度、结构不同，不能直接复制人体手指关节角；保留手—物体局部
  几何关系更有利于迁移和抓取。
- 反馈：理解正确。需要进一步区分 contact event、contact geometry 和 contact force。

## Session 002：什么是接触几何

接触几何是手与物体在接触附近的空间关系，回答的不只是“有没有碰到”，还包括：

- 哪根手指接触物体；
- 接触物体表面的哪个点或区域；
- 接触点相对手掌、指尖和其他手指的方向与距离；
- 多个接触点怎样分布并共同包围、夹持或支撑物体。

以抓瓶子为例，人体拇指在瓶子一侧、食指和中指在另一侧。机器人不必复制人体的
关节角，但应尽量保留“拇指与其他手指相对分布在瓶子两侧”这一局部空间结构。

ObjRetarget 对每根接触手指构造一个局部四面体：

```text
手掌中心 + 当前指尖 + 相邻指尖 + 物体接触点
```

多根手指产生多个四面体，组成 polytope cluster。优化时让机器人对应结构的边长和
相对位姿接近人体示教，以保留局部接触方向和空间分布。

需要区分：

| 概念 | 回答的问题 |
|---|---|
| contact event | 现在是否进入/离开接触？ |
| contact point/region | 在物体哪里接触？ |
| contact geometry | 手、指尖和物体接触点怎样相对排列？ |
| contact force | 接触有多大力、沿哪个方向施力？ |
| friction/dynamics | 接触后是否会滑动、滚动或失稳？ |

该论文的 polyhedral modeling 主要是几何约束，不等同于真实接触力或摩擦建模。因此
几何保持更好通常有利于稳定抓取，但不能单独保证物体一定不会滑落。

## 小规模复现安排

截至 2026-08-30，官方项目页与 arXiv 页面没有公开代码入口，因此当前不声称做作者代码复现。

- 完成 Phase 3 后，自行实现末端任务、arm-plane、joint limit 和 temporal smoothness 的整段轨迹优化；
- 完成 Phase 4 后，用合成物体点云、掌心和指尖实现简化的 object-relative/polyhedral contact geometry；
- 对比去掉 arm-plane、smoothness 或接触几何后的失败行为；
- 只评价几何误差、平滑性、限位余量和接触保持，不外推真实机器人成功率；
- Phase 6 前复查作者是否发布代码。详细步骤见 [`PAPER_REPRODUCTION_PLAN.md`](../../planning/03_embodied_ai_guide_learning/PAPER_REPRODUCTION_PLAN.md)。

复现性质：论文核心思想的方法级简化复现，而非原系统完整复现。

## Phase 3 回读：拟人手臂轨迹优化

本项目已分别验证 ObjRetarget 手臂目标的三个角色：

- `L_task`：通过 FK 保持腕部位置/方向；
- `L_plane`：在腕部任务相同的冗余解中选择合理的肘部弯曲方向；
- temporal smoothness：抑制相邻关节跳变和 IK branch flip。

受控消融表明 task-only 可在腕部零误差时产生 119.2 deg 最大平面误差和约 380 mm/frame 肘部跳变；过强 smoothness 又会增加 plane error。边界：实验使用合成 swivel reference 和二维/简化运动学，尚未实现论文的 task-adaptive normal、`w(t)`、SO(3) log 或物体接触几何。详细映射见 [`P3_PAPER_MAPPING.md`](../guide_phase03_motion_retargeting_optimization/notes/P3_PAPER_MAPPING.md)。
