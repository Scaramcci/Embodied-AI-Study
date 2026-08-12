# 论文精读指南

## DexTele

### 方法问题

1. 人和机器人的骨架图如何用同一编码器/解码器表示？
2. arm 与 hand 为什么需要双流结构？
3. 六个 retargeting loss 分别限制什么？它们的量纲是否一致？
4. 训练参数和 inference-time latent optimization 是什么关系？
5. 跨平台实验是否包含新拓扑上的训练或适配？
6. VLM 输出的“目标抓取力”如何校准？
7. 论文所称 MPC 与标准有限时域 MPC 有哪些差异？

### 实验问题

- Sign 与 CSL-Daily-derived 数据的划分和标注从哪里来？
- MPJPE、Quat、VE、AE 是与人体轨迹比，还是与机器人 ground truth 比？
- 消融是否保持了参数量和训练预算公平？
- 力控成功率的对照是固定角度、固定力还是无调整？

## ObjRetarget

### 方法问题

1. SLAHMR、物体位姿跟踪和接触检测的误差如何传递到后续优化？
2. 初始 retargeting 是否就是 DexTele 的 SAG-GCN 系统？
3. arm-plane normal 在手腕速度很小或向量共线时如何处理？
4. task loss、plane loss 和 smoothness loss 的权重如何选择？
5. human/robot 手指长度不同时，edge-length invariant 如何做尺度对齐？
6. 0.05 cm contact threshold 与 D435i 和物体跟踪精度是否匹配？
7. polytope optimization 是逐帧还是轨迹级？如何避免接触切换抖动？

### 实验问题

- OKAMI 与 ORION 适配到灵巧手时新增了哪些作者实现？
- object slip 是如何估计的，是否需要额外 motion capture？
- 三个示教者的比较是否有数值统计？
- 每个任务 20 次试验中，对象初始位姿随机化范围是什么？

## 共同问题

- 方法保留的是人的绝对姿态，还是任务相关的相对几何？
- 论文解决的是示教数据生成、实时遥操，还是自主 policy learning？
- 不使用多指灵巧手时，还能保留哪些方法和评估问题？
- 两篇论文的代码、数据、权重和硬件接口是否足以支持第三方复现？
