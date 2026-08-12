# Teleoperation and Data Collection

## Leader–Follower teleoperation

Entry：bring-up 与必需标定通过。先低速空载练习，再单物体短 episode；操作员始终可急停。记录 leader command、follower measured state、两路 RGB、延迟/饱和和所有 intervention 事件。演示质量标准包括平滑、任务有效、无未标注重置、无丢帧和无越限，不等于“最终成功”四个字。

## Dataset schema v0

| 字段 | 含义/要求 |
|---|---|
| `dataset_version`, `episode_id` | 不可变身份；任何清洗产生新版本 |
| `timestamp_capture/receive/control` | 同一时钟域或记录映射；单调且可测延迟 |
| `task_instruction`, `task_graph_id` | 原始语言与结构化任务版本 |
| `rgb.camera_top`, `rgb.camera_wrist` | 固定命名、shape/codec/FPS/config ID、valid mask |
| `observation.joint_position` | follower 实测，固定 joint order、单位和 calibration ID |
| `observation.gripper_state` | 实测开合/位置及有效性 |
| `action` | follower 目标，明确 position/delta/velocity、单位、频率和 horizon |
| `leader_state` | 可选但建议，便于分析 teleop 映射 |
| `success`, `termination_reason` | episode 级结果；允许 unknown/aborted |
| `subgoal_events` | 子目标开始/结束、verifier evidence |
| `failure_category` | 来自版本化 taxonomy，可多标签 |
| `intervention_flag/type` | 人工接管区间、原因、前后上下文 |
| `scene/object/layout IDs` | 支持无泄漏 split 和 OOD 定义 |
| `hardware/camera/calibration/config IDs` | 可复现物理设置 |

建议逻辑目录（不在本轮创建空目录）：`datasets/<name>/<version>/{manifest,episodes,media,audit,splits}`。名称描述任务和 schema，不包含“final”；版本由 immutable manifest/hash 管理。大型媒体和 checkpoints 不直接进 Git，Git 只跟踪 manifest、schema、审计摘要和获取方式。

## 采集设计

- 先冻结 scene distribution、任务语句、对象身份和 reset protocol。
- 训练/验证/test/OOD 按对象、布局或场景分组切分，绝不按相邻 frame 随机切分。
- Initial dataset 以一致成功 demonstrations 建立能力，但同时保留自然失败、取消和恢复标签。
- 不要只录成功 trajectory：失败状态及前后窗口是 failure mining 的关键；不可把失败硬拼进成功 episode 而不留事件边界。
- Random-success 与 failure-targeted 数据使用相同新增预算；同时报告轨迹数、有效控制步和人类操作量。
- 采集队列由 `scene × subgoal × failure type` 覆盖驱动，避免操作者只重复容易案例。

## Data audit

自动/人工检查：schema、hash、文件可读；timestamp 单调；缺失/重复/冻结图像；两相机 FPS 和错位；action/state lag；joint 越界/饱和；reset 泄漏；任务/结果/失败标签完整；抽样视频与轨迹可视化。Corrupted episode 隔离并记录原因，不静默删除或覆盖。

输出 artifact：dataset card、immutable manifest、split manifest、audit report、episode montage、动作/关节/延迟分布、failure/intervention 分布、排除清单。

## Gate

Entry：标定 Gate 通过；schema 和 split 规则冻结。Tasks：小规模 pilot 采集、审计、回放、冷启动重复。Exit：随机抽取 episode 可完整回放；无 silent missing frame/timing mismatch；失败与介入可定位；训练/验证/test 无场景泄漏；数据版本可还原。**Compute/Hardware**：采集 D；审计/可视化 A；大规模编码/训练可 B。未通过不得批量采集。

