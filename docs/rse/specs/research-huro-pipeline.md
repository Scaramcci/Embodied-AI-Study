# Research: HuRo RGB 数据流水线

**Date:** 2026-11-04
**Scope:** 本地论文、官方代码及远程运行条件；仅数据处理。
**Related Documents:** [部署计划](plan-huro-pipeline.md)

## Question / Scope
确认官方是否提供 RGB 到机器人关节及位姿的流程，并部署到用户指定服务器。

## Codebase Findings
本地资料基线 `0e25b56`。官方 HuRo 版本 `aeaae17f0fd51cc325b030bbef79ceb68a25199e`。
官方 [README](https://github.com/3587jjh/HuRo) 明确发布 raw egocentric video 到 LeRobot V2.0 的十阶段流程。
[阶段说明](https://github.com/3587jjh/HuRo/blob/main/pipeline/README.md) 中阶段 1–6 恢复内参、手框、手姿、相机轨迹和语言分段；7 修补画面，8 重定向，9 渲染，10 导出。
`pipeline/stage8_robot_retarget.py:519` 排除 `_narr.parquet` 并检查阶段 7 是否完成，因此原版不能简单跳过阶段 7。
`configs/allex.yaml:7` 定义双臂各7、双手各15、腰2、颈2，共48维关节。
[数据格式](https://github.com/3587jjh/HuRo/blob/main/examples/README.md) 定义 state_qpos、state_eef_left/right、cam_pose_base 和有序关节名元数据，位置单位米、角度弧度。动作是下一帧状态。

## Prior Art
[安装说明](https://github.com/3587jjh/HuRo/blob/main/setup/README.md) 要求 CUDA 12.8、24GB以上显存。远程 RTX 5880 Ada 48GB、驱动570.124.06、已有CUDA12.8和Miniforge；系统Ubuntu20.04，初始无git/curl。
限制核查：只支持第一视角输入，建议30fps和短边256；默认机器人仅Allex；MANO模型需注册取得；Isaac Sim叠加需RT核心和其许可。单目估计和IK不能证明轨迹物理正确或实机可执行。

## Synthesis
官方流程符合需求，无需训练。独立安装环境及公开模型，以官方样例做验证。MANO文件缺失时清楚记录阻塞，不能称为端到端完成。先验收阶段8数据，图像叠加单独验证。

## References / Sources
- https://3587jjh.github.io/HuRo/
- https://github.com/3587jjh/HuRo/tree/aeaae17f0fd51cc325b030bbef79ceb68a25199e

## 部署中确认的兼容性
- IsaacSim5.1 wheel 要求 glibc2.35，当前系统2.31；只部署阶段1–8，阶段9–10未运行。
- 官方 torch-scatter 和 FlashAttention wheel 要求 glibc2.32；torch-scatter改源码编译，Qwen使用官方支持的PyTorch SDPA后端，未改变模型权重。
- pandas固定2.2.3、ml-dtypes固定0.5.3以兼容NumPy1.26；cuDNN固定9.10.2.21并以Torch卷积和JAX JIT实测共存。
- DROID的setup.py显式列出多架构，不受TORCH_CUDA_ARCH_LIST约束；主机补丁只保留sm_89。
- CUDA头文件位于既有工具包targets/x86_64-linux/include，通过CPATH传入，未更换系统CUDA。
- 13个公开模型文件逐个匹配官方MD5；Qwen四个分片已下载且通过视频帧推理验证。用户明确表示尚无MANO，要求先完成其他安装。

## 后续实测更新
MANO已由用户提供。2026-11-04完成阶段4–8并生成2个片段259帧机器人轨迹；此前的MANO缺失状态已解除。数值与独立读取结果见[验证报告](validation-huro-pipeline.md)。
