# Project Charter

## Why

项目要把深度学习能力转化为机器人系统能力：从传感、控制和数据时序开始，最终形成可在真实失败后继续推进任务的系统。研究贡献不是“跑通某个大模型”，而是用受控实验回答 failure-targeted correction data 是否更高效。

## What

最终系统接收含顺序约束的自然语言任务，使用 SO-101 Pro follower、leader teleoperation、第三视角与腕部 RGB，在桌面场景完成多个物体的有序抓取放置。系统维护明确 task state，每个子目标后验证；发生失败时执行可审计恢复或请求人工介入。

## 范围边界

必须包含：Linux/可复现环境、机器人模型与控制基础、ROS2/TF 基础、MuJoCo 闭环、数据 schema/审计、teleop、双 RGB 标定、ACT baseline、真机 rollout、failure taxonomy、定向纠正数据实验、Verifier/Recovery、OOD/量化评估、GitHub/视频/技术报告。

不属于主线：从零讲 Python/PyTorch/Transformer；通用移动导航；人形 whole-body control；自主机械设计；训练基础大模型；用 RL 替代尚未稳定的模仿学习；为了复杂度强行加入 Isaac/Sim2Real/MoveIt。

Optional extension 只有在 G8 前置条件满足后才进入：Diffusion Policy、SmolVLA、更大 VLA、深度/触觉/力、HIL RL、偏好学习、VLM verifier、world model、移动操作。

## 成果清单

- 安全可重复的 SO-101 leader/follower 与双相机系统；
- 带版本、回放、完整性审计和失败/介入标签的数据集；
- scripted 与 ACT 定量 baseline，及可选语言条件 baseline；
- A/B/C 等新增数据预算的研究实验与统计不确定性；
- 长时序 Planner–Actor–Controller–Verifier–Recovery 系统；
- ID、OOD、消融、故障分布和恢复评估；
- 可复现实验配置、checkpoint 元数据、技术报告、GitHub 文档与演示视频；
- 简历、研究 CV 和导师联系材料，但所有数字只从实验记录提取。

## Tutorial / Engineering / Research

| 层级 | 特征 | 本项目要求 |
|---|---|---|
| Tutorial Demo | 跟教程运行一次；单一成功视频；设置不可追踪 | 仅作为学习中间产物，不是终点 |
| Engineering Project | 接口清晰、安全、可复现；数据和日志可审计；失败可诊断 | 必须达到 |
| Research-Oriented Project | 明确假设、公平对照、量化协议、OOD/消融和限制讨论 | 必须达到 |

## 非玩具项目判据

- 任务有多个依赖子目标和 distractor，局部失败不会让整条系统无条件重启；
- Planner、Actor、Controller、Verifier 职责可分别测试；
- 测试场景在采集前固定，训练/验证/测试对象与布置不泄漏；
- 失败案例、人工介入和安全停止均保留，不能只剪辑成功样本；
- 结论来自多次预定义条件实验，而非单次演示；
- 新增随机数据与定向数据的条数/时长/动作量至少采用一种公平预算并报告另一种；
- 代码、配置、硬件、相机、数据和 checkpoint 可追溯。

## 求职与科研价值

工程价值体现在真实传感器时序、标定、控制边界、安全、数据系统和部署；研究价值体现在真实 policy failure 分布、干预效率与长时序验证；沟通价值体现在将失败而非只把成功演示作为第一等证据。不能把可选模型名、参数量或设备价格当作贡献。

## 项目级完成标准

Entry：G0–G7 均通过且正式协议冻结。Tasks：执行 G8、复现实验、整理公开材料。Exit：所有关键结论能定位到 experiment ID、dataset version、commit、配置和原始统计；演示含正常、失败、恢复和 OOD；安全/限制被明确陈述；第三方能按文档恢复环境与评估流程。

