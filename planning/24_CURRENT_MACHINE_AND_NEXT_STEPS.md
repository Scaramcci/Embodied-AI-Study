# Current Machine Baseline and Next Steps

盘点日期：2026-08-11。本文把当前机器事实转换为 G0 的环境设计和下一阶段学习顺序。版本是当前基线，不把 `latest` 当作可复现版本。

## 1. Current machine inventory

| Item | Verified state | Decision impact |
|---|---|---|
| OS | Ubuntu 24.04.4 LTS, x86_64, kernel 7.0.0-28-generic | 使用 Ubuntu 原生 ROS 2 Jazzy 包 |
| CPU | Intel i7-9750H, 6 cores / 12 threads | 足够运行 ROS 2、MuJoCo 和数据审计 |
| RAM | 15 GiB available to OS, 4 GiB swap | 仿真从单环境开始；避免 Isaac 和大 batch |
| Disk | `/` 502 GiB, 452 GiB free | 足够完成 G0-G2；数据和 checkpoint 仍需 manifest |
| GPU | NVIDIA GeForce GTX 1650 Mobile, 4 GiB | 适合图形显示、GPU smoke 和小模型；正式视觉 ACT 训练转云端 |
| NVIDIA driver | 580.173.02; host `nvidia-smi` passed | 驱动正常，不需要先重装 |
| CUDA Toolkit | `nvcc` not installed | 当前不安装；PyTorch wheel 可自带所需 CUDA runtime |
| Python | Conda base Python 3.14.6; no project packages | 不污染 base；项目使用独立 Python 3.11 环境 |
| ROS 2 | Not installed | Ubuntu 24.04 对应 ROS 2 Jazzy；使用系统 Python 3.12 路径 |
| Build tools | GCC 13.3 and build-essential present; CMake absent | 安装最小开发依赖时补 CMake |
| Docker | Docker 29.1.3 installed; current user cannot access daemon; no NVIDIA runtime | G0-G2 本地学习不依赖 Docker，云训练前再处理 |
| Camera/USB | 沙箱内无法可靠读取 | 真机或相机到货后在宿主终端重新盘点 |

注意：沙箱内的 `nvidia-smi`、`lsusb` 和 systemd 检测会因设备隔离失败。宿主机只读复检已经确认 GPU 驱动与 `/dev/nvidia*` 正常。因此这不是 NVIDIA blocker。

## 2. Environment boundaries

不要把 ROS 2、MuJoCo/ML 和 Conda base 混成一个环境。

| Layer | Interpreter / manager | Purpose |
|---|---|---|
| System robotics | Ubuntu system Python 3.12 + apt | ROS 2 Jazzy、TF、RViz、rosbag、colcon |
| Simulation / ML | Conda environment `embodied-sim`, Python 3.11 | NumPy、SciPy、Matplotlib、pytest、MuJoCo、Gymnasium，之后再加 PyTorch |
| Cloud training | Pinned lock or container created after local smoke | 正式视觉 BC/ACT 训练与批量评估 |

ROS 2 官方文档明确提示：预编译 ROS 2 二进制要匹配构建时的 Python，Conda interpreter 很可能不兼容。因此 ROS 节点练习使用系统 Python；ML 与仿真代码通过明确 adapter/schema 连接，不直接让 Conda 接管 `/opt/ros/jazzy`。

当前建议的最小版本策略：

- ROS 2：Jazzy on Ubuntu 24.04，使用 apt 安装的二进制包；
- simulation Python：3.11，先锁 Python minor，再由安装后的 lock 记录精确包版本；
- MuJoCo：安装时锁定解析出的精确版本，使用官方 `mujoco` Python package，不使用废弃的 `mujoco-py`；
- PyTorch：推迟到 CPU MuJoCo smoke 通过后，按当时官方 wheel matrix 明确选择 CUDA wheel；不依据 `nvidia-smi` 的 `CUDA Version` 盲装 Toolkit；
- LeRobot：到 M7-M9 接入时锁 commit/tag 和 extras，不在 G0 安装 `.[all]`。

## 3. What to learn next

当前最重要的不是 ACT、VLA 或 Isaac，而是把 `joint/frame/action/time` 变成能运行和验证的闭环。

### Stage A - Finish M0: reproducible local baseline

学习：系统 Python 与 Conda 的边界、驱动与 CUDA runtime 的区别、环境 lock、smoke test。

实操：

1. 建立 `embodied-sim` Python 3.11 环境，只安装 NumPy、SciPy、Matplotlib、pytest、MuJoCo 和 Gymnasium。
2. 记录 exact package versions，运行 MuJoCo CPU/offscreen 和 GUI smoke。
3. 安装 ROS 2 Jazzy desktop 与开发工具，运行 talker/listener 和 RViz smoke。
4. 记录每条命令、输出和失败；暂不安装 PyTorch、LeRobot、Isaac 或 CUDA Toolkit。

Exit：新终端能分别进入 ROS 和 simulation 环境；两个 smoke test 都通过；能解释为什么二者使用不同 Python。

### Stage B - L0 robot representation and control

学习：joint/DOF、弧度、pose/frame、齐次变换、FK、position controller、frequency/latency。

实操：

1. 写 v0 joint table：name、order、unit、direction、limit，先使用简化 2-3 DOF arm。
2. 手算并用 NumPy 验证 2D/3D frame compose、inverse 和 point transform。
3. 为 2-link arm 实现 FK 数值测试，覆盖零位、边界和错误单位。
4. 实现离散 position loop，画 target/actual/error，并注入延迟、限幅和超时。

Exit：能定位 degree/radian、frame direction、joint order 和 stale timestamp 四类错误；测试会明确失败。

### Stage C - M4 MuJoCo closed loop

学习：MJCF/URDF 的角色、`qpos/qvel`、actuator、physics timestep 与 control period、contact。

实操：加载简化机械臂，完成 `reset -> observe -> act -> step -> log`；加入 joint/velocity limit、固定 seed、扰动和 stop reason；输出控制曲线与短视频。

Exit：闭环在扰动后重新收敛；越界/超时停止；同一 seed 可复现轨迹。此时再换入锁定版本的 SO-101 model，避免一开始同时调模型和控制器。

### Stage D - M1 ROS 2 interface diagnostics

学习：node/topic/service/action、QoS、TF、timestamp、rosbag。

实操：完成 `publisher -> safety controller mock -> joint state -> rosbag replay`，再发布简化模型的 TF/URDF；比较 command 和 state 的频率、延迟与丢帧。

Exit：能从 command topic 追踪到状态反馈；bag 回放产生一致 observation；action 可取消且 watchdog 生效。

完成 A-D 后，才进入 M5-M8：脚本抓放、observation/action schema、模拟 demonstrations 和小型 BC。ACT 是 M9，Isaac 与 VLA 继续后置。

## 4. Immediate execution order

下一次实施会话严格按以下顺序进行：

1. 创建最小 Conda Python 3.11 simulation 环境并生成 lock/explicit manifest；
2. 运行 MuJoCo headless、GUI、NumPy transform 三个 smoke tests；
3. 安装并验证 ROS 2 Jazzy，保持系统 Python 路径；
4. 创建第一个学习 artifact：joint/frame contract 与 transform tests；
5. 只有上述均通过后才决定 PyTorch CUDA wheel。

## 5. Smoke-test contract

| Smoke | Pass condition | Evidence |
|---|---|---|
| NVIDIA host | `nvidia-smi` returns GTX 1650, driver and 4096 MiB | captured command output |
| Python isolation | environment reports Python 3.11 and base remains unchanged | env manifest |
| MuJoCo headless | load minimal XML, step 1000 frames, finite state, deterministic result | test output and seed |
| MuJoCo GUI | render a visible moving body without crash | screenshot or short video |
| ROS graph | talker/listener exchange messages; `ros2 topic hz` is measurable | command log |
| RViz/TF | one rooted, acyclic frame tree with correct transform query | TF tree and screenshot |
| PyTorch CPU | tensor op and tiny backward pass | version and test output |
| PyTorch CUDA, later | GPU name is GTX 1650; allocation and backward pass succeed | torch/CUDA/driver versions and peak VRAM |

M0 remains open until the environment is actually built from its manifest and the relevant smoke tests pass. The inventory and design portions are complete.

## Official references

- ROS 2 Jazzy installation entry: <https://docs.ros.org/en/jazzy/Installation.html>
- ROS 2 Python package compatibility: <https://docs.ros.org/en/jazzy/How-To-Guides/Using-Python-Packages.html>
- MuJoCo Python bindings: <https://mujoco.readthedocs.io/en/stable/python.html>
- PyTorch local install matrix: <https://docs.pytorch.org/get-started/locally/>
- LeRobot installation: <https://github.com/huggingface/lerobot/blob/main/docs/source/installation.mdx>
