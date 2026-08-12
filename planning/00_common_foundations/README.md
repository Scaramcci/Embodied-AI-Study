# 公共基础

这部分只收录老师论文和机械臂项目都会用到的基础。当前以读懂 DexTele、ObjRetarget 和完成小型 motion retargeting 实验为标准。

## 范围

需要学：

- Linux、Conda、Git、CUDA/PyTorch 环境边界；
- 向量、坐标系、旋转、齐次变换和四元数；
- joint/link/DOF、FK、Jacobian、IK、冗余自由度和 joint limit；
- 人体骨架、手部关键点、物体位姿、深度与点云的基本表示；
- 最小二乘、约束优化、正则化、轨迹平滑和接触约束；
- position control、频率/延迟、力反馈和 MPC 的概念边界；
- 论文阅读、指标实现、对照实验和可复现记录。

不放在这里：ROS 2、TF2、rosbag、电机 ID、串口、急停、SO-101 标定、leader-follower、LeRobot、ACT 真机部署和长时序恢复。这些属于机械臂子项目。

## 学习方式

- [ROADMAP.md](ROADMAP.md)：按依赖关系安排学习顺序。
- [MATH_KINEMATICS_AND_CONTROL.md](MATH_KINEMATICS_AND_CONTROL.md)：论文所需数学、运动学和控制知识。
- [PERCEPTION_AND_REPRESENTATION.md](PERCEPTION_AND_REPRESENTATION.md)：人体、手、物体和图结构表示。
- [ENVIRONMENT_AND_TOOLS.md](ENVIRONMENT_AND_TOOLS.md)：环境隔离和本地/云端分工。
- [RESEARCH_PRACTICE.md](RESEARCH_PRACTICE.md)：阅读、评估和复现规则。

## 完成标准

进入论文小型实验前，应当能够：

1. 用 NumPy 验证坐标变换的复合与求逆。
2. 实现简单机械臂 FK，并能用 IK 解一组可达目标。
3. 解释人体骨架为什么不能直接当作机器人关节角。
4. 写出一个含 task loss、joint-limit loss 和 smoothness loss 的优化问题。
5. 自己计算 MPJPE、姿态误差、速度误差和加速度误差。
