# Optional Extensions

扩展不能打断主项目。统一 Admission Gate：G7/G8 主线稳定；扩展回答一个明确问题；不会改变冻结主结果；有独立资源/安全评估和退出条件；先在 DECISIONS 记录。不满足任一项则留在 backlog。

| Extension | 何时有价值 | 额外风险/要求 | 最小 Exit evidence |
|---|---|---|---|
| tactile / force sensing | 视觉难判断接触/slip | 新硬件、同步、校准、线缆 | 对抓取验证/恢复的增益 |
| depth camera | 几何/遮挡限制明确 | 标定、带宽、噪声 | 相对 RGB 的受控对比 |
| RL fine-tuning | BC 在明确状态有稳定不足且 reward 可验证 | 真机安全、样本成本 | 相对 BC 的安全量化增益 |
| HIL RL | 人工反馈可安全约束探索 | 操作者负担、非平稳 | 介入效率与安全事件 |
| preference learning | 难写 reward 但可稳定比较轨迹 | 标注一致性 | preference 可靠性和任务收益 |
| VLM verifier | 简单规则在语义判断上达到瓶颈 | 延迟、幻觉、成本 | 对 gold labels 的 FPR/FNR 改善 |
| world model | 需要预测长时后果/恢复 | 数据量与验证困难 | 预测对决策的实际增益 |
| π0/OpenVLA/GR00T | 小模型在语言/泛化上有明确上限 | 24/40/80GB、部署复杂和许可 | 同 protocol 下超越小 baseline |
| PiPER/xArm | 验证跨平台泛化或扩大工作空间 | 新硬件/驱动/安全 | 固定接口的跨机器人结果 |
| mobile manipulation | 桌面固定基座主线已完成 | 导航、全局安全、定位 | 独立新项目级证据 |
| ROS2 MoveIt | 需要通用 motion planning/避障 | 模型/规划集成复杂 | 明确减少碰撞或提高可达性 |
| Sim2Real | 可减少真机数据或覆盖稀有失败 | reality gap 和资产成本 | 按 [15_SIM2REAL_PLAN.md](15_SIM2REAL_PLAN.md) 通过 Gate |

扩展停止条件：主线 regression、安全风险、无法公平评估、资源超过预设上限或最小试验无效。停止并记录不是失败，而是保护主研究问题。

