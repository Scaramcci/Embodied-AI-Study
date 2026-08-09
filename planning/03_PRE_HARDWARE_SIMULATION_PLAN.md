# Pre-Hardware Simulation Plan

目标是在不拥有 SO-101 时完成可迁移的最小闭环和 imitation-learning pipeline；不是把所有仿真扩展做完。计算标签：A=旧 GTX1650 本地；B=建议 AutoDL；C=云端可做但本地 GPU GUI 更顺畅；D=必须本地实体 SO-101；E=建议未来 M16 16GB；F=仅大模型训练需 24/40/80GB 云 GPU。

## M0 Linux / Git / reproducible environment

- **Goal**：形成可恢复的开发基线。
- **Concepts to Learn**：Ubuntu 包/权限/设备、Git、Python 环境、lock/容器边界、CPU/GPU 驱动与用户空间依赖。
- **Implementation Tasks**：只盘点 OS/GPU/驱动/磁盘；规划仓库、环境 manifest、最小 smoke test；不在本轮安装。
- **Inputs / Outputs**：机器信息与项目要求 → 环境设计、版本清单、诊断命令记录。
- **Validation / Common Failure Modes**：新环境可由 manifest 重建；避免系统 Python 污染、CUDA/torch 错配、只记录 `latest`。
- **Artifacts**：environment spec、hardware inventory、smoke-test 输出。
- **Compute**：A。
- **Exit Criteria**：能解释每个版本约束；全新环境重建路径明确且测试定义完整。

## M1 ROS2 foundation

- **Goal**：能观察和诊断机器人消息图，为真机集成做准备。
- **Concepts**：node/topic/service/action/launch/rosbag、QoS、TF、时间。
- **Tasks**：按 [04_ROS2_AND_ROBOTICS_FOUNDATION.md](04_ROS2_AND_ROBOTICS_FOUNDATION.md) 完成 publisher→controller mock→joint state→bag 回放练习。
- **Inputs / Outputs**：模拟 joint command/state → graph、bag、频率/延迟统计。
- **Validation / Failures**：消息频率和单位断言；排查 QoS 不匹配、frame/时间错、陈旧消息。
- **Artifacts**：graph/TF 图、bag manifest、诊断笔记。
- **Compute**：A。
- **Exit**：能从命令 topic 追到状态反馈并回放复现。

## M2 Robot model / URDF

- **Goal**：建立与未来 SO-101 joint/frame 命名一致的模型接口。
- **Concepts**：link、joint、DOF、limit、collision/visual/inertial、base/tool frame。
- **Tasks**：选择可信模型来源并锁定版本；检查 joint order/axis/limits；RViz/MuJoCo 对照。
- **Inputs / Outputs**：URDF/mesh/spec → joint/frame contract 和模型审计。
- **Validation / Failures**：零位截图、随机 joint FK 对照；发现轴向、单位、mesh scale、关节序错误。
- **Artifacts**：model manifest、joint table、frame diagram、审计测试。
- **Compute**：A。
- **Exit**：每个 joint 的名称、单位、方向、范围和父子 link 有证据。

## M3 TF / FK / IK

- **Goal**：把 joint、末端、相机和物体位置放到一致坐标体系。
- **Concepts**：齐次变换、TF tree、FK、IK 可达性/多解/奇异性。
- **Tasks**：发布模型 TF；数值 FK；对一组可达/不可达目标调用 IK 或简化求解器。
- **Inputs / Outputs**：joint state/target pose → end-effector pose/joint candidates/status。
- **Validation / Failures**：变换往返、FK 对照、末端误差；排查 frame 混用、四元数顺序、度/弧度、错误解分支。
- **Artifacts**：TF tree、测试向量、误差表、可达域图。
- **Compute**：A。
- **Exit**：能解释并复现 FK，IK 不可达时显式失败而非输出危险命令。

## M4 MuJoCo closed-loop robot

- **Goal**：建立最小 reset→observe→act→step→log 闭环。
- **Concepts**：qpos/qvel、actuator、position control、contact、simulation/control step。
- **Tasks**：加载模型；安全位；关节阶跃/轨迹；记录 commanded/actual；加入动作/速度限制。
- **Inputs / Outputs**：目标关节 → 模拟状态、误差、接触和视频。
- **Validation / Failures**：固定种子曲线；排查爆炸、穿透、振荡、actuator/关节映射错误。
- **Artifacts**：rollout log、控制曲线、短视频、故障注入结果。
- **Compute**：A。
- **Exit**：受扰动后闭环重新收敛；限位和异常能停止 rollout。

## M5 Simple manipulation

- **Goal**：通过脚本或状态机完成可解释的 reach–grasp–lift–place。
- **Concepts**：approach pose、grasp aperture、contact、可达性、阶段终止。
- **Tasks**：定义单物体/目标区；实现分阶段 oracle/scripted policy；参数化初始位姿。
- **Inputs / Outputs**：scene state → actions、subgoal events、success/failure。
- **Validation / Failures**：多初始位姿；诊断 miss、slip、碰撞、不可达和 placement offset。
- **Artifacts**：场景配置、轨迹、成功率、失败样本。
- **Compute**：A。
- **Exit**：有固定评估集、量化成功率和可重现失败，不只一条成功视频。

## M6 Observation / action contract

- **Goal**：冻结能迁移到真机的 v0 schema。
- **Concepts**：state vs observation、proprioception、frame stacking、action chunk、时间语义。
- **Tasks**：定义两路 RGB 占位、joint/gripper、validity mask；action 单位/范围/频率；序列化和 shape 测试。
- **Inputs / Outputs**：仿真原始状态/图像 → 标准 observation/action episode。
- **Validation / Failures**：round-trip、单位、关节序、timestamp monotonic；防 silent cast、off-by-one、future leakage。
- **Artifacts**：schema/version、样例 episode、validator 报告。
- **Compute**：A。
- **Exit**：字段均有 shape/dtype/unit/frame/rate，真机替换数据源不改变 policy API。

## M7 Simulated demonstrations

- **Goal**：产生小而可审计的训练集。
- **Concepts**：episode/reset/termination、expert quality、train/val/test scene split。
- **Tasks**：用 scripted policy 采集成功与已知失败；保留 seed/config；可视化回放；按场景而非 frame 切分。
- **Inputs / Outputs**：scene distribution + expert → versioned episodes/manifest。
- **Validation / Failures**：缺帧、重复帧、动作/状态错位、split leakage、reset 污染检查。
- **Artifacts**：dataset manifest、audit report、montage、failure labels。
- **Compute**：A；大量渲染可 B。
- **Exit**：抽样回放、完整性与切分检查通过，所有 episode 可追溯。

## M8 BC baseline

- **Goal**：用最简单模型验证完整学习管线。
- **Concepts**：BC、offline loss vs rollout、covariate shift。
- **Tasks**：训练小型 state/vision policy；冻结 preprocessing；保存配置/checkpoint；在线 rollout。
- **Inputs / Outputs**：v0 dataset → action prediction/checkpoint/metrics。
- **Validation / Failures**：overfit 小样本、held-out loss、闭环成功率；排查 normalization、动作对齐和 train/eval 模式。
- **Artifacts**：experiment log、curves、checkpoint manifest、rollout failures。
- **Compute**：state BC A；轻量视觉 BC A/B。
- **Exit**：dataset→train→rollout 可重复，能解释 offline/online 差距。

## M9 ACT baseline

- **Goal**：验证 action chunk 视觉模仿策略和后续真机主 baseline。
- **Concepts**：chunk horizon、temporal aggregation、replanning、latency。
- **Tasks**：接入双视角 schema；训练；比较 chunk/replan 设置；加入 chunk 中断。
- **Inputs / Outputs**：图像+proprioception → joint/gripper action chunks。
- **Validation / Failures**：固定 test scenes、扰动、动作平滑/饱和；排查 chunk 时序、累积误差、过期动作。
- **Artifacts**：config/checkpoint、曲线、rollout 视频、failure distribution。
- **Compute**：小规模 A 可 smoke test；正式训练 B；未来 E 便于本地迭代。
- **Exit**：固定协议量化优于或清楚解释不优于 BC；失败可定位到数据/策略/控制。

## M10 Evaluation and failure loop prototype

- **Goal**：在买硬件前演练正式评估和定向数据回收。
- **Concepts**：trial unit、预算公平、failure mining、uncertainty。
- **Tasks**：冻结场景列表；自动记录指标；从仿真失败状态收集 targeted correction；做小型 A/B/C 流程验证。
- **Inputs / Outputs**：checkpoints + trial manifest → trial table、failure buckets、recollection queue。
- **Validation / Failures**：检查样本独立性、重试选择偏差、数据泄漏和只保留成功结果。
- **Artifacts**：评估脚本规范、结果表、失败 gallery、实验日志。
- **Compute**：A/B。
- **Exit**：同一 checkpoint 能在冻结场景上重复评估；故障到回收任务可追踪。

## M11 Optional Isaac

- **Goal**：仅在并行、传感真实性或 domain randomization 带来明确收益时扩展。
- **Concepts**：headless parallel env、GPU sensors、domain randomization、资产/仿真差异。
- **Tasks**：先写价值假设；迁移一个已由 MuJoCo 验证的任务；对照性能与工程成本。
- **Inputs / Outputs**：冻结任务接口 → Isaac env、批量数据/评估。
- **Validation / Failures**：跨 simulator action/observation 对齐；排查资产尺度、contact、camera/render 差异。
- **Artifacts**：迁移决策、headless config、对照结果。
- **Compute**：headless B；GUI C/E。Isaac 不要求本地运行。
- **Exit**：有可量化附加价值；否则记录“不采用”并回归主线。

## Hardware Purchase Gate

Entry：M0、M2–M10 的必需部分完成，M1 达到接口诊断能力；M11 非前置。Tasks：阅读 LeRobot SO-101 pipeline 并把其字段/控制流映射到本项目；准备采购、安全与 bring-up 清单。Exit：能解释 observation/state/action/policy/controller，跑通闭环 simulated robot 和 imitation policy，能独立追踪 dataset→train→rollout→failure。达到后即可购买 SO-101，不需要等所有 simulation 完成。

