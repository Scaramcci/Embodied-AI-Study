# Phase 5 总结：示范数据接口与闭环评测

> 完成日期：2026-08-31  
> 状态：压缩 Gate 通过

## 1. 已回答的核心问题

重定向轨迹只有在 episode、时间戳、因果方向和字段语义明确后，才能成为可用于回放、行为克隆或 action-chunk 策略的数据。模型在专家帧上的离线误差很低，只说明它会处理专家访问过的输入；真实部署必须让策略消费自己动作造成的下一状态，并用闭环 rollout 和冻结的任务谓词评价。

```text
retargeted trajectory + object/contact/force streams
  -> synchronized episode contract
  -> observation_t -> action_t -> observation_t+1
  -> one-step action or future action chunk
  -> masked offline loss
  -> closed-loop ID/OOD rollout
  -> trajectory/contact metrics + task predicate + failure reason
```

## 2. P5-1：Demonstration contract 与 action chunk

### 核心接口

每个控制周期遵循：

```text
observation[t]
  = 当前可获得的 q_feedback、object pose、contact、force、phase
      -> policy/controller decision
action[t]
  = 随后发出的 q_command
      -> robot/environment evolves
observation[t+1]
  = 执行后的新反馈
```

`q_feedback[t]` 是当前实测状态，`q_command[t]` 是即将执行的命令。二者即使 shape 相同也不能混为一谈；未来反馈、最终成功标签或执行后图像不能泄漏进当前 observation。

### 实验数据

- 两个独立 episode，共 16 帧，长度分别为 9 和 7；
- 采样率 10 Hz，关节顺序为 `shoulder/elbow/wrist`；
- `observation q` 与 `action command` 均为 `[16,3]`；
- object pose 为 `[16,7] = xyz + quaternion xyzw`；
- 五指 contact/force 为 `[16,5]`；
- terminal global indices 为 `[8,15]`，下一行不能被当作同一 episode 的后继状态。

### Action chunk

长度 `H=4` 的 chunk：

```text
pi(observation_t) -> [action_t, action_t+1, action_t+2, action_t+3]
```

得到：

```text
action_chunk      [16,4,3] = [T,H,Na]
padding_mask      [16,4]   = [T,H]
valid / padded              = 52 / 12
```

第一段 episode 的 global frame 7 只能取得 local frame `[7,8]`：

```text
source = [7, 8, -1, -1]
mask   = [T, T, F, F]
```

padding 表示“没有动作”，不是物理零命令。masked loss 只能统计有效项：

```text
L = sum(mask * action_error) / sum(mask)
```

### 被拒绝的错误

- action timestamp 偏移一帧：把 `observation[t]` 与错误时刻的 action 配对；
- future feedback leakage：当前决策使用未来才可获得的信息；
- naive chunk cross episode：把下一次任务的起始动作拼到当前任务末尾；
- missing padding mask：把存储用零值误当成真实专家命令。

## 3. P5-2：Offline error、distribution shift 与 rollout

### 最小 BC 实验

任务使用一维末端位置 `x`、目标 `g` 和速度动作 `u`。专家控制器是：

```text
e = g - x
u_expert = clip(0.35 e + 8 e^3, -1.5, 1.5)
```

36 段训练 episode、1116 个样本只覆盖：

```text
goal error in [-0.07823, 0.07940] m
```

线性 BC 学到：

```text
u_BC ~= -0.369 x + 0.369 goal ~= 0.369 e
```

它在目标附近拟合很好：offline action MAE 为 `0.000270 m/s`，最大误差仅 `0.002500 m/s`。但训练集没有提供大偏差下的非线性强恢复行为。

### 闭环结果

成功谓词冻结为：最后连续 10 帧的绝对目标误差均不超过 2 cm。

| Rollout | 初始/最终误差 | 轨迹 RMSE | 分布外帧 | Success |
|---|---:|---:|---:|---:|
| expert OOD | 0.8000 / 0.0120 m | 0.1629 m | 35.4% | True |
| BC ID | 0.0500 / 0.0027 m | 0.0206 m | 0.0% | True |
| BC OOD | 0.8000 / 0.0407 m | 0.3292 m | 77.0% | False |

结论：`0.000270 m/s` 的 teacher-forced offline MAE 与失败的 OOD rollout 可以同时成立。离线评测每一帧都重新提供专家 observation；闭环策略的下一帧输入则由它自己的上一步动作产生。策略一旦偏离并进入训练未覆盖状态，误差会改变后续输入分布。

## 4. Action chunk 与反馈速度

实验使用 20 Hz 控制和 `H=8`：完整 chunk 持续 0.4 s。在 state frame 37 注入 `-0.20 m` 外部扰动：

- 每步重规划在 action frame 37 立即响应；
- 完整 chunk 只在边界 `0,8,16,24,32,40,...` 重规划，到 frame 40 才响应；
- 额外延迟 3 帧，即 0.15 s。

chunk 越长，短期动作结构和推理效率通常越好，但对碰撞、滑移、物体移动等新反馈的纠错越慢。执行协议必须声明 `chunk horizon H` 与 `replanning/execution interval K`；预测 8 步不代表必须盲目执行 8 步。

## 5. 论文式指标示例

BC OOD 与专家 OOD 的教学对照得到：

| 指标 | 结果 | 主要回答 |
|---|---:|---|
| MPJPE | 102.296 mm | 各关节位置逐帧平均偏差 |
| mean Quat distance | 0.06395 rad，约 3.66 deg | 平均方向差异 |
| velocity error | 0.0579 m/s | 速度序列与参考的差异 |
| acceleration error | 0.1155 m/s² | 加速度/动态节奏与参考的差异 |
| discrete Fréchet | 0.0358 m | 两条空间曲线整体形状差异 |
| cumulative slip | 17.562 mm | 物体在手部局部坐标系中的累计相对移动 |
| normalized geometry error | 3.167% | 局部接触结构相对误差 |
| task success | False | 冻结任务谓词是否满足 |

其中 slip 与 geometry 是独立构造的接触指标示例，不是该一维动力系统产生的真实接触物理。

### 不能互相替代

- MPJPE 小不保证 orientation、smoothness 或 contact 正确；
- Quat 小不保证末端位置正确；
- VE/AE 小不保证目标到达，完全不动也可以很“平滑”；
- Fréchet 小不保证逐帧时间同步或物理成功；
- slip 小不保证物体被放到正确目标；
- geometry error 小不保证力、摩擦和稳定性；
- success 高不自动说明轨迹自然，仍要报告失败类型、安全中止和质量指标。

## 6. 评测层级

```text
离线拟合层
  action loss, MPJPE, Quat, VE, AE

轨迹与接触层
  Fréchet, slip, geometric consistency

闭环任务层
  rollout success, failure category, recovery, safety termination
```

有说服力的系统评测应同时回答：模型是否拟合了目标映射、闭环是否发生误差积累、交互是否稳定、最终任务是否完成。

## 7. 论文映射

### DexTele

- 数据必须声明 body/hand joint order、frame、unit、timestamp 和 episode boundary；
- arm/hand 网络的训练 loss 不能替代 FK 后的 MPJPE、Quat、VE、AE；
- 两个输出流分别准确也不保证同步协调，仍需闭环或执行评测；
- Phase 6 官方代码复现将继承本阶段的 dataset、checkpoint、offline evaluation 和 rollout 区分。

### ObjRetarget

- 优化后的机器人轨迹可作为回放或后续 skill-learning demonstration；
- MPJPE、Quat、Fréchet 衡量轨迹参考一致性；
- slip、geometric consistency 和 task success 衡量接触与任务结果；
- ObjRetarget 核心是结构化重定向与接触优化，不应把通用 ACT 训练强行当作论文复现。

## 8. 复现实验规则

- 固定 dataset split、输入字段、时间对齐、随机种子和 checkpoint；
- offline metric 与 closed-loop rollout 分开报告；
- success 必须声明 predicate、trial denominator、timeout 与 termination reason；
- ID/OOD 和扰动条件在测试前冻结，不能根据结果临时放宽；
- ablation 只改变目标组件，数据预算和评测协议保持一致；
- 报告 failure、abort、invalid trial 与负结果，不只展示成功视频；
- 训练结果必须区分作者论文数值和本机缩小复现数值。

## 9. Gate

- [x] 写出 demonstration 的 observation/action/timestamp/terminal contract；
- [x] 区分 state、observation、action command 与 feedback；
- [x] 构造 action chunk 和 padding mask，且不跨 episode；
- [x] 解释 BC、ACT、chunk horizon 和 replanning interval；
- [x] 解释 teacher-forced offline evaluation 与 closed-loop rollout 的输入分布差异；
- [x] 说明低 offline loss 为什么不能替代 task success；
- [x] 解释 MPJPE、Quat、VE、AE、Fréchet、slip、geometry 和 success 的侧重点；
- [x] 为 success 写出 predicate、试验分母和 termination reason；
- [x] 说明 Phase 5 与 DexTele/ObjRetarget 的直接关系及非复现内容。

## 10. 下一步

进入 Phase 6：完成 DexTele 与 ObjRetarget 的方法、输入、优化变量、控制与评测对比；优先审计 DexTele 官方代码，在独立 `eai-dextele-repro` 环境中走通小数据、短 epoch、checkpoint、离线评测和一个受控消融。ObjRetarget 继续使用 Phase 3/4 已完成的方法级实验，若仍无官方代码则不虚构完整复现。
