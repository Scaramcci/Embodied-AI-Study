# Implementation Plan: HuRo 数据环境

**Date:** 2026-11-04
**Status:** Data pipeline stages 1–8 verified
**Related Documents:** [调研](research-huro-pipeline.md)

## Overview
在 `/226040255/HuRo` 部署官方数据流水线，独立conda环境huro，不改已有环境。

## Current State Analysis
官方 `setup/setup.sh` 提供 env/build/check；`run_pipeline.sh:29` 配置输入和阶段范围；`pipeline/stage8_robot_retarget.py:519` 需要阶段7的表格。服务器已有Miniforge、CUDA12.8，缺git/curl及MANO模型。

## Desired End State
能从第一视角RGB输出48维关节状态、腕位姿与相机位姿，并提供启动及读取命令。缺用户模型时记录具体路径及未验收阶段。

## What We Are Not Doing
不训练模型，不部署实机，不替换用户已有环境，不宣称第三视角支持。

## Implementation Approach
使用官方固定提交及其子模块，按8.9单架构编译；保留日志和依赖清单。缺MANO时继续所有独立安装与可执行检查。

## Implementation Phases
- [x] 源码：`git clone https://github.com/3587jjh/HuRo.git /226040255/HuRo`，创建 `codex/huro-data-pipeline`，检出aeaae17，`git submodule update --init --recursive --jobs 4`。验证 `git submodule status --recursive` 无未初始化条目。
- [x] 环境：将Miniforge加入PATH，`TORCH_CUDA_ARCH_LIST=8.9 bash setup/setup-data.sh pip` 后运行 `bash setup/setup-data.sh build`，日志写入 `/226040255/.setup-huro/`。先检查不存在huro环境，再安装并验证GPU导入；不会为安装包装新增无意义单元测试。
- [x] 公开权重：`bash setup/download.sh`，`hf download Qwen/Qwen3.5-9B`。公开权重已完成；MANO由用户补充，存在后才运行手重建。
- [x] 验证：`bash setup/setup-data.sh check`；运行官方样例到阶段8并以 `python examples/read_parquet.py examples/clips_chunked` 检查非空轨迹、有限数值及关节名。只有实际执行成功才标记端到端通过。

## Success Criteria
### Automated Verification
- [x] CUDA扩展及阶段依赖可导入，GPU可用。
- [x] 所需公开模型下载完成，Qwen视频推理通过。
- [x] 用户MANO文件可读取并成功用于手部重建。
- [x] 样例输出非空48维关节轨迹和左右腕位姿，包含坐标系、单位、关节名称。
### Manual Verification
- [ ] 用户检查样例与目标视频视角及机器人是否符合用途。

## Testing Strategy
以官方import checks及真实样例作集成验收；未拿到MANO时分别记录可运行检查与被阻塞检查。保留固定提交、pip freeze、日志以及实际运行命令。

## References
[官方安装](https://github.com/3587jjh/HuRo/blob/main/setup/README.md)、[数据格式](https://github.com/3587jjh/HuRo/blob/main/examples/README.md)。

## 已确认的环境适配
Ubuntu20.04的glibc2.31不能加载IsaacSim5.1的manylinux_2_35轮子（https://pypi.nvidia.com/isaacsim-kernel/）。仅跳过阶段9对应安装，保留官方1–8阶段；使用已有 `/226040255/cuda-12.8`。用户确认尚无MANO并要求先完成其他安装。

## 验收范围更新
用户确认尚未取得MANO，先完成其余环境与公开权重。完整阶段4–8真实视频结果必须等待MANO；此次用官方P06_13_split.mp4验证1–3阶段，并独立检查48关节Allex加载及所有依赖/GPU运算。
PyArrow固定19.0.1，因最新版本不再支持NumPy1.26。语言注意力使用Qwen官方支持的SDPA，避免glibc2.32的FlashAttention二进制要求。

## 端到端验收完成（2026-11-04）
用户提供MANO后继续完成阶段4–8，官方样例生成2个操作片段、259帧机器人数据。官方读取器与独立NumPy/PyArrow环境检查通过。详情见[验证报告](validation-huro-pipeline.md)。此前MANO缺失说明是部署历史，已解除。
