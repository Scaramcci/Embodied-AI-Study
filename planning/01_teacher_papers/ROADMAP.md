# 论文学习路线

## 开学前压缩安排

按 18 天上限执行；若实际剩余时间更少，优先保留论文理解和组会材料，小型实验只做到当前可验证阶段。

| 时间 | 主任务 | 同步补的公共基础 | 最低交付 |
|---|---|---|---|
| Day 1-3 | P0，两篇论文快速建图 | F0、F1 中遇到的缺口 | 两张方法流程图、术语清单 |
| Day 4-7 | P1，精读 DexTele | 图表示、姿态与误差指标 | 符号表、模块关系和复现缺口 |
| Day 8-11 | P2，精读 ObjRetarget | 点云、IK、约束优化 | 符号表、loss 和阶段切换说明 |
| Day 12-14 | P3，对比并确定最小问题 | 轨迹平滑与实验设计 | 一页对比表、实验卡 |
| Day 15-17 | P4，只做 E0/E1 最小实验 | 缺什么补什么 | 可重复输出和一组消融 |
| Day 18 | P5 与缓冲 | 无新主题 | 组会材料、问题清单 |

任何阶段延期都不挤占 Day 18。若 E1 尚未完成，展示 E0 的正确结果与明确局限，也比仓促接入视频更可靠。

## P0 快速建图

先看摘要、方法总图、实验设置、主表和消融表。

输出：

- 每篇一张 input -> representation -> retargeting -> control -> evaluation 流程图；
- 论文用到的硬件、数据、预训练模块和未公开部分清单；
- 不懂的术语按影响大小排序。

完成条件：能在 5 分钟内讲清两篇论文分别做了什么。

## P1 精读 DexTele

重点：

- FrankMocap 输出如何转成 skeleton graph；
- SAG-GCN 的双流 arm/hand 结构；
- end-effector、orientation、arm normal、dynamics 和 finger loss；
- latent optimization 与跨机器人拓扑映射；
- VLM target force、关节角-力模型和 rolling optimization 之间的信号流；
- Sign/CSL-Daily 数据和 MPJPE/Quat/VE/AE 指标。

输出：方法笔记、公式符号表、主结果和消融结论。

## P2 精读 ObjRetarget

重点：

- RGB-D、SLAHMR、VLM 物体识别、点云与位姿跟踪；
- 初始 retargeting 与后续几何优化的分工；
- task-adaptive arm-plane regularization；
- task-oriented wrist pose loss；
- polytope cluster、edge invariant 和 relative-pose invariant；
- contact/non-contact 阶段切换；
- task success、object slip、geometric consistency 和 Fréchet distance。

输出：方法笔记、公式符号表、完整复现缺口清单。

## P3 对比与选题

固定对比：

| 问题 | DexTele | ObjRetarget |
|---|---|---|
| 人体输入 | 单目图像/FrankMocap | RGB-D/SLAHMR |
| 手臂重定向 | 图编码器+潜空间优化 | 初始轨迹+拟人几何优化 |
| 物体交互 | VLM 给出目标力，力反馈优化 | 点云与多指接触几何 |
| 主要泛化 | 跨机器人平台 | 跨示教者、物体位姿和任务 |
| 小型实验可保留部分 | 手臂图/轨迹重定向 | arm-plane 与平滑约束 |

输出：一页对比表和小型实验问题定义。

## P4 小型复现

按 [MINIMAL_REPRODUCTION.md](MINIMAL_REPRODUCTION.md) 实施，先用合成或已提取轨迹跑通，再接入短视频。

完成条件：

- 同一输入和配置可重复得到同一结果；
- 输出轨迹不越 joint limit；
- 报告 tracking、velocity、acceleration 指标；
- 有一组去除 smoothness 或 arm-plane 约束的消融。

## P5 组会准备

整理：

- 两篇论文的关系图；
- 完整复现为什么需要实验室硬件和作者代码；
- 小型实验的问题、结果、失败和局限；
- 需要向老师确认的下一步：复现、数据处理、方法改进，还是 egocentric video 方向。
