# Decisions

核心方向变化前新增记录，不覆盖旧记录。字段：Decision / Reason / Alternatives / Evidence / Can Revisit。

## D-001 — 主研究问题采用 failure-driven data collection

- **Decision**：主对比是 base、base+random-success、base+failure-targeted correction。
- **Reason**：直接连接 covariate shift、真实失败状态和人类数据效率，且能用公平预算量化。
- **Alternatives**：multi-camera robustness、sensor degradation、verifier-guided manipulation、intervention-efficient IL。
- **Evidence**：当前项目目标与资源约束；尚无实验结果。
- **Can Revisit?**：可以，但须在主实验启动前用 pilot 证据说明不可行；启动后只能作为明确的新版本研究问题。

## D-002 — 先稳定 ACT，不先上大 VLA

- **Decision**：scripted/小 BC 验证 pipeline，ACT 为主真机 baseline，SmolVLA 后置；π0/OpenVLA/GR00T 非起点。
- **Reason**：ACT 的 action chunk 与任务匹配，训练/部署/诊断成本较低，不掩盖数据、同步和控制故障。
- **Alternatives**：Diffusion Policy、SmolVLA、大型 VLA 直接微调。
- **Evidence**：项目重点是 failure-driven 数据与系统研究，不是模型规模。
- **Can Revisit?**：ACT Gate 通过且有语言/动作多模态瓶颈证据后。

## D-003 — 双 RGB：top + wrist

- **Decision**：默认 observation 使用固定第三视角和腕部 RGB。
- **Reason**：top 提供全局任务/目标状态，wrist 提供局部抓取细节，两者遮挡模式互补。
- **Alternatives**：仅 top、仅 wrist、depth/tactile。
- **Evidence**：系统需求；最终需用相机消融验证。
- **Can Revisit?**：若同步/带宽风险或消融表明无收益。

## D-004 — MuJoCo 必需，Isaac 可选

- **Decision**：MuJoCo 承担基础闭环和 IL 仿真；Isaac 仅过 Admission Gate 后加入。
- **Reason**：轻量、适合旧本地；Isaac 价值主要在并行、高保真传感和随机化，可由 AutoDL headless 承担。
- **Alternatives**：Isaac-only、无仿真。
- **Evidence**：算力条件和学习目标。
- **Can Revisit?**：MuJoCo 无法回答明确传感/规模问题时。

## D-005 — Planner/Actor/Controller/Verifier 分层

- **Decision**：语义顺序、动作预测、低层安全执行和结果判断分离，Task State 只接受验证事件更新。
- **Reason**：可单独测试、定位失败、阻止 Actor/LLM 自报成功。
- **Alternatives**：单一端到端 policy 包含状态推进。
- **Evidence**：长时序与恢复要求。
- **Can Revisit?**：接口可精简，但安全 gate 和独立 evidence 不可取消而无消融。

## D-006 — 真机实时闭环本地运行

- **Decision**：USB/camera/inference/safety/controller 本地；云端做训练、headless 仿真和 batch evaluation。
- **Reason**：公网延迟/中断不可成为硬件安全依赖。
- **Alternatives**：云端实时 inference。
- **Evidence**：系统安全边界。
- **Can Revisit?**：只可在本地保底控制和明确网络失效安全下做独立非主线实验。

## New Decision Template

### D-XXX — Title

- **Decision**：
- **Reason**：
- **Alternatives**：
- **Evidence**：
- **Can Revisit?**：

