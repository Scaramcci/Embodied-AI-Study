# Phase 2 学习进度

## 环境

状态：已完成

- Conda 环境：`eai-retarget`
- Python、NumPy、SciPy、Matplotlib、OpenCV、Open3D、pytest 已安装并验证；
- 当前阶段使用 Windows + CPU，无需 CUDA。

## Unit 1：论文输入接口与数据契约

状态：已完成

当前实验：

- 生成 10 帧 body/hand/object canonical packet；
- 分离数组数据与 metadata；
- 验证 shape、dtype、frame、unit、timestamp、quaternion order、confidence 和 joint order；
- 注入并拦截四类数据契约错误。
- 区分 confidence、valid mask 和缺失值，并检查 NaN、数值范围、四元数范数与 shape。
- 使用 adapter 转换上游模型的单位、时间、四元数布局和 joint order，再运行 canonical validator。

完成标准：能够解释为什么“数组 shape 正确”不等于“数据语义正确”，并能读懂验证报告。

## Unit 2：相机模型、深度与坐标变换

状态：已完成（Gate 通过）

当前实验：

- 使用针孔模型完成 camera-frame 3D point 到像素的投影；
- 使用像素和 Z-depth 反投影回 camera frame；
- 使用 `world_T_camera` 及其逆矩阵完成 camera/world frame round trip；
- 记录三维点和像素重投影误差。
- 注入深度单位、深度定义和外参方向错误，比较三维误差与像素重投影误差。
- 将合成 Z-depth 图完整反投影成 camera/world point cloud，并可视化深度平面。

总结：`notes/unit02_summary.md`

## Unit 3：人体上肢、手部关键点与骨架图

状态：核心已完成；加速路线下其余常规处理降为可选

当前实验：

- 按 joint name 建立左右 `shoulder-elbow-wrist` 节点顺序；
- 构造有向 `edge_index`、节点特征和边向量；
- 验证边向量和骨长对人体整体平移不变；
- 保存 frame 0 骨架图与结构化数组。
- 已建立上肢骨架图并理解 node/edge features；这是当前 Unit 3 的必学出口。
- 中心化/尺度归一化脚本已提供，但按 2026-08-30 加速策略改为可选参考，不要求运行。
- missing/NaN、confidence 和异常处理不再建立额外练习。

## 加速路线

状态：Phase 2 加速 Gate 已通过

- 权威计划：`planning/03_embodied_ai_guide_learning/ACCELERATED_PAPER_FIRST_ROUTE.md`
- 论文第一遍从现在并行开始，不等待 Phase 2–5 全部完成；
- 已完成 P2-A object local/world cloud + palm/fingertips，以及 P2-B contact distance/event；
- 下一步：进入 Phase 3 动作重定向与轨迹优化。

## P2-A：手—物任务几何

状态：已完成

- 已从 ObjRetarget Figure 2 明确 reference plan 输入；
- 已建立 DexTele Paper Pass 1 系统地图；
- 当前实验：`object_cloud_local -> world_T_object -> object_cloud_world`，并加入 world-frame palm + five fingertips。
- 已理解 world frame、object frame、表面点云以及图中 local/world 两种表示。

## P2-B：接触距离、事件与时间错位

状态：已完成

- 当前实验：五个指尖到物体 world point cloud 的最近距离与阈值接触事件；
- 正常案例：hand/object 使用相同 world frame 和同一 timestamp；
- 失败案例：物体流故意偏移 5 帧，观察接触事件误判；
- 输出：`hand_object_distance[T,5]`、`contact_event[T,5]`、曲线图和结构化数据包。
- 正确对齐：距离范围 2–50 mm，中指接触状态在 frame 27/91 切换；
- 物体流偏移 5 帧（0.167 s）：31 个 fingertip-frame 判定不一致，中指切换变为 frame 30/87；
- 结论：接触距离要求 hand/object 同单位、同 frame、同 timestamp；阈值事件不表示接触几何、力、摩擦或抓取稳定性。

## Phase 2 加速 Gate

状态：通过

- 能解释 object local/world cloud、world/object/camera frame；
- 能把 palm/fingertips 与物体点云放到同一 world frame；
- 能从最近距离生成可诊断的 contact event；
- 能指出 frame 或 timestamp 错位造成的接触误判；
- 可直接进入 Phase 3，不追加通用数据清洗练习。
