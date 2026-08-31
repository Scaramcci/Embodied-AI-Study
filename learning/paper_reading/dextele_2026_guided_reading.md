# DexTele 2026 加速导读

原文：`planning/01_teacher_papers/papers/DexTele_2026.pdf`

## Paper Pass 1：系统地图

### 论文问题

DexTele 同时解决两件事：人体动作怎样跨不同机器人拓扑重定向，以及灵巧手怎样针对不同物体自适应抓取力。

### 方法链

```text
外部相机图像
  -> FrankMocap 人体手臂/手部姿态
  -> 人体骨架图 [position, quaternion, edge]
  -> SAG-GCN 编码器/解码器 + 潜在空间优化
  -> 机器人手臂/手部关节命令
  -> VLM 识别物体并给出目标力先验
  -> 关节角—力预测模型 + 滚动在线优化
  -> 自适应抓取
```

### 五项地图

| 项目 | 当前答案 |
|---|---|
| Input | 外部 RGB 图像、人体手臂/手部姿态；抓取阶段还有物体图像、机器人关节反馈 |
| Representation | 人/机器人骨架图；节点 `[p,q]`，边 `p_j-p_i`；手臂/手部双流特征 |
| Retargeting | SAG-GCN 编解码与潜在空间优化，复合 loss 约束末端、方向、arm normal、动态和手指 |
| Force adaptation | VLM 目标力先验 + 关节角—力模型 + 带平滑正则的滚动优化 |
| Output/Evaluation | 多平台机器人关节动作和抓取力；评估重定向误差、跨平台能力和抓取表现 |

### 与 ObjRetarget 的第一处关键差异

- DexTele 的物体语义主要服务于“目标抓取力是多少”；
- ObjRetarget 的物体位姿与表面点云直接进入“手—物接触几何怎样保持”；
- 因而前者更突出跨平台图重定向与力闭环，后者更突出 object-aware 几何约束和接触阶段。

### 当前只需记住

我们已经完成 DexTele 图输入的最小结构：`G_k=(V_k,E_k,features)`、节点 `[p,q]` 和边向量。
归一化公式可以按需查阅，不再单独练习。进入 Phase 3 时重点回读复合重定向 loss 和潜在空间优化；
进入 Phase 4 时重点回读目标力、关节角—力模型和滚动优化。

## 小规模复现安排

- 官方项目页提供了公开代码仓库，具备训练入口、模型、配置、数据与测试代码；
- 完成 Phase 3 后新建隔离环境，先跑单 batch 的 forward/backward，再用固定小子集进行约 10–30 epoch 的短程训练；
- 必须保存子集清单、seed、配置、loss 曲线、checkpoint、评测结果、峰值显存和兼容补丁；
- 条件允许时只做一个受控消融，不复现 FrankMocap、真实机器人和全部平台；
- 详细步骤见 [`PAPER_REPRODUCTION_PLAN.md`](../../planning/03_embodied_ai_guide_learning/PAPER_REPRODUCTION_PLAN.md)。

复现性质：作者代码的小规模训练复现。目标是走通实战流程，不把缩小结果等同于论文完整结果。

## Phase 3 回读：重定向 loss 与本项目证据

本项目已用数值实验建立 `human reference -> robot q -> FK -> composite loss -> metrics` 链：

- `L_ee/L_ori` 对应腕部位置与方向任务；
- `L_norm` 对应肩—肘—腕平面法向，解决末端相同但翻肘的问题；
- `L_d` 对应跨帧动态/平滑约束，解决逐帧精确但分支切换的问题；
- joint bounds 负责排除数值可行但物理越界的输出。

边界：当前 wrist error 不等于全关节 MPJPE，关节差分也不等于论文 VE/AE；尚未验证 SAG-GCN、SBB、GRB 或双流消融。详细映射见 [`P3_PAPER_MAPPING.md`](../guide_phase03_motion_retargeting_optimization/notes/P3_PAPER_MAPPING.md)。
