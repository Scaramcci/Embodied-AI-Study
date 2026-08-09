# GitHub and Portfolio

最终 GitHub 要让读者看出这是经过量化和故障分析的真实机器人系统，而非拼接教程。

## README 证据顺序

1. 一段含任务、失败、恢复和最终完成的短 demo GIF/video；
2. 核心研究问题和 A/B/C 结果摘要；
3. Planner–Actor–Controller–Verifier–Recovery 架构图；
4. SO-101 leader/follower、工作区和双相机硬件照片；
5. 急停、motor mapping、calibration 与 teleoperation 证据；
6. dataset schema、同步可视化、episode/failure/intervention 样例；
7. ACT/可选 SmolVLA 输入输出和部署路径；
8. ID/OOD quantitative tables/plots 与不确定性；
9. failure taxonomy、失败 gallery 和 verifier errors；
10. recovery before/after、人工介入与仍失败案例；
11. 环境、数据/权重获取、复现实验命令和已知限制。

## 证明“真正做过 real robot”

可信证据包括：同一硬件的多角度/连续视频；leader/follower teleop；双相机同步 raw snippet；commanded-vs-measured joints；serial/motor mapping 的脱敏摘要；标定重载与安全测试；多次 trial 原始表；碰撞/丢帧/抓取失败和恢复；不同日期/布局的冻结评估。单段剪辑成功视频、仅仿真截图、模型训练 loss 或产品图不够。

## 发布边界

不公开密钥、完整序列号、私人路径、未经许可资产/数据；模型/数据许可逐项检查。声明哪些代码自写/由 Codex 辅助/来自上游并保留 attribution。简化公开硬件配置不能破坏复现关键信息。

## Portfolio Gate

Entry：G8 量化结果和 artifact 齐全。Tasks：从 EXPERIMENT_LOG 自动/人工核对数字；链接视频、报告、数据卡和 commit。Exit：所有数字有 experiment ID；失败和限制可见；公开步骤可由干净环境执行；无尚未完成的结果被写成事实。

