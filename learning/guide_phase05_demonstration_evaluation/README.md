# Phase 5：示范数据接口与闭环评测

详细计划：[`PHASE_05_DEMONSTRATION_EVALUATION.md`](../../planning/03_embodied_ai_guide_learning/PHASE_05_DEMONSTRATION_EVALUATION.md)

状态：Phase 5 两个压缩单元已完成。

阶段总结：[`PHASE_05_SUMMARY.md`](PHASE_05_SUMMARY.md)

本阶段继续使用 `eai-retarget`，不新增环境、不训练大型 ACT。P5-1 将建立 episode、observation/action、terminal、chunk 和 padding-mask 接口；P5-2 将比较 offline one-step error 与 closed-loop rollout。

运行 P5-1：

```powershell
conda activate eai-retarget
python learning\guide_phase05_demonstration_evaluation\src\p5a_demonstration_contract.py
```

实验输出两段 episode 的同步数据、future action chunks、padding mask，并拒绝动作错位、未来信息泄漏和跨 episode chunk。

运行 P5-2：

```powershell
conda activate eai-retarget
python learning\guide_phase05_demonstration_evaluation\src\p5b_offline_vs_rollout.py
```

实验拟合最小线性 BC，在专家状态上计算 offline action error，再对比 ID/OOD closed-loop rollout、action-chunk 扰动响应与论文常见指标。
