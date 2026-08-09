# Verifier and Recovery

Verifier 是独立测量组件，不接受 Actor、Planner、LLM/VLM 的无证据“成功”声明。优先采用简单可靠、可校准的方法，再按错误证据增加学习模型。

## Verifier ladder

| Predicate | 首选 v0 | 可升级 | 必测 |
|---|---|---|---|
| object grasped | gripper closure/位置变化 + top/wrist 前后图像规则 | 小型视觉分类器 | precision/recall，尤其 false success |
| correct object | 目标区/夹爪 ROI 的颜色/几何/ID 分类 | learned classifier；最后才 VLM | confusion matrix、distractor |
| placed correctly | top camera 中对象中心/掩膜相对目标区 | detection/segmentation | offset、边界案例 |
| dropped | 运输中对象不再随 gripper，或地面检测 | 时序 classifier | detection delay、miss rate |
| task state updated | 成功 event + predicate evidence + 顺序约束 | 不需 VLM | 非法状态转移测试 |

规则输出 `success/failure/unknown`。阈值由 validation scene 设定，test 前冻结。Unknown 不等于 failure，也不能推进；进入 reobserve 或人工判断。若引入 VLM，仅作为可评估的候选 evidence，不能以自然语言自信度替代 gold label。

## Recovery ladder

1. **Reobserve**：停止动作，移到安全观察姿态或等待遮挡解除。
2. **Retry**：同一子目标有限次重试，记录新的 attempt。
3. **Reposition/Regrasp**：选择不同 approach、先安全释放，再重新抓取。
4. **Return safe pose**：传感不确定、振荡、饱和或路径风险时回退。
5. **Human intervention**：操作者接管并完整记录 correction 区间/原因。
6. **Abort**：碰撞、硬件/相机/时序故障、对象不可安全恢复或急停。

每个 recovery policy 定义 allowed failure types、前置安全 predicate、最大尝试、成功 predicate、timeout 和 fallback；禁止无限重试。

## 评估

Verifier：precision、recall、FPR/FNR、unknown rate、decision latency，按 failure/scene 分层；false success 的安全/任务代价单独报告。Recovery：attempt-level 和 episode-level success、额外动作/完成时间、再次失败类型、intervention avoided、collision。用冻结 episode 回放与受控真机故障注入分开测，不能只在完整系统成功样例上判断。

## Gate

Entry：taxonomy、gold-label protocol、单子目标 dataset。Tasks：实现最小规则 verifier、校准阈值、构建 recovery table、离线回放和安全故障注入。Exit：Verifier 错误量化；unknown 路径安全；每种 recovery 可中断并有上限；状态只在 evidence 通过后提交；人工 intervention 数据可回流。**Compute**：规则/轻分类器 A/B；真机验证 D；VLM verifier 可选 F，非主线前置。

