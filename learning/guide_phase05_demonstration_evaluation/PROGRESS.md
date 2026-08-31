# Phase 5 学习进度

## P5-1：Trajectory 到 demonstration 与 action chunk

状态：已完成

- 构造同步 episode 与 observation/action contract；
- 生成单步 target、future action chunk 和 padding mask；
- 验证 timestamp offset、future leakage 与跨 episode 错误。

## P5-2：Offline error、distribution shift 与 rollout evaluation

状态：已完成

- 建立最小 BC 接口和专家 demonstration；
- 对比 offline one-step error 与受扰动 closed-loop rollout；
- 计算并解释目标论文中的主要轨迹、接触与成功率指标。
