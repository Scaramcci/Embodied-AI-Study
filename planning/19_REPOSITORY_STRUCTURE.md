# Repository Structure

以下是逐步生长的目标结构，本次不创建空代码目录。目录只有在对应 Gate 开始且有首个真实 artifact 时才创建。

```text
project/
├── configs/          # versioned system/train/eval configuration
├── docs/             # user-facing design, setup, safety and results
├── planning/         # project control plane and logs
├── hardware/         # BOM, device mapping, safety procedures (no secrets)
├── calibration/      # versioned calibration metadata and reports
├── simulation/       # MuJoCo; optional Isaac adapters/assets manifests
├── ros2_ws/          # only required ROS2 packages/adapters
├── teleop/           # leader/follower input and intervention capture
├── datasets/         # schemas/manifests/cards; large data external
├── policies/         # ACT/optional policies with common interface
├── training/         # training/evaluation entry points
├── deployment/       # local inference, controller and safety gate
├── verifier/         # predicates, learned verifier and calibration
├── recovery/         # bounded recovery rules/state transitions
├── evaluation/       # frozen trials, metrics and statistical analysis
├── scripts/          # small reproducible operational commands
├── notebooks/        # exploration only; no production-only logic
├── assets/           # lightweight diagrams/media and asset manifests
├── videos/           # small edited/public artifacts; raw media external
├── reports/          # technical report and result tables
└── tests/            # unit, replay, simulation and hardware dry-run tests
```

## 边界

`configs` 是行为来源，代码不硬编码实验参数；`deployment` 是唯一真机动作入口并调用 safety gate；`policies` 不能直接访问 servo；`verifier` 不能直接提交 task state；`recovery` 通过 Planner/Controller 接口执行；`evaluation` 只读冻结 checkpoint/dataset。`notebooks` 的有效逻辑必须迁回模块并测试。

大型 dataset、raw video、model checkpoint 不进普通 Git；只提交 schema、manifest/hash、card、样例小片段和获取路径。硬件序列号/云密钥/个人信息公开前脱敏，密钥从不进入仓库。

## 配置层次

建议组合：`robot`、`camera`、`calibration`、`task`、`observation`、`action`、`policy`、`train`、`evaluation`、`safety`。运行时把合并后的不可变 config snapshot 写入 experiment/episode，避免默认值漂移。

## Gate

Entry：相应模块首次实现。Tasks：创建最小目录、README/接口、首个测试；不预建空架构。Exit：文件所有权清晰；无循环依赖和双份配置；数据/模型身份外部可追；测试与模块同 Gate 更新。

