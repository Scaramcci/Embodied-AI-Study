# 论文优先加速路线

> 生效日期：2026-08-30  
> 状态：当前执行版本  
> 原因：开学临近，需要尽快具备阅读 DexTele 与 ObjRetarget 的方法地图，基础知识改为按论文需求补齐。

## 1. 执行原则

后续不再追求依次完成一门完整的具身智能基础课，而采用“双轨并行”：

```text
论文轨：立即粗读论文，先建立 problem -> input -> method -> output -> evaluation 地图
技术轨：只在论文出现理解障碍时，补对应机器人/具身概念与最小实验
```

知识分为三档：

| 优先级 | 学习方式 | 内容 |
|---|---|---|
| A：核心 | 讲清物理/几何意义，并做最小实验 | 人机拓扑差异、重定向目标、arm-plane、关节限位与平滑约束、物体相对几何、接触保持、整段轨迹优化、力反馈与滚动优化 |
| B：接口 | 一个概念 + 一个例子 | palm + five fingertips、6D pose、local/world cloud、timestamp 对齐、contact event、BC/ACT 接口、论文指标 |
| C：按需 | 只保留速查笔记，不设独立练习或 Gate | 中心化/标准化、NaN/缺失值、异常检测、confidence 阈值、通用线性插值、schema 样板、绘图与测试样板 |

判断标准：如果一个知识点可以用常规机器学习数据处理经验快速查明，而且不改变机器人几何、约束或执行结果，就不占用主线实验时间。

## 2. 从现在开始的论文轨

不等待 Phase 2–5 完成，立即开始两篇论文第一遍。

### Paper Pass 1：系统地图

每篇只读标题、摘要、Figure 1/2、方法总览、实验表和结论，回答：

```text
问题是什么？
输入是什么？
中间表示是什么？
优化/学习变量是什么？
输出给谁执行？
用什么指标和消融证明有效？
```

- ObjRetarget：沿用 [`learning/paper_reading/objretarget_2026_guided_reading.md`](../../learning/paper_reading/objretarget_2026_guided_reading.md)，下一步读 Figure 2 reference plan generation。
- DexTele：优先建立 perception -> graph retargeting -> arm/hand command -> adaptive force control 地图。

### Paper Pass 2：随技术阶段回读

- Phase 2 回读 perception/reference-plan 输入；
- Phase 3 回读 retargeting、loss、constraint 与 ablation；
- Phase 4 回读 contact geometry、force model、controller 与 rolling optimization；
- Phase 5 回读 demonstration/evaluation，不扩展成完整模仿学习课程。

### Paper Pass 3：最终综合

最后才做逐公式核对、两文对比、复现缺口和最小消融，不再承担“第一次读论文”的任务。

## 3. Phase 2 剩余内容：压缩为两次主线学习

已完成并保留：数据契约、相机内外参、RGB-D 反投影、camera/world frame、上肢 skeleton graph。

降为可选参考：现有中心化/尺度归一化脚本；不再要求运行，也不作为 Gate。missing/NaN、confidence、异常值和通用插值不再建立独立实验。

### P2-A：物体与手的任务几何

必须掌握：

- palm + five fingertips 为什么比完整复制人体手指关节角更适合跨形态接触表示；
- `world_T_object`、`object_cloud_local` 与 `object_cloud_world[t]`；
- 为什么 object category、2D box 或 mask 单独不足以支持三维接触重定向。

最小证据：把一个物体局部点云随 6D pose 变换到世界系，并同时显示掌心/五指指尖。

### P2-B：接触事件与论文输入包

必须掌握：

- 指尖到物体表面的最近距离；
- contact event 与 contact geometry 的区别；
- 人手、物体必须在同一 frame、相近 timestamp 后才能计算距离；
- 时间对齐、置信度和缺失只讲接口与一个失败例子。

最小证据：一段手靠近物体的短序列，输出 fingertip distance、contact/non-contact phase 和一个 timestamp 偏移造成的误判。

Phase 2 不再单独做原 Unit 6 大型综合数据包；P2-A/P2-B 的输出就是下游接口。

## 4. Phase 3：最高优先级——重定向与轨迹优化

建议 4 次学习，是后续时间投入最多的阶段。

### P3-1：重定向问题与人机差异

- 人和机器人 joint/DoF/link length/topology 为什么不能直接复制；
- task-space、joint-space、object-relative representation；
- 用 Phase 1 IK/FK 构造一个最小 geometric retargeting baseline。

### P3-2：论文中的目标函数

围绕优化变量 `q[0:T]` 理解：

```text
end-effector position/orientation
+ limb direction / arm-plane
+ joint limit
+ temporal smoothness
+ object-relative/contact constraint
```

不复习通用梯度下降或矩阵求导；只说明每项 loss 惩罚什么失败行为、单位怎样配平、权重变化会发生什么。

### P3-3：逐帧 IK 与整段优化

- 为什么逐帧 IK 成功仍可能抖动、翻肘或破坏接触；
- 整段轨迹优化怎样同时利用前后帧；
- warm start、冗余解、可达性与失败帧保留。

### P3-4：论文方法映射与消融

- DexTele：图表示/学习映射解决什么，人机尺度与拓扑怎样处理；
- ObjRetarget：arm-plane、末端、平滑与物体感知约束怎样组合；
- 最小消融：去掉 smoothness、joint limit、arm-plane 或 object-relative 项，观察具体失败。

阶段证据：同一条参考动作经 baseline 与约束优化后，对比 FK 误差、平滑性、限位余量、arm-plane 或物体相对误差。

## 5. Phase 4：高优先级——手物接触与力调节

建议 3 次学习。

1. ObjRetarget 接触几何：contact point/region、掌心—指尖—物体局部多面体、边长与相对位姿不变量；做一个小型 polyhedral/contact-geometry 实验。
2. 接触阶段与双臂/双手同步：approach、contact、manipulate、release；理解为什么 arm 与 hand 解耦优化。
3. DexTele 力调节：目标抓取力、关节角—力预测、反馈修正、滚动/在线优化；只做简化数值闭环，不推完整 MPC，不涉及硬件制作。

摩擦锥、接触动力学和阻抗控制只讲到能读论文；若论文公式需要再补，不展开完整课程。

## 6. Phase 5：压缩——示范数据与评测

建议 1–2 次学习。

- 重定向结果怎样组成 `observation/action/trajectory` demonstration；
- BC、ACT/action chunk、distribution shift 各用一个例子解释；
- 重点实现/读懂论文真正使用的指标、成功率、消融和 rollout 评测；
- 不要求训练大型 ACT、RoboTwin 或 VLA，除非老师明确要求复现训练。

## 7. 论文小规模复现轨：训练闭环优先

硬件基线为 32 GB RAM + RTX 4090 Laptop（16 GB VRAM），足够开展缩小后的训练和方法实验。详细执行见[论文小规模复现计划](PAPER_REPRODUCTION_PLAN.md)。

- **主项目 DexTele**：官方公开了代码，完成 Phase 3 后使用固定小数据子集走通前向、反向传播、短程训练、checkpoint、评测和一个受控消融。
- **次项目 ObjRetarget**：当前官方页面没有代码入口；完成 Phase 3/4 后自行实现 arm-plane/平滑约束和简化接触多面体实验，明确标注为方法级复现。
- 不追求全部机器人平台、完整数据规模或论文原数值；优先获得可重复的完整实战流程。
- Phase 6 前复查 ObjRetarget 是否发布代码，并根据审计结果决定是否追加官方实现。

## 8. Phase 6：论文综合，而不是论文起点

建议 2 次学习：

1. 画出 DexTele 与 ObjRetarget 的完整方法图，制作 input/representation/optimization/control/evaluation 对比表；
2. 核对关键公式、指标、实验设置与消融结论，整理 DexTele 小规模训练和 ObjRetarget 方法级实验；至少提交一份包含环境、数据清单、checkpoint、评测与局限的复现报告。

## 9. 加速 Gate

不再要求“一个阶段所有概念都练过”才能前进。只检查阻塞论文理解的核心能力：

- Phase 2：能把 hand/object 放到同一 frame，并解释 local/world cloud 与 contact distance；
- Phase 3：能读懂优化变量、主要 loss/constraint，并解释消融后会出现的机器人失败；
- Phase 4：能区分 contact event、contact geometry、contact force，并解释反馈闭环；
- Phase 5：能说明 demonstration 字段和离线 loss 与真实 rollout 成功率的差异；
- 复现轨：至少有一个项目走通训练或优化、保存结果、重新评测的闭环；
- Phase 6：能独立讲清两篇论文的方法链、差异、证据、复现结果和局限。

## 10. 当前下一步

1. 不再要求运行 Unit 3 normalization 脚本；把公式作为速查即可。
2. 立即开始 Paper Pass 1，同时完成 P2-A 的 object local/world cloud 与 palm/fingertip 几何。
3. P2-B 完成后直接进入 Phase 3，不再追加通用数据清洗实验。
4. 当前只记录 DexTele 仓库结构；完成 Phase 3 后再创建隔离复现环境并启动小规模训练。
