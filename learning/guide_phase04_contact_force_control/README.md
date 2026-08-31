# Phase 4：手—物接触、灵巧手与力调节

详细计划：[`PHASE_04_CONTACT_FORCE_CONTROL.md`](../../planning/03_embodied_ai_guide_learning/PHASE_04_CONTACT_FORCE_CONTROL.md)

状态：Phase 4 三个核心单元已完成。

阶段总结：[`PHASE_04_SUMMARY.md`](PHASE_04_SUMMARY.md)

下一阶段：[`Phase 5：示范数据接口与闭环评测`](../guide_phase05_demonstration_evaluation/README.md)

```powershell
conda activate eai-retarget
python learning\guide_phase04_contact_force_control\src\p4c_rolling_force_control.py
```

实验使用可微的 command + feedback force surrogate，在每个控制周期根据最新反馈重新优化下一条手指命令，
并比较无调节、弱正则、合理正则和过强正则。
