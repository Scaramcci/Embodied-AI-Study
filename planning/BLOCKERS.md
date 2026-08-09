# Blockers

阻塞是有证据的依赖/安全问题，不是任务困难。每个 blocker 保留尝试历史；涉及硬件时优先无运动、断电或仿真诊断。

## Active Blockers

当前无。

## Blocker Template

### BLK-XXX — Short title

- **Category**：dependency / CUDA / ROS / USB / servo / camera / dataset / training / inference / hardware / safety
- **Problem**：
- **Affected Gate / Scope**：
- **Evidence**：完整错误、日志、设备状态、最小复现；敏感信息脱敏
- **Attempts**：按顺序记录命令/配置、结果和是否改变状态
- **Current Hypothesis**：区分事实与推断
- **Safe Next Action**：最小、可逆、可验证；硬件风险时先断电/dry-run
- **Owner / External Dependency**：
- **Resolution Criteria**：
- **Resolution / Linked Decision**：

禁止通过静默换 dataset/model、降低评估要求、关闭限位或删除失败数据“解决” blocker。需要改变核心设计时转入 DECISIONS。

