# 调研：Being-H0 与 Do as I Do 的 RGB 数据处理流程

**日期：** 2026-10-24  
**范围：** 本仓库资料、论文原文、官方公开代码；只研究数据生成，不训练模型、不部署实机。  
**本仓库基线：** `49cdd18`。本次保留了用户对《视频数据利用调研笔记.md》的未提交修改。  
**后续计划：** [RGB 数据处理复现计划](plan-rgb-data-pipelines.md)。

## 问题与范围

目标是把用户自己的单目 RGB 操作视频，分别转换为两种可检查、可追溯的数据：

1. Being-H0 路线：图像、语言指令、规范化人手运动，以及由已有动作 tokenizer 编码出的 motion tokens。
2. Do as I Do 路线：手与物体的三维重建、相对一致的尺度和坐标系，以及经过物理仿真优化的机器人控制轨迹。

预训练视觉模型与动作 tokenizer 的前向推理属于本任务；梯度更新、训练 tokenizer、训练 VLA 均不属于本任务。Do as I Do 的采样式轨迹优化用于生成数据，属于本任务。

## 本地资料与版本

当前仓库主要是文献与学习规划，README 的入口为 `README.md:5` 起的学习计划。两篇论文已有 PDF 与中文译稿，但没有这两条数据流水线的可运行工程。

本次在临时目录读取了两个官方仓库，未将源码、权重或数据加入本仓库：

| 项目 | 本次检出的上游提交 | 官方源 |
|---|---|---|
| Being-H0 | `ae92e46f671f48d91161ef1c8cc956bcdffab606` | [BeingBeyond/Being-H0](https://github.com/BeingBeyond/Being-H0) |
| Do as I Do | `824591b808c342b20079c3b4198a8c2bdf88c74e` | [malik-group/do-as-i-do](https://github.com/malik-group/do-as-i-do) |

下面的上游源码位置均相对于对应仓库。引用使用固定提交，避免 main 更新后含义变化。

## Being-H0：原文规定的流程

依据[论文](https://arxiv.org/abs/2507.15597)第 4.1.4、5.2、6.1.1 节；本仓库原文见 `papers/手动作与动作 token/Being-H0/BeingH0.pdf`。中文译稿属于阅读辅助，不能替代参数和格式核对。

- 原论文同时整合已有动作捕捉/VR 标注和纯 RGB 视频。纯 RGB 路线使用 **HaMeR** 估计逐帧手姿，再检查左右手错配、轨迹跳变，插值少量缺失，并约束关节与时序平滑。
- 运动使用 MANO 表示。关节角、手腕旋转、平移、手形，以及用于编码的派生特征必须区分；不能把 HaMeR 的任意输出数组直接交给动作 tokenizer。
- 语言标注先把长视频切为不重叠、最长 10 秒的片段，以 2 FPS 抽取用于语言理解的帧；还对重叠的 1 秒窗口标注，并分别描述双手与单手活动。原文使用 Gemini 标注与扩展模板。
- **2 FPS 是语言标注取帧频率，15 FPS 是动作序列频率。** 不应把这两个参数合并。动作分词使用一秒窗口，并处理参考帧坐标系。
- 使用已有的腕部、手指动作 tokenizer 编码运动，再构建动作生成、动作翻译、上下文动作预测三类指令数据。原文默认配置为每手每秒 128 个动作代码；实际复现必须读取所下载 checkpoint 的配置验证，而不能只写死该数字。

### 公开代码能直接提供什么

- [README:31](https://github.com/BeingBeyond/Being-H0/blob/ae92e46f671f48d91161ef1c8cc956bcdffab606/README.md#L31) 列出了动作 tokenizer 和 VLA 权重。
- [mano_adapter.py:225](https://github.com/BeingBeyond/Being-H0/blob/ae92e46f671f48d91161ef1c8cc956bcdffab606/beingvla/models/motion/mano_adapter.py#L225) 加载腕/指 checkpoint 及 `motion_meta.json`、`meta_mask.json`；[同文件:428](https://github.com/BeingBeyond/Being-H0/blob/ae92e46f671f48d91161ef1c8cc956bcdffab606/beingvla/models/motion/mano_adapter.py#L428) 提供运动编码，包含标准化、时间补齐、分部位代码偏移与词表偏移。
- [mano_utils.py:1116](https://github.com/BeingBeyond/Being-H0/blob/ae92e46f671f48d91161ef1c8cc956bcdffab606/beingvla/models/motion/m2m/utils/mano_utils.py#L1116) 和 [tokenizer/model.py:454](https://github.com/BeingBeyond/Being-H0/blob/ae92e46f671f48d91161ef1c8cc956bcdffab606/beingvla/models/motion/m2m/tokenizer/model.py#L454) 展示了特征拆分。论文的 MANO-D162 名称、包含根关节的特征、分部位编码输入不应被视为同一个固定维度；代码中还存在 159 维解码分支，必须以 checkpoint 元数据和往返重建验证为准。
- [preprocess_robot_data.py:10](https://github.com/BeingBeyond/Being-H0/blob/ae92e46f671f48d91161ef1c8cc956bcdffab606/beingvla/models/motion/m2m/aligner/preprocess_robot_data.py#L10) 是已有机器人 Zarr 数据到 JSONL 的转换，**不是** RGB 视频到人手伪标签的完整处理器。
- 对检出版本的文件树和入口检索，没有发现完整的 HaMeR 视频批处理、UniHand 质检、语言标注与三类样本生成的一键入口。因此这部分需要依据论文补齐工程，并明确记录自主选择的阈值和模板。

[HaMeR 官方代码](https://github.com/geopavlakos/hamer)提供图像推理与 MANO 依赖说明。视频抽帧、检测结果关联、左右手维护及输出参数保存仍需针对本任务封装。

## Do as I Do：可直接复用的官方流水线

依据[重建说明](https://github.com/malik-group/do-as-i-do/blob/824591b808c342b20079c3b4198a8c2bdf88c74e/reconstruction/README.md)与[重定向说明](https://github.com/malik-group/do-as-i-do/blob/824591b808c342b20079c3b4198a8c2bdf88c74e/retargeting/README.md)。

重建阶段依次涉及分割、物体网格、深度/内参、HaWoR 手部重建、重力、点跟踪引导的物体姿态跟踪、手物平移与尺度对齐。主要输出包括 mask、OBJ 网格、pointmap、相机参数、`all_hand_meshes.npz`、`gravity.json` 和 `layout_camera_frame_optimized.json`。

重定向阶段把这些结果转换为清理后的参考、物体凸分解、MuJoCo 场景、逆运动学和采样式 MPC 优化结果。最终 `trajectory_mjwp.npz` 是后续机器人样本导出的重要来源。

### 部署条件与代码中的具体风险

- 官方重建最低要求为 NVIDIA GPU、至少 32GB 显存，以及 SAM 3、SAM 3D 和 MANO 访问权限。用户 48GB 单卡满足容量门槛；这不等于已经验证所有阶段的峰值显存或驱动兼容性。
- 重建使用 `sam3`、`sam3d`、`hawor`、`tapnet` 四个环境；重定向另有环境，要求 Python ≥3.12。[pyproject.toml:31](https://github.com/malik-group/do-as-i-do/blob/824591b808c342b20079c3b4198a8c2bdf88c74e/retargeting/pyproject.toml#L31)固定 MuJoCo/Warp 的关键组合，不能统一升级所有依赖。
- [config/paths.sh](https://github.com/malik-group/do-as-i-do/blob/824591b808c342b20079c3b4198a8c2bdf88c74e/reconstruction/config/paths.sh)将 `CUDA_VISIBLE_DEVICES` 固定为 0；[run_pipeline.sh:75](https://github.com/malik-group/do-as-i-do/blob/824591b808c342b20079c3b4198a8c2bdf88c74e/reconstruction/run_pipeline.sh#L75)物体分割使用点击 GUI。批量多卡处理前需要使 GPU 设置可由外部传入，并显式保存分割提示；已有文本/点提示接口可用于无显示模式，但其分割质量需另行验收。
- [optimize_physics.py:593](https://github.com/malik-group/do-as-i-do/blob/824591b808c342b20079c3b4198a8c2bdf88c74e/retargeting/retargeting/pipeline/optimize_physics.py#L593)及后续代码记录 `qpos`、`qvel`、`time`、`ctrl`，保存时可能有“规划块×仿真子步”的维度。导出前必须按时间轴展开和检查，不能把所有第一维都当视频帧。
- `qpos` 包含场景状态，`ctrl` 是仿真 actuator 控制；两者都不能不加说明地称为机器人关节角 action。必须保存关节/actuator 名称、类型、单位、机器人模型、时间步和动作含义。

## 结论与边界

先复用 Do as I Do 的官方样例验证环境和原生输出，再补 Being-H0 的 RGB 路线，最终在同一小批视频上生成两类数据进行质量比较。

两条路线的人手跟踪器不同：**HaMeR 与 HaWoR 不能为了省事直接互换并仍称为原方法复现。** 可以共享视频清单、时间戳和审阅工具；跨方法复用伪标签应作为单独变体。

原论文没有公开全部清洗阈值、完整 UniHand 制备工程或所有训练样本。可以复现算法链与数据结构；在未拿到原始参数/数据之前，不承诺逐样本一致。没有三维真值时，投影一致性和仿真跟踪误差只是质量信号，不能证明真实三维绝对准确或实机可执行。

## 核验状态

已核对论文原文和上述固定提交源码；没有安装 GPU 环境，没有下载模型权重，没有在用户服务器执行，没有产生或验证数据处理结果。本文件是后续实施的证据记录，不是复现完成报告。
