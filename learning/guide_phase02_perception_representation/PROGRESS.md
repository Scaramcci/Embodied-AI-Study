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

状态：进行中

当前实验：

- 使用针孔模型完成 camera-frame 3D point 到像素的投影；
- 使用像素和 Z-depth 反投影回 camera frame；
- 使用 `world_T_camera` 及其逆矩阵完成 camera/world frame round trip；
- 记录三维点和像素重投影误差。
- 注入深度单位、深度定义和外参方向错误，比较三维误差与像素重投影误差。
- 将合成 Z-depth 图完整反投影成 camera/world point cloud，并可视化深度平面。
