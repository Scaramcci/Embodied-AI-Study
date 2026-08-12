# 论文路线环境

## 小型实验默认配置

```text
Ubuntu 22.04 or 24.04
Python 3.10
PyTorch 2.x with a matched CUDA runtime
PyTorch Geometric matched to PyTorch/CUDA
NumPy / SciPy / h5py
Matplotlib
PyBullet
pytest
```

实际安装时锁定解析出的精确版本，不在文档中长期写 `latest`。

## 硬件选择

| 任务 | 4090 Laptop 16GB | AutoDL 3090/4090 24GB |
|---|---|---|
| 合成/已提取轨迹重定向 | 优先 | 不需要 |
| 小型 PyG 训练 | 可以 | 数据大时再用 |
| 短视频现代姿态提取 | 可以 | 批量处理时使用 |
| SLAHMR | 短片段可尝试 | 更稳妥 |
| 仿真 GUI | 优先 | 主要用 headless |

AutoDL 实例建议 32GB 以上内存、50-100GB 数据盘。处理完及时关机，并将轨迹、配置和权重下载回本地。

## 与原论文环境的差异

DexTele 依赖的 FrankMocap 官方组合是 Python 3.7、PyTorch 1.6 和 CUDA 10.1。RTX 4090 不适合照搬这套环境。小型实验默认换用现代姿态模型，或者直接使用已提取骨架。

ObjRetarget 的 SLAHMR 官方基线为 PyTorch 1.13 + CUDA 11.7，并需要 PHALP、ViTPose、DROID-SLAM 和 SMPL 权重。这不是第一个实验的前置。

## 端到端边界

- 本地：录制视频、仿真可视化、以后的机器人连接。
- AutoDL：离线姿态处理、训练、批量评估。
- 环境间：只通过有 schema 的 NPZ/HDF5/JSON 交换，不依赖隐式 Python object。
