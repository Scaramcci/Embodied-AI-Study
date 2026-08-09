# Ablation and Experiments

消融只回答能改变设计决策的问题。每项均先写 Question/Hypothesis/Controlled variables/Decision rule，再执行；不为增加表格穷举组合。

## 优先级

| 优先 | 对比 | 核心问题 | 控制要点 | 结果影响 |
|---|---|---|---|---|
| P0 | base vs +random vs +failure-driven | 定向纠正是否更高效 | 同 D0、同新增预算、同模型/训练/test | 主研究结论 |
| P0 | no recovery vs recovery | 恢复是否提升完整任务且不增安全风险 | 同 Actor/Verifier/scenes | 是否保留恢复层 |
| P0 | no verifier vs verifier | 显式验证是否减少错误状态推进 | 同 Actor；gold 离线复核 | 架构必要性 |
| P1 | single top vs single wrist vs dual | 双相机是否改善遮挡/抓取/放置 | 同数据预算/模型容量/增广 | 传感器设计 |
| P1 | ID vs OOD | 增益是否只在训练分布 | 冻结 strata | 泛化边界 |
| P1 | ACT vs SmolVLA | 语言模型是否改善语言泛化 | 相同可用数据/动作/评估；报告算力 | VLA 是否值得 |
| P2 | Sim2Real vs real-only | 仿真是否减少真实数据 | 同真实数据预算和 test | 是否保留仿真训练 |
| P2 | chunk/replan variants | 延迟/反馈权衡 | 小范围预注册，不大搜参 | 部署设置 |

`without verifier` 仍用离线 gold 评分，但在线 task state 采用对照逻辑；`without recovery` 在首次失败终止，不能给更多隐性重置。相机消融必须防止双相机模型因参数量/训练步获得不公平优势。ACT/SmolVLA 比较不是主研究问题，不能挤占 A/B/C 资源。

## 通用模板

- Entry：baseline 稳定、主 protocol 冻结、该组件确有待决策问题。
- Tasks：预注册假设和 primary metric；固定控制变量；生成 experiment IDs；执行并记录全部 trials。
- Validation：检查 data/test leakage、有效预算、checkpoint selection、公平 compute；查看 failure distribution 解释均值。
- Exit：结果足以做“保留/删除/需更多证据”决策；负结果同样记录；不可事后按成功结果挑消融。

