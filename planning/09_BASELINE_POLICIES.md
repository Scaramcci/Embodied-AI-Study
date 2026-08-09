# Baseline Policies

顺序采用 scripted → ACT → 可选 Diffusion Policy → SmolVLA。Scripted 验证系统和指标；ACT 是成熟且规模适合的 action-chunk baseline；Diffusion 增加多模态动作建模但训练/采样更重；SmolVLA 只有在单任务闭环稳定后才用于语言条件。BC 小模型在仿真中作为 pipeline smoke baseline。π0.5/OpenVLA/GR00T 不作为起点，因为其资源、部署和诊断复杂度会掩盖数据/控制问题。

## Baseline 0 — Scripted / state-machine oracle

- **Input/Output**：已知/估计对象与机器人状态 → 分阶段 joint/task-space target。
- **Dataset/Training**：无学习；也可生成 sim demonstrations。
- **Inference/rollout**：确定性、经过相同 safety gate；真机仅在可靠 perception/几何可用时做有限脚本。
- **Metrics**：系统上限、控制/抓取/放置成功率、延迟。
- **Failure modes**：状态估计错、不可达、接触参数、硬编码过拟合。
- **GPU**：A；真机 D。
- **Gate**：能区分基础设施故障与 learned policy 故障。

## Baseline 1 — ACT（主 baseline）

- **Input/Output**：双 RGB + joint/gripper + 可选任务 token → 关节/夹爪 action chunk。
- **Dataset**：审计通过的 teleop episodes；固定 normalization、joint order、camera order。
- **Training**：先 overfit 小样本，再正式 train/val；锁定 chunk horizon、temporal aggregation、augmentations 和 seed。
- **Inference**：本地预处理与推理，滚动 chunk，可被 verifier/急停中断；记录 inference/chunk age。
- **Real rollout**：离线回放 → zero-motion dry-run → 限幅低速 → 单子目标 → 多场景。
- **Metrics**：offline action error 仅诊断；主要看闭环成功、平滑/饱和、子目标及故障分布。
- **Failures**：covariate shift、相机错序、normalization 错、chunk 过期、动作平均化、遮挡。
- **GPU**：A 做 smoke/推理视模型而定；正式训练推荐 B；E 适合本地迭代和较大实时推理。
- **Gate**：固定 protocol 有可重复真机量化 baseline，失败均进入 taxonomy。

## Baseline 2 — Diffusion Policy（可选）

- **Input/Output**：视觉+proprioception → 多步动作分布/序列。
- **Dataset/Training**：使用与 ACT 相同版本与 split；调参预算预先限制。
- **Inference/rollout**：测采样步数、延迟、动作中断；不能牺牲本地闭环时效。
- **Metrics**：相同 trial manifest 下成功率、延迟、平滑、数据效率。
- **Failures**：采样慢、随机性难复现、动作不连续、超参优势不公平。
- **GPU**：B 推荐；E 可本地；A 不建议正式训练。
- **Admission**：ACT 稳定且有“动作多模态”证据；否则不加入。

## Baseline 3 — SmolVLA / language-conditioned

- **Input/Output**：任务语言、双 RGB、proprioception → action chunks。
- **Dataset/Training**：语言一致性审计；先参数高效微调或官方可行路径，不从头预训练。
- **Inference/rollout**：本地真机推理优先；若模型不满足延迟/显存则不把公网服务器放入闭环。
- **Metrics**：除操作成功外，测语言顺序、改写指令和任务泛化。
- **Failures**：语言 grounding、token/视觉处理错、延迟、灾难性动作、数据规模不足。
- **GPU**：16GB 是否足够取决于具体 checkpoint、精度、batch、序列长度和官方版本；先实测 memory/latency。训练一般 B；更大模型/全参训练 F。
- **Admission**：G7 的非 VLA 长时序 baseline 已通过；贡献仍是失败驱动数据/验证恢复，不是模型名。

## 模型通用 Gate

Entry：dataset audit 与 evaluation protocol 冻结。Tasks：配置化训练、checkpoint 身份、离线回放、dry-run、安全 rollout。Exit：实验可追溯到 commit/dataset/config/hardware/seed；与前一层用相同测试清单；报告失败和资源；没有模型因“更先进”跳过安全或公平比较。

