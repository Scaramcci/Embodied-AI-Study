# EgoInfinity：RGB 到 4D 重建的公开程度与部署评估

**日期：** 2026-11-06（北京时间）  
**范围：** 本地论文译稿、官方源码与依赖文档、本机和 SSH 服务器只读检查；未安装环境、下载模型或执行完整重建。  
**版本：** 本仓库 `0e25b56`；EgoInfinity `de59610531c08010d63d0493d6a72973eabd402e`，源码临时检出于 `/tmp/egoinfinity-audit`。  
**相关调研：** [已有 RGB 数据流水线调研](research-rgb-data-pipelines.md)。

## 问题与结论

官方公开了从静态相机 RGB 操作视频生成时序手—物三维表示的主要流水线，有统一命令入口、分阶段恢复和交互查看器。可以作为实际部署基础。但“输入一个任意 RGB 视频，完全自动得到与官方演示一致的 4D MP4”不是当前默认入口提供的完整体验：需要物体文字提示、独立模型环境、显式启动 SAM3D，演示使用的 FoundationPose++ 旋转结果需外部生成，通用手—物场景 MP4 导出还需补充。

这里的 4D 是手网格、物体几何和六自由度轨迹随时间变化。它不是任意动态场景的完整稠密 4D 重建保证，也不等于生成式新视角视频。当前方法以近似静态相机的操作片段为目标；先用短、清晰、物体可见的视频验证。

## 源码核实

以下链接均固定在本次检出的官方提交，便于复核。

1. **自有视频入口已公开。** [process.py:24](https://github.com/Rice-RobotPI-Lab/EgoInfinity/blob/de59610531c08010d63d0493d6a72973eabd402e/egoinfinity/cli/process.py#L24) 接受视频路径、`--objects`、起止时间和 FPS；[extract_frames.py:68](https://github.com/Rice-RobotPI-Lab/EgoInfinity/blob/de59610531c08010d63d0493d6a72973eabd402e/egoinfinity/stages/extract_frames.py#L68) 调用 FFmpeg。该实现要求视频已在本地，URL 下载尚未接通。
2. **物体发现需要输入提示。** 用户提供 `objects` 列表，随后 SAM3 检测、SAM2 传播；不能把论文中的自动语义整理直接视为当前命令行已经实现的无提示输入能力。[MANIFEST.md](https://github.com/Rice-RobotPI-Lab/EgoInfinity/blob/de59610531c08010d63d0493d6a72973eabd402e/docs/MANIFEST.md)
3. **默认不会启动 SAM3D worker。** [defaults.yaml:27](https://github.com/Rice-RobotPI-Lab/EgoInfinity/blob/de59610531c08010d63d0493d6a72973eabd402e/configs/defaults.yaml#L27) 设置 `with_sam3d_worker: false`；[phase1.py:97](https://github.com/Rice-RobotPI-Lab/EgoInfinity/blob/de59610531c08010d63d0493d6a72973eabd402e/egoinfinity/stages/phase1.py#L97) 传入 `--no-sam3d-worker`。没有外部运行的 worker 时，[exo_pipeline.py:1970](https://github.com/Rice-RobotPI-Lab/EgoInfinity/blob/de59610531c08010d63d0493d6a72973eabd402e/scripts/exo_pipeline.py#L1970) 的网格分支不会执行。要显式启用并核对产物，不能只检查进程退出码。
4. **论文路线与默认配置不同。** MoGe-2 是默认深度模块；Flow3R 是已有实现、默认关闭的可选 refinement。[defaults.yaml:30](https://github.com/Rice-RobotPI-Lab/EgoInfinity/blob/de59610531c08010d63d0493d6a72973eabd402e/configs/defaults.yaml#L30)
5. **FP++ 接入不等于已经集成其推理。** `bake_fp` 消费独立 FoundationPose-plus-plus 运行生成的 `pose.npy`，缺失时保留原跟踪旋转。官方可视化使用的是经过该组合处理的旋转。[bake_fp_pose.py:3](https://github.com/Rice-RobotPI-Lab/EgoInfinity/blob/de59610531c08010d63d0493d6a72973eabd402e/egoinfinity/pipeline/post_tracking/bake_fp_pose.py#L3)
6. **原生输出以数据和查看器为主。** `pipeline_result.pkl.gz` 保存逐帧手、深度、掩码和位姿，`sam3_meshes/*.ply` 保存物体重建；[exo_pipeline.py:177](https://github.com/Rice-RobotPI-Lab/EgoInfinity/blob/de59610531c08010d63d0493d6a72973eabd402e/scripts/exo_pipeline.py#L177) 的 `--load-cache` 可启动 Viser 查看。源码中的 MP4 输出主要对应深度、机器人重定向和叠加结果，本次未找到默认主流程的通用手—物三维场景 MP4 导出入口。[retarget.py](https://github.com/Rice-RobotPI-Lab/EgoInfinity/blob/de59610531c08010d63d0493d6a72973eabd402e/egoinfinity/stages/retarget.py)

## 流程和计算分配

| 步骤 | 作用 | 本机建议 | 服务器建议 |
|---|---|---|---|
| 视频裁剪、缩放、抽帧、物体提示 | 准备短片和 manifest | 优先本机 | 也可执行 |
| MoGe-2、GeoCalib | 度量深度、焦距、重力 | 可运行，需安装环境 | 首轮统一运行 |
| YOLO、WiLoR、HaWoR infiller | 手检测、MANO 重建、补帧 | 可运行 | 首轮统一运行 |
| MEMFOF、深度对齐、平滑 | 时序稳定 | 可运行 | 首轮统一运行 |
| SAM3.1、SAM2 | 物体检测和掩码跟踪 | 可运行，控制模型驻留 | 首轮统一运行 |
| SAM 3D Objects | 完整物体几何重建 | 不建议作为首轮部署目标 | 优先服务器 |
| 内部 6DoF 跟踪与后处理 | 轨迹、抓握状态和对齐 | 可运行，部分步骤用 GPU | 建议与重建同机 |
| Flow3R（可选） | 时序深度 refinement | 限帧、独占 GPU 后尝试 | 优先服务器 |
| FoundationPose++（演示对齐） | 改善物体旋转 | 未验证依赖和峰值 | 优先服务器，另行部署 |
| 交互查看、检查、视频编码 | 检查和展示结果 | 优先本机 | 可运行服务并经 SSH 转发 |

这是基于模块预算和实测硬件的部署判断，不是各模块在两台机器上已经跑通的记录。官方架构描述了顺序加载模型及独立 worker；主 Phase 1 仍是一个大阶段，不建议为了分工随意拆开其内存中间量。官方支持的实用分割点是“小卡完成手、深度、掩码 → 传输片段缓存 → 大卡补 SAM3D → 继续后处理”。[架构说明](https://github.com/Rice-RobotPI-Lab/EgoInfinity/blob/de59610531c08010d63d0493d6a72973eabd402e/docs/PIPELINE.md)、[双机方案](https://github.com/Rice-RobotPI-Lab/EgoInfinity/blob/de59610531c08010d63d0493d6a72973eabd402e/docs/MULTI_HOST.md)

显存文档存在不一致：README 的完整流程目标是 A100 40 GB/H100 80 GB，multi-host 文档部分段落称 16 GB 可运行；其列出的 4+10+3～5 GB 实际合计为 17～19 GB，不能采用文中另写的 14～15 GB 作为可靠峰值。SAM3D 上游要求约 32 GB 显存。因此 5090 32 GB 是合理部署候选，本机 16 GB 适合拆分运行；峰值必须通过短片实测。[SAM3D 安装要求](https://github.com/facebookresearch/sam-3d-objects/blob/main/doc/setup.md)

## 两台机器实测

### 本机

- Ryzen 9 7945HX，16 核/32 线程；内存约 30 GiB，可用约 23 GiB。
- RTX 4090 Laptop，显存 16376 MiB，当时空闲 13736 MiB；驱动 595.99.02。
- 系统盘空闲约 518 GiB；已有 Miniconda 和 FFmpeg。
- 沙箱内 `nvidia-smi` 失败；沙箱外成功，故不能据此判断驱动损坏。本次未对本机模型环境执行 CUDA 推理测试。

### 服务器 `10.27.130.23:32476`

- Ubuntu 20.04.5；一张可见 RTX 5090，32607 MiB 显存，检查时几乎完全空闲；驱动 570.124.04。
- 主机可见 128 逻辑 CPU，但容器 `cpu.max=1200000 100000`，约为 **12 个 CPU 核心的时间配额**，不能按独占 128 线程估算吞吐。
- 主机内存显示 880 GiB、可用约 789 GiB；当前层级 `memory.max=max`。这不保证独享该容量，也不排除上级限制。
- 根文件系统仅余约 69 GiB。`/226040255` 为 GPFS，共享文件系统显示约 479 TiB 空闲；用户配额未核实。环境、缓存、权重应放该目录下，避免填满根分区。
- 发现 `/226040255/miniforge3` 与 `/226040255/cuda-12.8`；`nvcc` 为 12.8.93。默认 shell 未激活它们，系统 Python 3.8 中无 torch 不代表服务器没有可用环境。
- `huro` 环境：PyTorch 2.7.0+cu128；`sam3` 和 `sam3d`：PyTorch 2.8.0+cu128。三者均检测到 5090、包含 `sm_120`，实际执行 GPU tensor 求和并得到 8.0。
- `sam3`、`sam3d` 包路径分别指向已有 Do as I Do 模块。仅验证了包定位与基础 CUDA 运算，尚未验证 EgoInfinity 所需 SAM3.1 API、模型权重、SAM3D 自定义算子和推理。
- 已找到 MANO：`/226040255/HuRo/submodules/hawor/_DATA/data/mano/MANO_RIGHT.pkl`。也找到 Fast-SAM3D 配置文件，但不能据此确认官方 SAM3D 所有 checkpoint 齐全或可直接替换。
- 检查范围内未发现 EgoInfinity 专用部署；默认 PATH 未发现 Docker，未发现 `/var/run/docker.sock`。FP++ 的容器方案需另行解决。

5090 部署应沿用支持 Blackwell 的 CUDA 12.8/PyTorch 路线，不直接照搬 README 的 cu124 或 SAM3D 旧 cu121 示例；自定义 CUDA 扩展需要匹配架构和环境。[PyTorch 官方 Blackwell 支持说明](https://pytorch.org/blog/pytorch-2-7/)

## 建议的落地顺序

1. 在服务器共享盘创建隔离的 EgoInfinity 主环境；先核实并尽量复用已有模型文件，避免改坏 HuRo/Do as I Do 环境。SAM3.1 和 SAM3D worker 单独验证。
2. 用 4～6 秒、约 480p、15 FPS、1～2 个物体的静态相机操作视频进行验收。先不做机器人重定向；Flow3R 与 FP++ 作为后续明确验收项。
3. 显式启用 SAM3D worker。入口示意如下，**尚未实际运行**，路径与环境需在部署时设置：

   ```bash
   python -m egoinfinity process /absolute/path/clip.mp4 \
     --objects 'red mug' --start 0 --end 4 --fps 15 \
     --output /226040255/EgoInfinity-artifacts/test01 \
     --set 'phase1.args.with_sam3d_worker=true'
   ```

4. 检查非空手网格、对象 mask、`sam3_meshes/*.ply`、逐帧位姿与对齐效果，并测峰值显存。仅生成 PKL 不算完整物体重建成功。
5. 用 Viser 查看结果，再补固定/可选视角的手—物 MP4 导出。如果要求匹配官方展示的姿态处理链，再部署 FP++、生成 `pose.npy` 并 bake；启用 Flow3R 时单独记录结果。
6. 服务器单机通过后，再按需要启用双机模式：本机计算手/深度/掩码，服务器完成 SAM3D 和后处理；缓存传输包含 manifest、PKL 和物体 PLY，并保留源帧以支持重跑。

**当前判断：服务器具备部署硬件和已验证的 CUDA 基础环境，但 EgoInfinity 整套运行环境尚未完成验收。本机有能力承担多数轻中型推理阶段，首轮让服务器统一完成重建更便于验证。**
