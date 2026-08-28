# Phase 2：人体、手部与物体感知表示

> 状态：进行中（计划已建立，待开始 Unit 1）  
> 前置条件：完成 Phase 1《机械臂仿真与可执行轨迹》  
> 建议用时：6 次学习，每次 60–90 分钟  
> 实验栈：Python + NumPy + SciPy + OpenCV + Matplotlib + Open3D + pytest  
> 论文出口：为 DexTele/ObjRetarget 构造可验证的人体骨架、手部关键点、物体位姿/点云和接触事件输入

## 1. 阶段核心问题

给定一段 RGB 或 RGB-D 人类操作视频，后续动作重定向模块究竟需要什么结构化输入，怎样保证这些输入的 shape、坐标系、单位和时间对应关系可信？

```text
RGB / RGB-D sequence
    -> camera model and timestamps
    -> 3D upper-body / hand pose interface
    -> human skeleton graph
    -> object identity / pose / point cloud interface
    -> confidence, valid mask and temporal alignment
    -> hand-object distance and contact event
    -> validated perception data packet for retargeting
```

完成后，应能明确区分：

- RGB 像素、depth value 与 camera-frame 3D point；
- camera frame、world frame、human-root frame、hand-local frame 与 object frame；
- 人体姿态估计器的原始输出和重定向真正使用的结构化骨架序列；
- 手部全部关节与 ObjRetarget 使用的掌心 + 五指尖六关键点表示；
- 物体类别、2D mask、3D point cloud、6D object pose 与 time-varying trajectory；
- tracking confidence、valid mask、missing observation 和真实 contact event；
- 感知误差与 Phase 1 中 IK/FK、轨迹和控制误差的传播关系。

## 2. 与论文的直接联系

### DexTele

- 使用标准 RGB 相机与 FrankMocap 捕捉人体三维手臂和手部动作；
- 将捕捉结果拆分为手臂流和手部流，再送入双流 SAG-GCN；
- 将人体和机器人表示为骨架图 `G_k=(V_k,E_k,W_k)`；
- 节点特征为 `h_{k,i}=[p_{k,i}, q_{k,i}]`，包含三维位置和四元数；
- 边特征 `e_{k,ij}=p_{k,j}-p_{k,i}` 表示局部几何；
- 位置使用几何中心 `c_k` 和全局尺度 `s_k` 归一化，以处理人机尺度差异；
- VLM 读取外部相机图像并输出物体类别/目标力先验，但本阶段只学习其输入输出接口，不训练 VLM。

本阶段出口：能够构造与 DexTele 图输入语义一致的 `position + quaternion + edge + normalization` 数据，而不是部署 FrankMocap 或复现 SAG-GCN。

### ObjRetarget

- 输入是一段 RGB-D 人类操作视频；
- SLAHMR 提供时间连续的人体动作序列；
- VLM/检测与跟踪模块提供任务物体身份及随时间变化的 object pose；
- 系统整合时间同步的人体关节姿态、物体点云位姿和人—物交互距离；
- 手部接触表示使用掌心与五个指尖，共六个关键点；
- 物体表面从 depth point cloud 重建；
- 通过手指关键点与物体表面点的距离检测接触事件；
- 统一时间调度器依赖可靠的 timestamp 与 contact/non-contact phase。

本阶段出口：能够构造 ObjRetarget 后续几何模块需要的同步人体/手/物数据接口；多面体簇、几何不变量和接触优化留到 Phase 4。

## 3. 学习范围与删减

### 必学

- 数组数据契约：shape、dtype、frame、unit、timestamp、quaternion order；
- 针孔相机模型、相机内参与基础 RGB-D 深度反投影；
- 齐次变换在 camera/world/human/object frame 之间的使用；
- 上肢 shoulder–elbow–wrist 与手部关键点表示；
- 人体骨架 graph nodes、edges、node/edge features；
- 人体位置中心化与尺度归一化；
- 物体 6D pose、local point cloud 与 world point cloud；
- tracking confidence、valid mask、missing frame 与异常值；
- 不同采样率序列的 timestamp 对齐；
- position 插值与 quaternion SLERP 的概念和最小实现；
- 手—物最近距离与 contact event 的最小接口；
- 感知输入的数值验证、失败案例和可重复报告。

### 只学接口，不做大型模型训练

- FrankMocap：理解 RGB -> 3D body/hand pose 接口与误差来源；
- SLAHMR：理解 RGB video -> temporally consistent human motion 接口；
- VLM：理解 image/prompt -> object identity/semantic prior 接口；
- detector/segmenter/tracker：理解 mask、track id、pose、confidence 和 missing observation；
- RealSense：理解 RGB-D、intrinsics、depth scale 和 timestamp 字段。

### 暂不学习

- 训练或微调 FrankMocap、SLAHMR、SAM、VLM 和大型检测器；
- 大规模人体姿态数据集、完整 2D/3D pose benchmark；
- 多视角动作捕捉、SLAM、NeRF 与完整三维重建；
- 真实相机采购、外参标定板实验和硬件同步；
- 复杂 object pose network、dense correspondence 与 category-level pose；
- 多面体簇、接触几何优化、灵巧手控制与力反馈；
- ROS 2 图像管线、真机通信和实时部署优化。

## 4. 环境、目录与数据契约

### 环境策略

计划使用独立 Conda 环境：`eai-retarget`。

第一批最小依赖：

```text
Python 3.11
NumPy
SciPy
Matplotlib
OpenCV
pytest
```

按单元需要再加入：

```text
Open3D：Unit 4 点云读取、变换和可视化
PyTorch：Phase 3 图表示与优化开始前加入
```

本阶段的核心数值实验在 Windows + CPU 上即可完成，不要求 CUDA。大型感知模型建立单独遗留环境或容器，不污染 `eai-retarget`。

### 学习目录

开始实践时创建：

```text
learning/guide_phase02_perception_representation/
├── README.md
├── PROGRESS.md
├── src/
├── tests/
├── data/
├── outputs/
└── notes/
```

`data/` 先保存小型合成数据和固定 fixture，不提交大型视频、模型权重或真实数据集。

### 阶段统一数据契约

以下是教学用 canonical schema；真实模型输出必须先经过 adapter 转换到该 schema：

```text
timestamp                    [T]                 float64, seconds
rgb                          [T,H,W,3]           uint8, optional interface
depth                        [T,H,W]             float32, meters
camera_intrinsics            [3,3]               float64
world_T_camera               [T,4,4] or [4,4]    float64

body_position                [T,J_body,3]        float32, meters
body_quaternion_xyzw         [T,J_body,4]        float32
body_confidence              [T,J_body]          float32 in [0,1]
body_valid                    [T,J_body]          bool
body_edges                    [2,E_body]          int64

hand_position                [T,2,J_hand,3]      float32, meters
hand_quaternion_xyzw         [T,2,J_hand,4]      float32, optional
contact_keypoints            [T,2,6,3]           palm + five fingertips
hand_confidence              [T,2,J_hand]        float32 in [0,1]

object_track_id              [N_object]           string/int
object_pose_xyzw             [T,N_object,7]       position + quaternion
object_pose_confidence       [T,N_object]         float32 in [0,1]
object_valid                 [T,N_object]         bool
object_cloud_local           [N_object,P,3]       float32, meters

hand_object_distance         [T,2,5]              float32, meters
contact_event                [T,2,5]              bool
```

每个实际文件必须同时保存 metadata：

```text
schema_version
coordinate_frames
position_unit
depth_unit / depth_scale
quaternion_order
joint/keypoint names and order
timestamp source / sample rate
confidence definition
missing-value policy
```

## 5. 六个学习单元

### Unit 1：论文输入接口与数据契约

核心问题：看到一组人体/手/物体数组时，怎样判断它能否安全送入重定向模块？

学习与操作：

1. 把两篇论文的感知输入整理成统一字段表；
2. 区分 raw observation、model output、canonical representation；
3. 定义 `T`、body/hand joint order、object track id 与 keypoint names；
4. 为每个数组声明 shape、dtype、frame、unit、timestamp 和 quaternion order；
5. 编写 schema validator，检查 shape、NaN、timestamp 单调性、四元数单位长度和 confidence 范围；
6. 构造一个正确样本和至少四个错误样本：mm/m、xyzw/wxyz、错位 timestamp、缺失 joint order。

产物：canonical schema、字段说明、数据 validator、正确/错误 fixture 与测试。

通过条件：拿到任意 pose sequence 时，先问清数据契约，不再只根据数组维度猜语义。

### Unit 2：相机模型、深度与坐标变换

核心问题：RGB-D 中一个像素和深度值，怎样变成重定向可用的世界坐标三维点？

学习与操作：

1. 理解 `fx, fy, cx, cy` 与相机内参矩阵 `K`；
2. 使用 pinhole model 完成 3D point -> pixel projection；
3. 使用 depth 完成 pixel -> camera-frame point back-projection；
4. 使用 `world_T_camera` 把 camera point 转换到 world frame；
5. 比较 optical-frame 轴约定和 Phase 1 world/base frame；
6. 验证 projection/back-projection round trip；
7. 注入 depth scale、矩阵方向和 meter/millimeter 三类错误。

最低验证：

```text
pixel + depth
    -> point_camera
    -> point_world
    -> world_T_camera^-1
    -> point_camera_recovered
    -> pixel_reprojected
```

产物：相机模型脚本、RGB-D 小 fixture、3D 可视化、round-trip 误差表和约定错误案例。

通过条件：能说明一个 3D 关键点当前位于哪个 frame，并正确决定该乘 `world_T_camera` 还是其逆矩阵。

### Unit 3：人体上肢、手部关键点与骨架图

核心问题：FrankMocap/SLAHMR 的姿态输出怎样变成 DexTele/ObjRetarget 使用的结构化人体表示？

学习与操作：

1. 建立 body/hand joint-name -> index 映射；
2. 提取左右 shoulder、elbow、wrist 与手部关键点；
3. 构造 skeleton edges 和邻接关系；
4. 构造 DexTele 风格节点特征 `[position, quaternion]`；
5. 构造边特征 `p_child - p_parent`；
6. 实现几何中心/尺度归一化并验证平移、尺度变化后的结果；
7. 提取 ObjRetarget 的 palm + five fingertips 六关键点；
8. 使用 confidence/valid mask 显式标记遮挡与缺失关键点。

产物：上肢/手部 skeleton schema、graph arrays、归一化实验、关键点图和缺失观测案例。

通过条件：能够从时序人体数据构造 `G_k=(V_k,E_k,features)`，并解释节点位置、方向和边向量的 frame/scale。

### Unit 4：物体身份、6D 位姿与点云

核心问题：论文中的“检测到物体”“跟踪物体”和“知道物体表面”分别提供什么数据？

学习与操作：

1. 区分 object category、instance id、track id、2D box 与 mask；
2. 定义 object pose 为 `world_T_object` 或 position+quaternion；
3. 从固定 mask + depth 反投影一个小型 object point cloud；
4. 区分 `object_cloud_local` 与随 pose 变换的 `object_cloud_world[t]`；
5. 验证 `world_T_object @ point_object`；
6. 模拟 object tracking confidence、遮挡和 track loss；
7. 为 VLM/检测器/pose tracker 写最小 adapter 接口，不调用大型模型训练。

产物：object schema、点云 fixture、pose transform 脚本、点云图和 track-loss 案例。

通过条件：能解释为什么只有物体类别或 2D box 不足以支持 ObjRetarget 的三维手—物接触几何。

### Unit 5：时间同步、置信度与接触事件

核心问题：人体、手部、深度和物体跟踪来自不同时间时，怎样得到可信的同帧交互表示？

学习与操作：

1. 为 body、hand、depth 和 object stream 建立独立 timestamp；
2. 选择统一 timeline 并做 nearest/linear alignment；
3. 对 position 使用线性插值，对 orientation 使用 quaternion SLERP；
4. 比较错误的四元数线性插值与 SLERP；
5. 根据 confidence 和最大时间差生成 valid mask；
6. 计算五个指尖到 object world cloud 的最近距离；
7. 用可配置阈值生成 contact/non-contact event；
8. 分析 depth noise、pose drift 和 timestamp offset 对 contact event 的影响。

产物：多流时间同步脚本、aligned data packet、distance/contact 曲线、missing frame 和 false-contact 案例。

通过条件：不会把不同 timestamp 的人体手指和物体点云直接做距离计算，能够解释 confidence 与阈值如何影响接触误判。

### Unit 6：论文导向综合感知数据包

核心问题：能否生成一份后续重定向/接触模块可以直接消费、可以诊断且可复现的感知输入？

任务：使用固定的小型合成 RGB-D-like sequence，完成：

```text
camera intrinsics / extrinsics / timestamps
    -> body and hand canonical pose sequence
    -> DexTele-style skeleton graph features
    -> object local cloud + world pose trajectory
    -> synchronized hand/object world points
    -> fingertip-object distance and contact events
    -> confidence / valid / failure report
```

必须报告：

- 所有输入 shape、dtype、frame、unit、timestamp 和 quaternion order；
- projection/back-projection 与 frame round-trip error；
- body/hand joint order、graph edges 和 normalization metadata；
- object track id、pose confidence、point-cloud frame 和 valid mask；
- 时间对齐误差与缺失帧；
- fingertip-object distance 和 contact event；
- 一个正常案例、一个 unit/frame 错误案例、一个 missing/low-confidence 案例；
- 对下游 Phase 3/4 的接口说明。

产物：固定输入、canonical NPZ/JSON、validator tests、可视化、失败报告和一页结论。

通过条件：综合数据包可由新终端重复生成，并能明确指出哪些字段供 DexTele 图重定向使用，哪些字段供 ObjRetarget 物体/接触模块使用。

## 6. 阶段 Gate

全部满足后才进入 Phase 3：

- [ ] 能为人体、手部、物体和相机数组写出完整数据契约；
- [ ] 能完成 pinhole projection、depth back-projection 和 frame round trip；
- [ ] 能区分 camera/world/human-root/hand/object frame；
- [ ] 能构造上肢/手部 skeleton graph、node features 和 edge features；
- [ ] 能实现人体位置中心化/尺度归一化并解释它保留与丢失的信息；
- [ ] 能表示 object 6D pose、local/world point cloud 和 tracking validity；
- [ ] 能按 timestamp 对齐 body/hand/object stream，并正确处理 quaternion；
- [ ] 能显式保存 confidence、valid mask、missing observation 和失败原因；
- [ ] 能从 hand keypoints 与 object cloud 生成可诊断的 contact event；
- [ ] 能把综合数据包映射到 DexTele/ObjRetarget 的下游输入。

## 7. 每次学习的协作流程

遵循 Phase 1 中形成的教学节奏：

1. 先说明本单元解决什么问题以及与论文的关系；
2. 解释实验输入、改变的变量、记录指标和预期现象；
3. 再创建并运行最小代码；
4. 学习者先解释输出和图表；
5. 助手纠正 frame/unit/quaternion/timestamp 等关键概念；
6. 注入至少一个约定错误或感知失败案例；
7. 保存代码、fixture、图表、测试和进度；
8. 当前 Unit 通过后再进入下一 Unit。

单次记录模板：

```text
Date / Unit:
Question:
Paper interface:
Input contract:
Prediction:
Observation:
Evidence path:
Failure / confusion:
Gate result:
Next single action:
```

## 8. 当前入口

第一课只做 Unit 1：

1. 创建并验证 `eai-retarget` Conda 环境；
2. 创建 Phase 2 学习目录；
3. 定义 canonical schema 和 metadata；
4. 生成一个 10 帧合成 body/hand/object fixture；
5. 编写 validator；
6. 验证正确样本，并依次触发 mm/m、xyzw/wxyz、timestamp 和 joint-order 错误。
