# SO-101 机械臂项目

## 状态

本项目已暂停。原有目标、安全设计、仿真、数据、模仿学习和失败恢复方案均保留，但它们不再是当前执行计划。恢复时先看 [STATUS.md](STATUS.md) 和 [ROADMAP.md](ROADMAP.md)。

这个子项目可以在后续整体迁移到单独 GitHub 仓库。迁移前不拆散文档中的研究假设与 Gate，避免丢失原有设计上下文。

## 保留的目标

使用 SO-101 Pro leader/follower、第三视角与腕部 RGB，完成可安全评估的长时序桌面操作。核心研究问题仍是：在相同新增数据预算下，针对真实策略失败状态采集的纠正数据，是否比随机增加成功示教更有效。

## 项目边界

归入这个子项目：

- ROS 2、TF2、URDF、rosbag 与真机接口；
- MuJoCo 闭环抓放与仿真数据；
- SO-101 采购、电机 ID、标定、急停与限位；
- leader-follower、双相机同步和数据审计；
- BC/ACT 真机 baseline；
- failure-targeted correction、Verifier、Recovery 和长时序任务；
- OOD、消融、发布和作品集。

通用的坐标、运动学、轨迹优化和论文实验方法现在由 [公共基础](../00_common_foundations/README.md) 维护。恢复本项目时，已有证据可直接复用，不重复学习。

## 文档索引

### 项目设计

- [project/CHARTER.md](project/CHARTER.md)：范围、成果和非玩具标准。
- [project/SYSTEM_ARCHITECTURE.md](project/SYSTEM_ARCHITECTURE.md)：Planner/Actor/Controller/Verifier/Recovery 架构。
- [project/DECISIONS.md](project/DECISIONS.md)：已锁定的设计决策。
- [project/BLOCKERS.md](project/BLOCKERS.md)：阻塞记录模板。
- [project/CONTRIBUTING_AI.md](project/CONTRIBUTING_AI.md)：后续 Codex 执行规则。

### 基础、ROS 与仿真

- [foundation_simulation/LEARNING_MAP.md](foundation_simulation/LEARNING_MAP.md)
- [foundation_simulation/PRE_HARDWARE_SIMULATION.md](foundation_simulation/PRE_HARDWARE_SIMULATION.md)
- [foundation_simulation/ROS2_AND_ROBOTICS_FOUNDATION.md](foundation_simulation/ROS2_AND_ROBOTICS_FOUNDATION.md)
- [foundation_simulation/SIMULATION_STACK.md](foundation_simulation/SIMULATION_STACK.md)
- [foundation_simulation/CURRENT_MACHINE_AND_NEXT_STEPS.md](foundation_simulation/CURRENT_MACHINE_AND_NEXT_STEPS.md)
- [environments/mujoco.yml](environments/mujoco.yml)

### 实机与数据

- [hardware_data/SO101_HARDWARE_BRINGUP.md](hardware_data/SO101_HARDWARE_BRINGUP.md)
- [hardware_data/CALIBRATION_AND_SENSORS.md](hardware_data/CALIBRATION_AND_SENSORS.md)
- [hardware_data/TELEOP_AND_DATA_COLLECTION.md](hardware_data/TELEOP_AND_DATA_COLLECTION.md)

### 策略与系统

- [policy_system/BASELINE_POLICIES.md](policy_system/BASELINE_POLICIES.md)
- [policy_system/FAILURE_TAXONOMY.md](policy_system/FAILURE_TAXONOMY.md)
- [policy_system/FAILURE_DRIVEN_DATA_LOOP.md](policy_system/FAILURE_DRIVEN_DATA_LOOP.md)
- [policy_system/LONG_HORIZON_TASK.md](policy_system/LONG_HORIZON_TASK.md)
- [policy_system/VERIFIER_AND_RECOVERY.md](policy_system/VERIFIER_AND_RECOVERY.md)
- [policy_system/VLA_EXTENSION.md](policy_system/VLA_EXTENSION.md)
- [policy_system/SIM2REAL_PLAN.md](policy_system/SIM2REAL_PLAN.md)
- [policy_system/OPTIONAL_EXTENSIONS.md](policy_system/OPTIONAL_EXTENSIONS.md)

### 评估与发布

- [evaluation_release/EVALUATION_PROTOCOL.md](evaluation_release/EVALUATION_PROTOCOL.md)
- [evaluation_release/ABLATION_AND_EXPERIMENTS.md](evaluation_release/ABLATION_AND_EXPERIMENTS.md)
- [evaluation_release/EXPERIMENT_LOG.md](evaluation_release/EXPERIMENT_LOG.md)
- [evaluation_release/COMPUTE_AND_DEPLOYMENT.md](evaluation_release/COMPUTE_AND_DEPLOYMENT.md)
- [evaluation_release/REPRODUCIBILITY.md](evaluation_release/REPRODUCIBILITY.md)
- [evaluation_release/REPOSITORY_STRUCTURE.md](evaluation_release/REPOSITORY_STRUCTURE.md)
- [evaluation_release/GITHUB_AND_PORTFOLIO.md](evaluation_release/GITHUB_AND_PORTFOLIO.md)
- [evaluation_release/RESUME_OUTPUT.md](evaluation_release/RESUME_OUTPUT.md)

## 恢复条件

同时满足以下条件再恢复：

1. 老师已明确近期小组方向与你的参与方式。
2. 当前论文阅读或小型实验已形成可交付结果。
3. 有连续时间处理硬件安全、标定和数据采集，不以碎片时间启动实机。

## 独立仓库迁移

如果后续单开 GitHub，整体迁移 `02_robot_arm_project/`，并将机械臂代码、模型、配置和实验记录放在新仓库。大型数据和 checkpoint 只保存 manifest 与获取方式，不直接提交。
