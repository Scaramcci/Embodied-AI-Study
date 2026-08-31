# Phase 3 学习进度

## P3-1：人机差异与几何重定向 baseline

状态：已完成

- 核心问题：为什么不同形态之间不能按 joint index 复制角度？
- 当前对比：二维两关节人体臂、三关节机器人臂；joint-copy zero padding 与 task-space optimization。
- 结论：joint-copy 可保持部分角度/方向趋势，却因形态差异产生约 171 mm 腕部位置误差；task-space 方法通过有界数值 IK 保留所选腕部任务，但不自动保留肘部形态。

## P3-2：复合损失与约束

状态：核心已完成

- Part 1：固定同一肩部/腕部任务，让冗余肘部绕肩—腕轴变化；比较 task-only、plane-only、plane+smooth 和过强 smoothness。
- 已区分 task、arm-plane 与 temporal smoothness：plane 选择空间弯曲方向，smoothness 约束跨帧变化；过强平滑会偏离参考趋势。

## P3-3：整段轨迹优化

状态：已完成

- 当前实验：比较独立逐帧 IK、固定分支/warm start 和 whole-trajectory refinement。
- 独立 IK 虽然逐帧 FK 误差为零，但发生 7 次 elbow branch flip，最大相邻关节变化 2.95827 rad；
- warm start 保持同一解分支，最大相邻变化降至 0.04125 rad；
- 整段优化允许最大 0.1364 mm / 0.04501 deg 的微小任务误差，将速度、加速度和相邻变化进一步降低；
- 结论：逐帧成功、分支连续与整段时间质量必须分别评价。

## P3-4：论文映射与消融

状态：已完成

- 已建立 DexTele `L_ee/L_ori/L_norm/L_d` 与 P3 实验的对应关系；
- 已建立 ObjRetarget `L_task/L_plane/smoothness` 与 P3 实验的对应关系；
- 已明确 wrist error、MPJPE、Quat、VE/AE 之间不能直接等同；
- 已使用 P3-2 四组固定输入/单变量权重设置作为受控消融。

## Phase 3 Gate

状态：通过（2026-08-31）

- 阶段总结：`PHASE_03_SUMMARY.md`；
- 下一阶段：Phase 4 手—物接触、灵巧手与力调节；
- 并行任务：DexTele 官方仓库 R0/R1 复现审计。
