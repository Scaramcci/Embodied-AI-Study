# Do as I Do：服务器运行、本机展示计划

日期：2026-11-06。状态：用户已授权配置非受限部分；SAM3/SAM3D 权重等待访问许可。
依据：[本轮调查](research-do-as-i-do-deployment.md)。

## 目标与当前状态

复用服务器 `/226040255/do-as-i-do` 及五个环境，补齐模型并生成一个可回放的样例。本机通过浏览器检查每阶段结果，随后按“输入—命令—输出—可视化”逐步教学。基础 CUDA 已通过，完整模型和仿真尚未验收。

## 分工和实施方式

服务器负责权重、分割、深度、手物重建、轨迹跟踪、物理优化和 Viser 服务。本机负责选点、浏览器交互与结果展示。使用本机 18081 转发服务器 8081，避开 EgoInfinity 的本机 18080。新产物放 `/226040255/do-as-i-do-runs/`，保留原始样例。

本轮配置和验证不依赖 SAM 权重的环境，并验证官方样例回放；完整 RGB 样例待权限通过。后续首个样例包含仿真重定向，不涉及真实机械臂执行、训练或批量数据生成。

## 阶段 1：官方样例回放和展示验收

先记录服务器当前源码及子模块修改，启动已有回放：

```bash
source /226040255/activate-doasido.sh retargeting
cd /226040255/do-as-i-do/retargeting
python replay_viser.py --port 8081
```

本机另开终端：

```bash
ssh -F /dev/null -p 32476 -N -o ExitOnForwardFailure=yes \
  -L 127.0.0.1:18081:127.0.0.1:8081 root@10.27.130.23
```

打开 `http://localhost:18081`；验证播放、逐帧滑块及 MANO/IK/物理轨迹三个图层。此阶段标注“官方预计算样例”，不宣称复现完成。连接使用交互密码，不把密码写进脚本。

## 阶段 2：重新计算重定向

依赖阶段 1，使用官方重建参考，先执行有界 GPU 烟测：

```bash
source /226040255/activate-doasido.sh retargeting
cd /226040255/do-as-i-do/retargeting
python launch.py --task whisking --raw-dir ../reconstruction/whisking \
  --output-root-dir /226040255/do-as-i-do-runs/smoke \
  --max-sim-steps 10 --no-show-viewer --no-wait-on-finish
```

通过后删除命令中的 `--max-sim-steps 10`，输出根目录改为 `/226040255/do-as-i-do-runs/full`，完成整段。核实生成 scene.xml、trajectory_kinematic.npz、trajectory_mjwp.npz 和 config.yaml；检查时间轴、有限数值、数组维度、跟踪误差及峰值显存。回放命令：

```bash
python replay_viser.py \
  --run-dir /226040255/do-as-i-do-runs/full/sharpa/right/whisking/0 --port 8081
```

这证明“已有重建参考→机器人动作”，尚不等于从 RGB 的完整复现。

## 阶段 3：补齐 RGB 重建并跑同一视频

依赖模型可访问与本地选点适配。先核实 SAM3、SAM3D 访问许可，使用服务器交互认证；分别验证 checkpoint 实际加载，不以下载脚本退出码替代验收。核实已有 MANO 文件，链接到 Do as I Do 的两个目标目录，并验证 HaWoR 加载。

将输入复制到独立目录：

```bash
mkdir -p /226040255/do-as-i-do-runs/rgb/whisking
cp /226040255/do-as-i-do/reconstruction/whisking/whisking.mp4 \
  /226040255/do-as-i-do-runs/rgb/whisking/whisking.mp4
```

后续实施时为 run_pipeline.sh:75 的点击入口增加可保存的点坐标输入，调用 run_sam3_video.py 已有 `--points` 和 `--point_labels`，保留原始像素坐标及参考帧 125。本机选点工具与包装脚本在该阶段编写并验证；这是明确推迟的实现设计，不把尚未存在的脚本列作现成命令。

使用对象 `whisk`、右手、参考帧 125 顺序执行分割、网格/深度/手部重建、重力估计、TAPIR、引导跟踪、尺度平移对齐。逐阶段检查 mask、OBJ、all_hand_meshes.npz、gravity.json、layout_camera_frame_optimized.json，再将新目录传给阶段 2 的 `--raw-dir`，输出到独立端到端目录。

## 阶段 4：逐步教学

依赖完整样例验收。按六个节点讲解：原视频与参考帧 → mask → 手和物体三维重建 → 对齐轨迹 → IK → 物理优化。每次只展开一个节点，展示实际输入、执行命令、输出文件及本机画面；由用户操作确认后继续。完整运行日志、版本、参数、输入哈希与原始/新生成结果分开保存。

## 验收与测试策略

自动验收：基础 CUDA（已通过）、模型加载、自定义算子实际执行、样例各阶段非空且数值有限、查看器 HTTP 可达。先用 10 步仿真验证 GPU 算子，再运行完整样例；不为安装过程增加模拟单元测试。

人工验收：本机可播放与拖动时间轴；分割对象正确；手物相对位置可解释；三层轨迹可比较。仿真输出产生、轨迹质量和 RGB 重建正确性分别评价，不用单一退出码替代。

模型权限未齐时先完成前两阶段；不以跳过重建冒充端到端成功。首次完整运行记录时间、显存、失败阶段与恢复入口，不预估未经实测的运行时长。
