# Phase 3：动作重定向与轨迹优化

详细计划：[`PHASE_03_MOTION_RETARGETING_OPTIMIZATION.md`](../../planning/03_embodied_ai_guide_learning/PHASE_03_MOTION_RETARGETING_OPTIMIZATION.md)

当前单元：P3-1 人机形态差异与 task-space geometric baseline。

```powershell
conda activate eai-retarget
python learning\guide_phase03_motion_retargeting_optimization\src\p3a_retargeting_baselines.py
```

实验比较二维两关节人体臂与三关节机器人臂上的 joint-copy zero padding 和 task-space
retargeting。重点不是二维模型本身，而是确认跨形态映射必须先声明要保留的任务语义。

## P3-2 Part 1：arm-plane 与时间平滑

```powershell
conda activate eai-retarget
python learning\guide_phase03_motion_retargeting_optimization\src\p3b_arm_plane_losses.py
```

该实验固定肩部和腕部任务，使不同肘部构型具有完全相同的腕部误差，再观察 arm-plane 与
smoothness 如何从冗余解中选出不同手臂运动。

## P3-3：逐帧 IK 与整段轨迹优化

```powershell
conda activate eai-retarget
python learning\guide_phase03_motion_retargeting_optimization\src\p3c_whole_trajectory_optimization.py
```

该实验为每帧构造肘上/肘下两组合法解析 IK 解。独立求解会切换分支，warm start 保持分支，
整段优化则在任务误差与相邻关节变化之间做统一折中。

## P3-4：论文映射与消融总结

阅读 [`P3_PAPER_MAPPING.md`](notes/P3_PAPER_MAPPING.md)，将 P3-1/P3-2/P3-3 分别映射到
DexTele 的复合重定向 loss 与 ObjRetarget 的手臂轨迹细化目标，并核对当前实验与论文指标的边界。
