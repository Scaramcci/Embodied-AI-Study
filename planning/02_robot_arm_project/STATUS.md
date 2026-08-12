# SO-101 项目状态

## 当前状态

Paused。本项目不是当前学习主线。

## 已完成

- 建立原 G0-G8 依赖 Gate。
- 定义 failure-driven A/B/C 对照和 Hardware Purchase Gate。
- 完成旧 Ubuntu 笔记本的只读盘点和环境边界设计。
- 验证 GTX 1650 驱动可用；形成 ROS 2 系统 Python 与 Conda 仿真/ML 环境的分离方案。
- 保存项目架构、SO-101 bring-up、双相机 teleop、ACT、失败数据和长时序恢复设计。

## 未实施

- ROS 2 Jazzy 安装与 smoke test。
- MuJoCo 实际闭环实验。
- SO-101 采购和实机搭建。
- 数据采集、模型训练、真机 rollout 和研究实验。

## 暂停期间的规则

- 不采购硬件。
- 不训练 ACT/VLA，不下载大型机械臂数据集。
- 不因论文线的小型重定向实验而提前启动实机。
- 论文线产生的通用几何、IK、轨迹优化和指标代码，恢复时再评估是否复用。

## 恢复后的第一步

从 [foundation_simulation/CURRENT_MACHINE_AND_NEXT_STEPS.md](foundation_simulation/CURRENT_MACHINE_AND_NEXT_STEPS.md) 的环境 smoke test 开始，而不是从购买机械臂或训练模型开始。
