# 环境与工具

## 环境边界

不建立一个包含所有依赖的环境。老代姿态估计代码和现代 PyTorch Geometric 组合很容易冲突。

| 环境 | 用途 | 建议边界 |
|---|---|---|
| `retarget` | 运动学、优化、PyG、仿真和指标 | Python 3.10，现代 PyTorch/CUDA，版本锁定 |
| `pose-modern` | 短视频人体/手部关键点 | 使用现代姿态模型，通过 NPZ/HDF5 输出与 `retarget` 连接 |
| `frankmocap-legacy` | 只在必须贴近 DexTele 时使用 | Python 3.7/PyTorch 1.6/CUDA 10.1 是原始组合，不与现代环境混装 |
| `slahmr` | 只在小实验需要三维人体恢复时建立 | 官方以 Ubuntu 22.04、PyTorch 1.13、CUDA 11.7 为基线 |

## 计算资源

| 资源 | 用途 | 不做什么 |
|---|---|---|
| GTX 1650 4GB | NumPy/SciPy、轻量 IK、PyBullet、现成轨迹推理 | 不跑完整 SLAHMR 和实时全身姿态 |
| RTX 4090 Laptop 16GB | 日常开发、短视频姿态、小模型训练、本地仿真 | 不当作论文中 24GB 桌面 4090 |
| AutoDL 3090/4090 24GB | 批处理、SLAHMR 尝试、模型训练与消融 | 不承担本地相机或机器人实时控制 |

小型实验优先使用 4090 Laptop。只有本地显存、运行时间或老依赖隔离成为问题时，才租 AutoDL。

## 最小工具集

- NumPy、SciPy：几何与约束优化。
- PyTorch、PyTorch Geometric：DexTele 图结构重定向。
- h5py/NPZ：姿态与轨迹的跨环境交换。
- PyBullet：机器人模型可视化、IK 和轨迹回放。
- Matplotlib：轨迹、速度、加速度和误差图。
- pytest：单位、坐标系、四元数顺序和指标测试。

## 环境证据

每次实验保存：

```text
OS / kernel
GPU / driver
Python
PyTorch / CUDA runtime
PyTorch Geometric
git commit + dirty diff
exact command
peak VRAM
```

不把 `nvidia-smi` 显示的 CUDA 上限当作 PyTorch 实际 runtime 版本。
