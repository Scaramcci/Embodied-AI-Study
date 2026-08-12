# 老师论文路线

这是当前主线。目标是在开学前建立对 human-to-robot motion retargeting 和 learning from human video 的基本认识，并留下一个可展示的小型实验。

## 核心论文

- ObjRetarget: An Object-Aware Motion Retargeting Framework with Anthropomorphic Arm Constraints and Polyhedral Hand Modeling
- DexTele: A Dual-Arm Dexterous Teleoperation System Based on Motion Retargeting and Adaptive Force Control

论文原文与出处见 [papers/README.md](papers/README.md)。

## 这条路线要解决什么

```text
human image / video
    -> body, hand and object representation
    -> human-to-robot retargeting
    -> kinematic and interaction constraints
    -> executable robot trajectory
    -> simulation or real-robot evaluation
```

DexTele 重点是跨机器人图结构重定向与自适应力控。ObjRetarget 重点是物体感知、拟人手臂轨迹约束和多指接触几何。

## 当前边界

- 不购买双臂或灵巧手。
- 不追求复现论文完整 benchmark。
- 不下载作者代码，等阅读和小型实验设计确定后再做。
- 小型实验先使用单臂仿真、肩-肘-腕轨迹和几何/IK 优化。
- learning from egocentric video 先作为扩展问题，等老师给出具体论文后再加入主线。

## 文档

- [ROADMAP.md](ROADMAP.md)：学习顺序和每阶段输出。
- [PAPER_GUIDE.md](PAPER_GUIDE.md)：两篇论文的精读问题。
- [MINIMAL_REPRODUCTION.md](MINIMAL_REPRODUCTION.md)：不依赖灵巧手的小型实现。
- [ENVIRONMENT.md](ENVIRONMENT.md)：AutoDL、4090 Laptop 和老依赖的分工。
- [EXPERIMENT_LOG.md](EXPERIMENT_LOG.md)：这条路线的实验记录。

## 结束标准

1. 能脱离论文摘要讲清两个系统的输入、模块、loss、输出和硬件。
2. 能说明两篇论文共享的初始重定向关系，以及各自新增的问题。
3. 完成一段人体轨迹到仿真机械臂轨迹的可重复实验。
4. 报告至少一组平滑项或拟人约束消融。
5. 整理组会可用的一页方法对比与实验结果。
