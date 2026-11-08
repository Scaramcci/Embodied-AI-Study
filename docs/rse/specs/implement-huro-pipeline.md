# Implementation Summary: HuRo 数据处理环境

**日期：** 2026-11-04  
**状态：** 官方样例阶段1–8已验证，已生成机器人关节与位姿数据。  
**计划：** [部署计划](plan-huro-pipeline.md)

## 实施内容
服务器`root@10.27.130.23:32476`，目录`/226040255/HuRo`，环境`/226040255/miniforge3/envs/huro`。官方提交`aeaae17f0fd51cc325b030bbef79ceb68a25199e`，工作分支`codex/huro-data-pipeline`，全部子模块初始化。
独立安装Python3.11、PyTorch2.7.0+cu128、JAX0.6.2，构建DROID、LieTorch、Detectron2、SAM2、PyTorch3D、100DoH和torch-scatter。没有训练模型，没有修改已有Being-H0/Do-as-I-do环境。

## 适配与变更
- `setup/setup-data.sh`：仅数据阶段安装，跳过IsaacSim；固定pandas2.2.3、ml-dtypes0.5.3、PyArrow19.0.1、NumPy1.26.0、cuDNN9.10.2.21；torch-scatter源码构建。
- `submodules_patches/droidcalib-data.patch`：官方补丁加sm_89单架构构建。修复CUDA头文件路径，使用已有CUDA12.8。
- `pipeline/captioning/caption.py`：将FlashAttention2替换为Qwen官方支持的SDPA，避免glibc2.32二进制要求。
- `setup/download-data.sh`：支持续传和多连接；SAM2使用作者官方HF镜像，并核对原始MD5。
- `run_data_pipeline.sh`：默认运行阶段1–8，支持环境变量指定输入目录和阶段。
- `/226040255/activate-huro.sh`：激活环境并设置CUDA、缓存、编译路径。
- `DATA_PIPELINE_USAGE.zh.md`：服务器上的中文使用说明及输出字段。

Ubuntu20.04的glibc2.31不满足IsaacSim5.1的2.35要求，未安装阶段9渲染和依赖它的阶段10导出。用户关注的关节和位姿由阶段8Parquet输出。

## 验证结果
- 10项模块/GPU/Parquet检查通过，结果位于`/226040255/.setup-huro/check-env.json`。
- Allex模型加载48个可控关节：双臂各7、双手各15、腰2、颈2。
- 官方30秒视频`examples/clips/P06_13_split.mp4`跑通阶段1–3。标定因相机运动不足按原实现回退AnyCalib，生成有效内参。检测与整理表均为712帧、1206个手检测。
- 13个公开权重文件匹配官方MD5，见`weights-check.json`。
- Qwen3.5-9B四个分片全部下载，HF revision为`c202236235762e1c871ad0ccb60c8ee5ba337b9a`。通过原流程视频输入函数对样例帧执行生成，输出有效场景描述，峰值CUDA显存18.94GB；日志`vlm-smoke.log`。
- `pip check`保留3项元数据差异：mmengine/ultralytics声明opencv-python而实际用官方要求的opencv-contrib-python-headless；Torch精确声明cuDNN9.7，而JAX运行需较新版本。实际Torch卷积、JAX JIT和SDPA GPU运算均通过。

## 恢复与使用
```bash
source /226040255/activate-huro.sh
# MANO就绪后运行用户视频；输入第一视角30FPS，建议短边256
INPUT_DIR=/226040255/my_clips bash run_data_pipeline.sh
python examples/read_parquet.py /226040255/my_clips_chunked
```
完整构建及验收恢复入口：`bash /226040255/.setup-huro/resume-build.sh`；依赖清单`/226040255/.setup-huro/pip-freeze.txt`。

## 完整数据流程验收（MANO补齐后）

用户上传MANO v1.2左右模型，SHA256与本地一致。继续运行：

```bash
source /226040255/activate-huro.sh
INPUT_DIR=smoke/clips FIRST_STAGE=4 LAST_STAGE=8 bash run_data_pipeline.sh
```

阶段4输出927个有限三维手姿，阶段5输出365个有效相机变换。阶段6生成92帧和167帧两个操作片段，阶段7修补成功，阶段8生成对应48维机器人关节及腕/相机位姿，退出码0。

输出目录：`/226040255/HuRo/smoke/clips_chunked/allex/annot/P06_13_split/`。详细数值、关节名、有效掩码及独立环境读取检查均通过；原始求解含最大0.424°的关节限位超出，保留原数据与诊断，不作裁剪。

## 验证来源与复查

运行记录：`/226040255/.setup-huro/e2e-provenance.json`，包含代码版本、硬件、Python版本、配置哈希和准确命令。输入与输出SHA256分别见`e2e-input-hashes.json`、`e2e-output-hashes.json`。依赖清单沿用`pip-freeze.txt`。

新建的独立venv仅安装NumPy1.26.0和PyArrow19.0.1，成功重现数据读取与结构/数值不变量检查。这验证输出格式的独立可读性；没有声称完整模型推理在全新环境中的逐位复现，也未固定额外随机种子。

## 后续边界

阶段9机器人视觉叠加及阶段10导出未部署。用户自己的视频、人工轨迹质量评价、实机执行均未验收。使用数据时保留有效掩码和IK残差，不把估计轨迹当成运动捕捉真值。

## References
[调研](research-huro-pipeline.md)、[计划](plan-huro-pipeline.md)、[官方仓库](https://github.com/3587jjh/HuRo)。
