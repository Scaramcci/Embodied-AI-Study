# Sim2Real Plan

Sim2Real 只在它能减少真机数据、覆盖危险/稀有失败或回答独立研究问题时进入；“项目更完整”不是充分理由。默认主研究实验使用真实 teleop 数据。

## Reality-gap 清单

| 维度 | 最小对齐 | 可选增强 | 验证 |
|---|---|---|---|
| robot model | joint order/axis/limits/zero/tool geometry | inertial/system identification | 相同 joint 输入的 pose/轨迹差 |
| camera | 分辨率、视角、安装位、裁剪 | intrinsics/extrinsics、噪声/blur | 标志物位置和图像统计 |
| geometry | 桌面、物体尺度、目标区 | mesh/材质随机化 | 接触/可达区域对照 |
| servo/control | action type、频率、limit、delay | identified response model | step/trajectory response |
| friction/contact | 合理抓取/滑落区间 | 参数分布 | grasp/slip 统计差 |
| latency | capture→inference→execute 分布 | jitter/drop injection | 端到端 trace |
| appearance | 背景/光照/颜色范围 | domain randomization | feature/image distribution 与任务性能 |

## 工作流

Entry：真机 baseline 已能暴露具体瓶颈。先提出假设，例如“加入从真机测得的延迟分布可减少振荡”；收集最小识别数据；只随机化有证据的参数；用相同 action/observation contract 训练；在未用于拟合的真机场景评估；计算收益相对于工程和真机采集成本。

可有价值：危险/稀有 failure 的恢复预训练、相机扰动鲁棒性、并行生成验证器数据、对真实数据需求的消融。价值低：已有充足 teleop 数据；接触/柔性差异主导；仿真资产调参成本高于直接采集；只增加漂亮视频。

## Gate

Entry：具体 gap、指标和最小对照已写入实验计划。Tasks：system identification、最小 sim-vs-real benchmark、randomization 消融。Exit：相对 real-only baseline 有量化收益或形成可信负结论；未用 test/OOD 调 simulator；差异和限制公开。**Compute**：MuJoCo A/B；Isaac headless B；Isaac GUI E；测量 D。无价值则记录“不纳入主线”。

