# Phase 4 总结：手—物接触、阶段调度与力调节

> 完成日期：2026-08-31  
> 状态：加速 Gate 通过

## 1. 已回答的核心问题

机械臂把手腕送到目标位姿以后，系统还需要判断何时接触、接触在哪里、局部手型是否保持、当前处于哪一个操作阶段，以及抓力是否达到目标。完整链路是：

```text
fingertips + object cloud + timestamps
  -> contact event / region / representative point
  -> palm-fingertip-neighbor-contact local geometry
  -> approach/contact/manipulate/release scheduler
  -> normal or geometry-refined hand command
  -> force target + command/feedback force surrogate
  -> rolling command update + new feedback
```

必须区分五个层级：

| 层级 | 回答的问题 | 本阶段边界 |
|---|---|---|
| contact event | 当前是否足够接近或已经接触？ | 距离阈值只是近似观测 |
| contact region/point | 指尖靠近物体表面哪里？ | 邻域质心不等于真实接触压力中心 |
| contact geometry | 手掌、指尖、相邻指尖和物体怎样相对排列？ | 几何正确不证明抓取稳定 |
| contact force | 抓力是否接近目标？ | 合成 surrogate，不是真实传感器 |
| friction/dynamics | 会不会滑动、滚动、失稳？ | 本阶段只讲概念，不做高保真验证 |

## 2. P4-1：Contact region 与局部多面体几何

### 表示

对第 `f` 根指尖 `p_f`，从物体点云中提取半径 `r` 内的邻域：

```text
C_f = {o_j | ||o_j - p_f|| <= r}
c_f = mean(C_f)
```

以邻域质心 `c_f` 作为代表接触点。每根手指构造四顶点单元：

```text
palm, current fingertip, adjacent fingertip, object contact point
```

四点形成六条边；五根手指得到五个局部单元组成 polyhedral cluster。

### 实验结论

- 五根手指分别提取到 `24/23/23/23/24` 个邻域点，代表接触距离约 3 mm；
- 整套手—物结构施加相同刚体运动后，世界坐标变化约 0.979 m，但 edge-length、hand-local edge 和 hand-local contact pose 的变化均约为 `1e-16 m`；
- raw world-frame edge vector 因整体旋转改变约 70.0 mm，说明世界系向量并不天然具有全局旋转不变性；
- 局部扰动指尖和接触点后，三类描述分别产生约 `5.173/5.675/4.033 mm` RMSE，能够检测真实局部接触结构变化。

核心判断：全局刚体运动不应改变接触语义，局部手型或接触点畸变应产生损失。边长天然刚体不变；向量差若要跨全局姿态比较，必须先对齐 frame 或转入 hand-local frame。

## 3. P4-2：接触阶段与 arm/hand 同步

### 两层状态逻辑

```text
distance observation
  -> contact detector: contact / non-contact
  -> task scheduler: approach / contact / manipulate / release
  -> active controller and command
```

接触检测使用滞回：距离小于 7 mm 才进入接触，大于 11 mm 才退出；切换后至少驻留 8 帧。任务状态机在接触建立后先停留 10 帧，再从 `contact` 进入 `manipulate`。

### 实验结论

- 8 mm 单阈值因距离噪声产生 10 次控制器切换，总命令变化 2.1627 rad；
- hysteresis + minimum dwell 只在进入/退出时切换两次，总命令变化降至 0.5621 rad；
- 稳健调度仍有约 0.2100 rad 最大单步变化，因为硬切换没有消除那一次必要交接；真实系统还需要 command blending、rate limit 和 controller state transfer；
- 将手/物体流延迟 5 帧，即 0.167 s，接触转换从 `[46,112]` 变成 `[51,117]`；
- 三个 phase boundary 各错五帧，得到 15 个 phase mismatch；`contact` 与 `manipulate` 使用同一几何控制器，所以真正 wrong-controller 只有进入/退出附近的 10 帧。

核心判断：滞回抑制阈值 chatter，但不能修复 timestamp misalignment。arm、hand、object observation 和 controller command 必须使用同一时钟与 phase state。

## 4. P4-3：目标力与滚动命令调节

### 闭环

本实验用固定表模拟语义力先验：`plastic_bottle -> 8 N`，再使用明确可微的合成模型：

```text
F_hat = M(q_command, q_feedback)
```

每个周期求解：

```text
min_q  (M(q, q_feedback) - F_target)^2
       + lambda * (q - q_previous_command)^2
```

只执行当前求出的命令，读取新的反馈角和测量力，再滚动求解。`q_command` 是控制器期望角，`q_feedback` 是执行器实际角；由于响应延迟，两者不能混为一谈。

### 实验结论

| Case | 全程/末30帧 force MAE | Overshoot | 最大命令步长 | 稳定时间 `+/-0.5 N` | 结论 |
|---|---:|---:|---:|---:|---|
| no adjustment | 4.0438 / 4.0094 N | 0 N | 0 rad | 未稳定 | 没有过冲只是因为始终抓力不足 |
| weak regularization | 0.2663 / 0.0482 N | 2.6360 N | 0.4000 rad | 0.433 s | 快，但命令激进且过冲大 |
| balanced | 0.2975 / 0.0482 N | 0.4925 N | 0.0464 rad | 0.567 s | 小幅牺牲速度，大幅改善平滑与过冲 |
| over-regularized | 1.3635 / 0.3318 N | 0 N | 0.0062 rad | 2.867 s | 过于保守，抓力建立太慢 |

正则权重依赖损失量纲、归一化、执行器和物体，`1200` 只对当前合成实验有意义，不能直接迁移到真实机器人。

## 5. 论文映射

### ObjRetarget

- `C_f` 和质心 `c_f` 对应逐指接触区域与代表接触点；
- palm、current fingertip、adjacent fingertip、contact point 对应局部四顶点单元；
- edge 与 hand-local contact-pose 描述对应保持局部接触结构的 hand loss；
- non-contact 使用初始化手轨迹，contact 时切入几何优化命令，对应本阶段 scheduler；
- 本实验是方法级简化，没有复刻完整手模型、检测管线、优化器和真实执行。

特别注意：论文文字称 edge-length，但公式若直接比较 edge vector，则它并非对全局旋转不变；只有参考与机器人 frame 已对齐，或先转入共同局部 frame 时，比较才成立。

### DexTele

- 物体语义到 `F_target` 对应 VLM 给出的目标力先验；
- `(q_command, q_feedback) -> force` 对应角度—力预测模型；
- force error 与 command regularization 对应在线命令修正目标；
- `feedback -> optimize -> command -> new feedback` 对应滚动闭环；
- 本实验未调用 VLM、随机森林、真实力传感器或灵巧手。若论文实现使用随机森林，不能无说明地假设它能像普通神经网络一样直接反向传播，复现时必须审计其实际优化方式。

## 6. 失败模式与评价原则

- 指尖距离小不代表接触几何正确；
- 接触几何正确不代表力、摩擦或抓取稳定性正确；
- 世界坐标明显变化不代表接触语义变化；
- contact boolean 正确不代表 task phase 正确；
- 单模块准确不代表多流时间同步；
- overshoot 为零不代表控制成功，也可能一直低于目标；
- command 很平滑不代表任务完成，也可能响应过慢；
- semantic/VLM force target 是先验，不是安全认证或底层电机命令；
- 离线 surrogate 误差小不保证闭环执行稳定，必须看 rollout 指标。

## 7. Gate

- [x] 区分 contact event、region/point、geometry、force 和 friction；
- [x] 从点云邻域得到代表接触点并解释质心边界；
- [x] 构造 palm/fingertip/neighbor/contact 四顶点单元；
- [x] 解释 pairwise geometry、hand-local pose 与 global pose；
- [x] 指出 raw world edge vector 不具有全局旋转不变性；
- [x] 解释 hysteresis、minimum dwell、phase scheduler 和 controller handoff；
- [x] 解释 timestamp offset 为何导致 arm/hand 错误交接；
- [x] 写出 target force、surrogate、command regularization 与 rolling feedback 链；
- [x] 解释 force error、overshoot、oscillation、command step 和 settling time；
- [x] 映射到 ObjRetarget contact loss 与 DexTele force adaptation，并明确简化边界。

## 8. 下一步

进入压缩 Phase 5：只学习论文需要的 demonstration/observation/action 数据接口、BC/ACT/action chunk、distribution shift 和 rollout evaluation。大型训练不在 Phase 5 展开；训练实战集中到 Phase 6 的 DexTele 官方代码小规模复现。
