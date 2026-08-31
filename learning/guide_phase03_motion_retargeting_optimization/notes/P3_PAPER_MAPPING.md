# Phase 3：实验到论文方法的映射

> 目的：区分“相同的数学/物理作用”与“已经复现论文实现”。本阶段验证的是重定向核心机制，不宣称复现 DexTele 网络或 ObjRetarget 完整系统。

## 1. 共同计算链

```text
human observation / reference
    -> semantic target or graph representation
    -> robot q candidate
    -> robot FK(q)
    -> task / morphology / temporal losses
    -> constraints and optimization or learning
    -> FK, continuity and execution metrics
```

本项目三个实验分别覆盖：

| 实验 | 直接结论 |
|---|---|
| P3-1 joint-copy vs task-space | 人体 `q` 无法按索引迁移；必须先声明要保留的任务语义 |
| P3-2 arm-plane/smoothness | 腕部任务无法唯一决定冗余肘部；空间先验与时间正则作用不同 |
| P3-3 frame-wise vs whole trajectory | 单帧 FK 成功不保证分支连续、速度/加速度合理 |

## 2. 映射到 DexTele

DexTele 的主链为：

```text
human skeleton graph G
  -> SAG-GCN encoder / latent representation
  -> decoder predicts robot joint angles theta
  -> FK K(theta) gives robot motion S
  -> composite retargeting loss
```

复合目标：

```text
L_ret = lambda_ee   L_ee
      + lambda_ori  L_ori
      + lambda_norm L_norm
      + lambda_d    L_d
      + lambda_fin1 L_fin1
      + lambda_fin2 L_fin2
```

对应关系：

| DexTele 项 | 本阶段对应 | 防止的失败 |
|---|---|---|
| `L_ee` | P3-1/P3-3 wrist position task | 末端没有到达示范目标 |
| `L_ori` | P3-1/P3-3 wrist orientation task | 位置正确但腕部方向错误 |
| `L_norm` | P3-2 arm-plane normal | 翻肘、异常弯曲和全臂形态不自然 |
| `L_d` | P3-2/P3-3 temporal difference | 相邻帧抖动、速度/加速度过大 |
| joint bounds | 三个实验的 bounds/margin | 输出超过物理关节范围 |
| finger losses | Phase 4 再处理 | 手指方向/角度与抓取不一致 |

关键差异：本项目直接把 `q[0:T]` 当作数值优化变量；DexTele 主要学习图编码器/解码器参数并输出机器人 `theta`。两者共享 `q -> FK -> loss` 语义，但不是同一个求解器或实现。

指标边界：

- 本项目 wrist position error 只检查末端，不等于跨全部关节平均的 MPJPE；
- 本项目 wrist orientation error 与 Quat 作用相近，但维度/平均方式未复刻论文；
- adjacent `q`、joint velocity/acceleration 用于诊断可执行性，不等于论文基于关节空间位置导数定义的 VE/AE；
- 尚未验证 SAG-GCN、SBB、GRB、双流融合和跨平台泛化。

## 3. 映射到 ObjRetarget

ObjRetarget 手臂部分是两阶段：

```text
initial retargeted trajectory
    -> optimize q[0:T]
       with L_task + lambda_p L_plane + lambda_s temporal smoothness
    -> refined arm trajectory
```

对应关系：

| ObjRetarget 项 | 本阶段对应 | 已验证的作用 |
|---|---|---|
| initial trajectory | P3-1 joint-copy/task-space baseline；P3-3 warm start | 合理初值帮助留在连续解分支 |
| `L_task` position | P3-1/P3-3 FK position residual | 保持腕部任务精度 |
| `L_task` SO(3) orientation | P3-1/P3-3 二维方向 residual | 位置与方向必须分别约束；尚未复刻 SO(3) log |
| `L_plane` | P3-2 normal alignment | 相同腕部任务下选择合理弯曲方向 |
| `||q(t)-q(t-1)||²` | P3-2/P3-3 smoothness | 抑制 branch flip 和大幅相邻变化 |
| joint constraints | bounds/margin 检查 | 防止数值可行但物理越界 |
| object/contact geometry | Phase 4 | 尚未纳入当前手臂优化 |

关键差异：P3-2 使用合成 elbow swivel reference，未复刻论文由手腕运动趋势构造的 task-adaptive reference normal 与自适应权重 `w(t)`；P3-3 是二维解析模型，没有真实机器人碰撞、动力学和控制误差。

## 4. 受控消融结论

P3-2 保持肩部、腕部、连杆长度和输入轨迹完全相同，只改变 loss 权重：

| 设置 | mean plane error | max elbow change | 结论 |
|---|---:|---:|---|
| task only | 43.6110 deg | 379.9521 mm/frame | 腕部为零误差仍可严重翻肘 |
| plane only | 0 deg | 15.6439 mm/frame | 空间结构准确，但严格跟随参考变化 |
| plane + smooth | 2.7118 deg | 10.5258 mm/frame | 少量结构误差换取更连续动作 |
| over-smooth | 8.7123 deg | 5.8943 mm/frame | 最平滑，但开始压制必要构型变化 |

因此不能只报告总 loss；必须分别报告任务精度、拟人结构和时间质量。权重变化表达的是任务折中，不是“越大越好”。

## 5. 当前复现边界与下一阶段接口

本阶段已经具备阅读两文重定向部分的最低能力：

- 能追踪优化变量、FK、loss 和 constraint；
- 能预测删除 task/plane/smoothness 后的具体失败；
- 能区分学习映射、逐帧 IK、warm start 与整段优化；
- 能判断论文指标是否真的支持其方法主张。

尚未覆盖：

- DexTele 官方 SAG-GCN 训练与 checkpoint/评测；
- ObjRetarget object-relative/polyhedral hand loss；
- contact force、摩擦、真实双臂/灵巧手控制。

下一步：Phase 4 学习 contact event -> contact region -> polyhedral geometry -> contact force；同时按论文复现计划开始 DexTele R0/R1 仓库与单 batch 审计。

