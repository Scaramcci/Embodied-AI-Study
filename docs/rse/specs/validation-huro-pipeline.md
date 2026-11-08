# HuRo 数据流水线验证

**日期：** 2026-11-04  
**依据：** [计划](plan-huro-pipeline.md)、[实施记录](implement-huro-pipeline.md)。远端官方基线`aeaae17f0fd51cc325b030bbef79ceb68a25199e`，保留已记录的主机兼容性补丁。

## 结论

官方第一视角RGB样例的数据流程阶段1–8已跑通，实际输出2个机器人操作片段、259帧。验证范围不包括阶段9渲染、阶段10导出、用户自有视频或实机执行。

## 实际执行

样例`examples/clips/P06_13_split.mp4`，30秒、900帧、30FPS、456×256。沿用已通过验证的阶段1–3输出，在用户MANO补齐后运行`INPUT_DIR=smoke/clips FIRST_STAGE=4 LAST_STAGE=8 bash run_data_pipeline.sh`，退出码0，没有跳过分段/修补或降低过滤阈值。

- 阶段1–3：有效AnyCalib内参，712行、1206个手检测。
- 阶段4：712行，927个有限三维手姿。
- 阶段5：365个有限相机变换，其余缺失由后续筛选/插值处理。
- 阶段6–8：保留以下2个操作段；不是对原视频全部900帧输出机器人轨迹。

| 片段文件 | 帧数 | 左手有效帧 | 右手有效帧 | 语言 |
|---|---:|---:|---:|---|
| 000299_000390.parquet | 92 | 80 | 50 | separate the lid from the container |
| 000733_000899.parquet | 167 | 167 | 141 | transfer a potato from the colander to a plate |

服务器输出目录：`/226040255/HuRo/smoke/clips_chunked/allex/annot/P06_13_split/`。

## 数值验收

- 每帧`state_qpos`为48维，关节名/顺序与Allex配置一致；双臂各7、双手各15、腰2、颈2。
- 关节状态、左右腕位姿、相机到底座变换均非空且有限。
- 相机齐次变换最后一行正确，旋转矩阵正交且行列式为1；腕部6D旋转的两个向量单位长度且正交（容差1e-3）。
- 帧索引连续；双臂均有真实数值变化，不是恒定默认姿态；各片段至少有有效手部目标。
- 官方`examples/read_parquet.py`读取成功。
- 新建仅含NumPy1.26.0/PyArrow19.0.1的独立venv读取成功，复核2片段259帧及相同数值不变量。这不是完整神经网络的全新环境逐位复现。

## 质量诊断与边界

有效目标上的指尖IK残差中位数约13.6–20.1mm（各片段/手分别统计），不是对真实机器人测量的精度。
原始优化使用关节限位软惩罚（`pipeline/retargeting/retargeter.py:251`及`:402`），存在轻微越界：最大0.00740047rad，约0.424°，位于右拇指偏航关节；机械臂关节最大约0.076°。保留原数据，未裁剪或隐藏这些值。后续数据筛选应结合掩码、IK残差及限位诊断。

既有10项模块/Parquet/GPU验收、13个公开权重MD5校验及Qwen视频推理均已通过。`pip check`的3项已记录元数据差异（OpenCV分发名、cuDNN精确版本）保留，实际运行通过。

## 证据与后续

服务器`/226040255/.setup-huro/`下：`e2e.log`、`e2e.status`、`output-validation.json`、`output-independent.log`、`official-reader.log`、`joint-limit-diagnostics.json`、`e2e-provenance.json`及输入/输出哈希。
人工检查操作语义与轨迹视觉质量、用户视频泛化和实机可执行性尚未验证。需要机器人画面叠加时另行配置兼容IsaacSim的系统环境。

## References
[计划](plan-huro-pipeline.md)、[实施记录](implement-huro-pipeline.md)、[调研](research-huro-pipeline.md)、[官方代码](https://github.com/3587jjh/HuRo)。
