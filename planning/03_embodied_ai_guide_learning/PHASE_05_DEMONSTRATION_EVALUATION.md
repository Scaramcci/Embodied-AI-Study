# Phase 5：示范数据接口与闭环评测（压缩）

> 状态：已完成（2026-08-31）  
> 前置条件：Phase 4 contact/geometry/scheduler/force Gate 通过  
> 优先级：中，论文接口型阶段  
> 建议节奏：2 个核心单元，每单元 45–75 分钟  
> 论文出口：读懂 trajectory 怎样成为 demonstration，并能区分离线指标、闭环 rollout 与真实任务成功率

## 1. 阶段核心问题

重定向得到的机器人轨迹如何变成可供策略学习或回放的数据？为什么一个模型在专家数据上预测动作很准，闭环执行时仍可能逐渐偏离并失败？

```text
retargeted robot trajectory + object/contact/force streams
  -> synchronized episode
  -> observation_t / action_t / terminal / valid mask
  -> one-step target or future action chunk
  -> offline replay metric
  -> closed-loop rollout under perturbation
  -> task predicate + failure category + success rate
```

Phase 5 不把 BC/ACT 当成新的大课程，而是建立阅读论文和运行 Phase 6 训练所需的最小数据与评测语言。

## 2. 与目标论文的关系

### DexTele

- 人体/机器人时序样本必须声明 joint order、frame、unit、timestamp 和 episode boundary；
- 网络输出要与 FK 后的 MPJPE、Quat、VE、AE 等指标对应，不能只报告训练 loss；
- graph retargeting 的小规模训练复现将在 Phase 6 完成，本阶段只准备 dataset/metric contract；
- arm、hand 两个输出流即使分别准确，也要检查同步、连续性和最终执行接口。

### ObjRetarget

- 输出是经初始化与约束优化后的可执行轨迹，可作为回放、遥操作或后续 skill-learning demonstration；
- MPJPE、Quat、Fréchet 描述轨迹相似性，slip、geometric consistency 和 task success 描述交互结果；
- 论文核心不是 ACT 训练，因此本阶段不会把通用策略训练强行当成 ObjRetarget 复现；
- 离线几何损失更小并不自动证明真实物体操作成功率更高。

## 3. 学习取舍

### 必学并实验

- `episode -> timestamp -> observation_t -> action_t -> next observation` 因果关系；
- observation、action、state、command、feedback 和 label 的区别；
- episode boundary、terminal、valid mask 与 padding mask；
- action chunk `[a_t, ..., a_{t+H-1}]` 的 shape、执行长度和重规划频率；
- BC 的监督学习接口，以及 covariate/distribution shift 为什么只在闭环中暴露；
- offline one-step error 与 closed-loop rollout success 的区别；
- MPJPE、Quat、VE、AE、Fréchet、slip、geometric consistency 和 task success 分别回答什么；
- ablation 必须保持数据、预算、随机种子和评测协议一致。

### 概念 + 一个例子

- ACT：用 Transformer 一次预测 action chunk，而不是本阶段训练完整模型；
- temporal ensembling：重叠 chunk 的动作怎样组合；
- open-loop playback、closed-loop policy 和 receding-horizon execution；
- ID/OOD、扰动测试、置信区间和失败类型统计；
- teacher forcing 与 rollout 输入分布差异。

### 暂不展开

- Transformer/ACT 架构推导与大规模调参；
- RoboTwin、VLA 或大型视觉编码器训练；
- DAgger、offline RL、diffusion policy 的完整课程；
- 数据采集硬件、ROS bag、真机安全部署；
- 大型 benchmark 下载和多 GPU 训练。

## 4. 环境与目录

继续使用 `eai-retarget`：NumPy、SciPy、Matplotlib、pytest。P5 的最小 BC 例子使用 NumPy 最小二乘或明确的小模型，不需要 CUDA；不新建 Conda 环境。

```text
learning/guide_phase05_demonstration_evaluation/
  README.md
  PROGRESS.md
  data/
  notes/
  outputs/
  src/
  tests/
```

统一 demonstration contract：

```text
episode_id                 scalar/string
timestamp                  [T]             s, strictly increasing per episode
observation.robot_q        [T,Nq]          rad, measured/available at time t
observation.object_pose    [T,7]           xyz + quat xyzw
observation.contact        [T,5]           bool
observation.force          [T,Nf]          declared force unit
action.robot_q_command     [T,Na]          command applied after observation_t
phase                      [T]             approach/contact/manipulate/release
terminal                   [T]             bool; exactly marks episode end
valid                      [T] or [T,...]   missing/padded data mask
success                    episode scalar  defined by frozen task predicate
termination_reason         episode scalar  success/failure/abort/system fault
```

因果约定必须明确：`observation[t]` 只能包含决策时刻已经可用的信息；`action[t]` 是随后发出的命令。不能把未来状态或成功标签泄漏进 observation。

## 5. 两个核心单元

### P5-1：Trajectory 到 demonstration 与 action chunk

核心问题：怎样把 Phase 3/4 的多条时间流整理成不会错位、不会跨 episode 泄漏的训练样本？

实验：

1. 构造两段短 episode，包含 robot state、object pose、contact/phase、force 和 command；
2. 验证 timestamp、shape、unit、joint order、terminal 和 episode boundary；
3. 生成单步样本 `observation[t] -> action[t]`；
4. 生成长度 `H` 的 action chunk `[a_t, ..., a_{t+H-1}]` 与 padding mask；
5. 故意演示三种错误：action 偏移一帧、chunk 跨 episode、把未来反馈放入 observation；
6. 输出 shape/时间对齐报告和样本时间线图。

产物：规范 demonstration arrays、chunk arrays、mask、contract violation 报告。

通过条件：能解释 action 为什么不能与错误时刻的 observation 配对，以及 padding mask 为什么不能当作真实零动作。

### P5-2：Offline error、distribution shift 与 rollout evaluation

核心问题：为什么专家数据上的一步动作 MAE 很低，闭环执行仍可能失败？

实验：

1. 用简单受控动力系统生成专家 demonstration；
2. 拟合最小 BC baseline，只验证 `observation -> action` 接口；
3. 在专家状态上计算 offline one-step error；
4. 从轻微扰动状态开始 closed-loop rollout，让策略消费自己的历史结果；
5. 比较 open-loop replay、closed-loop、短 action chunk 和滚动重规划；
6. 记录 trajectory error、terminal task success、failure frame 与 distribution-shift 图；
7. 用固定合成轨迹各计算一个 MPJPE/Quat/VE/AE/Fréchet/slip/geometric-consistency 示例，并说明不可互相替代。

产物：offline/rollout 对照表、失败轨迹图、论文指标速查笔记。

通过条件：能说明低 offline loss 为什么不是 deployment guarantee，以及 task success 为什么必须有明确 predicate、分母和 termination reason。

## 6. BC 与 ACT 的最低理解

### Behavior Cloning

```text
dataset: (observation_t, expert_action_t)
policy:  action_hat_t = pi(observation_t)
loss:    distance(action_hat_t, expert_action_t)
```

BC 在专家访问过的状态上学习；闭环偏离后，可能进入训练集中没有覆盖的状态，误差继续累积。

### Action Chunking / ACT

```text
pi(observation_t) -> [action_t, action_t+1, ..., action_t+H-1]
```

chunk 能建模短时动作结构并减少高层推理频率，但 chunk 太长会降低反馈纠错速度。执行时必须声明：一次执行完整 chunk，还是只执行前 `K < H` 步后重新规划。

## 7. 指标阅读框架

| 指标 | 主要回答 | 不能单独证明 |
|---|---|---|
| MPJPE | 关节/关键点位置是否接近参考 | 姿态、时间连续性、任务成功 |
| Quat distance | 朝向是否接近参考 | 位置和接触正确 |
| VE / AE | 速度/加速度动态是否接近或平滑 | 目标是否到达 |
| Fréchet | 两条曲线整体形状是否接近 | 时间同步、物理执行成功 |
| slip | 手—物相对滑移是否小 | 完整任务完成 |
| geometric consistency | 局部接触结构是否保持 | 力、摩擦、安全性 |
| task success | 冻结谓词下任务是否完成 | 轨迹自然、失败原因 |

任何结果都必须同时记录 metric definition、frame/alignment、unit、aggregation、trial denominator 和 failure handling。

## 8. 阶段 Gate

- [x] 能写出 demonstration 的 observation/action/timestamp/terminal contract；
- [x] 能区分 state、observation、action command 与 feedback；
- [x] 能构造 action chunk 和 padding mask，且不跨 episode；
- [x] 能解释 BC、ACT、chunk horizon 和 replanning interval；
- [x] 能解释 teacher-forced offline evaluation 与 closed-loop rollout 的输入分布差异；
- [x] 能说明低 offline loss 为什么不能替代 task success；
- [x] 能解释 MPJPE、Quat、VE、AE、Fréchet、slip、geometry 和 success 的侧重点；
- [x] 能为 success 写出 predicate、试验分母和 termination reason；
- [x] 能说明 Phase 5 与 DexTele/ObjRetarget 的直接关系及非复现内容。

Gate 通过后进入 Phase 6：论文综合与小规模复现。训练闭环优先使用 DexTele 官方代码和独立环境 `eai-dextele-repro`。

## 9. 当前入口

Phase 5 Gate 与阶段总结均已完成；下一步进入 Phase 6 论文综合与小规模复现。
