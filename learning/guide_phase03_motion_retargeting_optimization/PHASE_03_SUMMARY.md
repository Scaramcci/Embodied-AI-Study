# Phase 3 总结：动作重定向与轨迹优化

> 完成日期：2026-08-31  
> 状态：加速 Gate 通过

## 1. 已回答的核心问题

动作重定向不是把人体关节数组复制给机器人，而是在不同 link length、DoF、joint axis、topology 和 limits 下，先声明要保留的任务语义，再通过机器人自身的 FK、loss 与约束求合法 `q[0:T]`。

```text
human reference
  -> root/frame/scale and semantic target
  -> robot q candidate
  -> FK(q)
  -> task + morphology + temporal losses
  -> bounds / optimization
  -> trajectory metrics and failure report
```

## 2. 三个实验结论

### P3-1：joint-copy 与 task-space

- 人体 2 DoF、机器人 3 DoF，按索引复制必须武断地补 `q3=0`；
- joint-copy 方向误差可为零，但腕部位置平均误差约 170.6 mm；
- task-space 有界数值 IK 将腕部位置/方向误差降到数值精度范围；
- 腕部任务正确仍不保证机器人肘部或完整手臂形态像人。

### P3-2：arm-plane 与 smoothness

- task-only 在腕部零误差下仍产生 43.61 deg 平均 plane error 和 379.95 mm/frame 最大肘部跳变；
- plane-only 消除弯曲方向误差，但严格跟随参考变化；
- plane+smooth 以 2.71 deg 平均 plane error 换取更连续的肘部运动；
- over-smooth 最平滑，但 plane error 增至 8.71 deg，说明正则权重不是越大越好。

### P3-3：逐帧 IK 与整段优化

- 独立 IK 每帧 FK 零误差，但发生 7 次 elbow branch flip，最大相邻 `q` 变化 2.958 rad；
- warm start 保持同一分支，将最大变化降至 0.04125 rad；
- whole-trajectory optimization 用最大 0.1364 mm / 0.0450 deg 微小任务误差进一步改善速度、加速度和相邻变化；
- 单帧成功、分支连续、整段时间质量和控制执行必须分别评价。

## 3. 论文映射

- DexTele：`L_ee/L_ori/L_norm/L_d` 分别对应任务位置、方向、arm-plane 和动态连续性；网络学习映射与本项目直接优化 `q` 的求解变量不同。
- ObjRetarget：`L_task + lambda_p L_plane + lambda_s ||q(t)-q(t-1)||²` 与本阶段实验直接对应；task-adaptive normal、SO(3) log 和物体接触仍未复刻。
- 本项目 wrist error 不等于 MPJPE，二维方向不等于完整 Quat，joint angular velocity/acceleration 不等于论文 VE/AE。

详细边界见 [`notes/P3_PAPER_MAPPING.md`](notes/P3_PAPER_MAPPING.md)。

## 4. Gate

- [x] 解释人体 `q` 为什么不能按索引复制给不同机器人；
- [x] 区分 joint-space、task-space、graph/geometric 与 object-relative 表示；
- [x] 写出 `q -> FK(q) -> loss` 优化链；
- [x] 解释 task、orientation、plane、limit 与 smoothness 的作用和折中；
- [x] 计算并解释 arm-plane normal；
- [x] 区分独立 IK、warm start 与 whole-trajectory optimization；
- [x] 使用固定输入完成 plane/smoothness 受控消融；
- [x] 将实验映射到 DexTele 与 ObjRetarget，并明确未复现部分。

## 5. 下一步

进入 Phase 4：从 contact event 进入 contact region、object-relative/polyhedral contact geometry，再学习 DexTele 的目标力、角度—力模型与滚动优化。同时启动 DexTele 官方仓库 R0/R1 审计，为小规模训练做准备。

