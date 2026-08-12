# Experiment Log

每个实验在运行前复制模板并填写 Question/Hypothesis/primary metric；运行后补全所有结果。失败实验不删除。

## Experiment Index

| Experiment ID | Question | Status | Dataset | Model | Primary result | Linked artifacts |
|---|---|---|---|---|---|---|
| — | 尚未运行实验 | — | — | — | — | — |

## Experiment Template

### EXP-XXX — Title

- **Question**：
- **Hypothesis**：
- **Status**：planned / running / completed / invalidated
- **Code Commit / Dirty Diff**：
- **Dataset Version / Split**：
- **Model / Checkpoint Initialization**：
- **Config / Config Hash**：
- **Hardware / Software Environment**：
- **Seed / Trial Manifest**：
- **Calibration / Camera / Robot IDs**：
- **Evaluation Protocol Version**：
- **Input**：
- **Output / Artifact Paths**：
- **Primary Metric and Decision Rule**：
- **Secondary Metrics**：
- **Result (include denominator/uncertainty)**：
- **Failure / Invalid Trials / Exclusions**：
- **Interpretation**：
- **Limitations**：
- **Next Step**：

## Logging Gate

正式运行前 Entry fields 完整；运行后 hash/原始输出存在；结论只引用已完成且未 invalidated 的实验。Invalidated 实验保留原因和 artifact，不能静默重跑。

