# Contributing with Codex

## 开始任务

任何较大任务前必须阅读 [项目入口](../README.md)、[状态记录](../STATUS.md)、[DECISIONS.md](DECISIONS.md)，再读该 Gate 的主题文档。确认 Entry Criteria、当前唯一 objective、预期 artifact 和验证方法；未满足 Entry 时先解决依赖。

## 记录规则

- 完成每个子任务：更新 `../STATUS.md`，只写已验证事实、修改文件和下一动作。
- 运行实验：运行前后更新 `../evaluation_release/EXPERIMENT_LOG.md`，保留失败/invalidated 记录。
- 改核心设计：先更新 `DECISIONS.md`，记录替代方案和证据。
- 遇阻塞：更新 `BLOCKERS.md`，附证据、已尝试项和安全下一步。
- 不允许无记录更换 dataset、模型、observation/action definition、evaluation protocol 或主要研究问题。

## 执行原则

1. 优先建立稳定 baseline；不因“更先进”随意升级大 VLA。
2. 一次只推进一个清晰实验问题，变更最小且可回退。
3. 自动生成代码必须有最小可验证测试；测试应覆盖单位、shape、时间、限位和异常路径。
4. 可能影响硬件安全的代码先做 replay/simulation、zero-motion dry-run、action-limit/velocity/watchdog 检查，再低速真机。
5. 所有动作通过统一 safety gate；急停、陈旧数据、越界和断连必须 fail-safe。
6. 不因某步困难绕过 Entry/Exit Criteria、数据审计或正式评估。
7. 不只展示成功案例；保留 failure、abort、intervention 和排除原因。
8. 最终结论必须有 quantitative evidence，并能定位 experiment ID、commit、dataset、config 和 trial manifest。
9. 先读上游官方接口/本地代码版本，锁定版本后实现；不凭记忆假设最新 API。
10. 当前任务若只授权规划/诊断，不扩展为安装、训练、硬件运动或其他写操作。

## 子任务完成定义

`Done = explanation + implementation/artifact + validation + recorded state`。代码“不报错”、视频“一次成功”或训练 loss 下降均不足。每个 Gate 的完成以主题文档和 [路线图](../ROADMAP.md) 的 Exit Criteria 为准。

## 会话恢复

若会话中断：从 [STATUS.md](../STATUS.md) 的 Current Phase/Objective、Last Stable Checkpoint 和 Next Recommended Action 恢复；核对 Git 状态及外部数据/checkpoint 是否与 manifest 一致；不要重复已完成实验，也不要推断未记录结果。
