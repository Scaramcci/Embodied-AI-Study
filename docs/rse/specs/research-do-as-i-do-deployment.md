# Do as I Do 服务器部署调查

日期：2026-11-06（北京时间）。范围：SSH 连接、既有环境与源码检查、服务器计算和本机展示的可行性。没有安装包或执行模型推理、重定向优化。

## 问题与结论

已通过 SSH 登录 `root@10.27.130.23:32476`。服务器已有部署基础，下一轮应验收并补齐，而不是重新安装五套环境。本机运行浏览器，服务器运行模型、仿真与 Viser，通过 SSH 转发展示；与 [EgoInfinity](implement-egoinfinity-deployment.md) 的分工一致。

## 当前状态

本地仓库提交 `0e25b56`；服务器 `/226040255/do-as-i-do` 提交 `824591b808c342b20079c3b4198a8c2bdf88c74e`。Fast-SAM3D、HaWoR、sam-3d-objects 子模块存在既有修改，后续保留并先记录 diff。既有安装记录 `/226040255/.setup-doasido/STATUS.md` 日期为 10 月 29 日，其中“无 GPU”已被本轮检查更新；其历史 CPU/导入测试不是本轮重测结果。

实测 RTX 5090，32607 MiB 显存，检查时使用 2 MiB；根盘余 68 GiB，共享盘 `/226040255` 显示余 479 TiB（不等同用户配额）。源码、运行输出、缓存均放共享盘。

| 环境 | PyTorch | 本轮 CUDA 求和 |
|---|---|---|
| sam3 | 2.8.0+cu128 | 8.0，通过 |
| sam3d | 2.8.0+cu128 | 8.0，通过 |
| hawor | 2.9.0+cu128 | 8.0，通过 |
| tapnet | 2.7.0+cu128 | 8.0，通过 |
| retargeting | 2.8.0+cu128 | 8.0，通过 |

测试为 `torch.ones(8,device="cuda").sum().item()`。这证明基础 GPU 运算可用，自定义算子和实际模型前向仍需验收。激活脚本 `/226040255/activate-doasido.sh` 设置 CUDA 12.8、共享盘缓存和独立环境。

## 样例、权重和交互

- `reconstruction/whisking/whisking.mp4` 存在；`retargeting/outputs/sharpa/right/whisking/0/` 有 scene.xml、IK、物理轨迹及配置。这是官方预计算样例，不是本轮生成。
- `reconstruction/weights/tapnet/bootstapir_checkpoint_v2.pt` 存在。旧安装报告记录 HaWoR 等公开权重已下载；下一轮加载模型前逐项验证。
- SAM3D 共享权重目录不存在，指定 HF 缓存下未发现 SAM 目录。Do as I Do 的两个 MANO 目标目录为空。HuRo 曾发现 MANO_RIGHT，可优先核实本地已有授权模型再链接；左手文件需单独核实。
- `reconstruction/run_pipeline.sh:75` 使用 `--click`；`reconstruction/scripts/run_sam3_video.py:44` 起已有 `--points`、`--point_labels`、`--text` 和 `--frame_idx`。可在本机对参考帧选点后把坐标交给服务器。
- `retargeting/replay_viser.py:64` 起支持运行目录、端口等参数；284 行启动查看器。`retargeting/retargeting/config.py:29` 支持独立输出根目录，45 行定义最大仿真步数。

## 综合判断

先回放官方样例检查展示，再从已有重建重新计算机器人轨迹，最后完成原视频重建与重定向。SAM 权重授权是完整 RGB 重建的前置条件，不影响先验收回放和已有参考上的重定向。第一轮需观测实际峰值显存；32 GB 是官方要求的起点，不是任意输入的运行保证。

## 来源

- [官方源码](https://github.com/malik-group/do-as-i-do)，本轮浏览核验。
- 服务器固定版本的 reconstruction/README.md、retargeting/README.md、config/paths.sh、run_pipeline.sh、setup/02_fetch_weights.sh、scripts/run_sam3_video.py。
- [既有调研](research-rgb-data-pipelines.md)、[EgoInfinity 部署调查](research-egoinfinity-deployment.md)。
