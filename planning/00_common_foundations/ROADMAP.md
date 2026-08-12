# 公共基础路线

基础不单独追求“系统学完”。每一阶段都以论文中的一个具体问题为出口。

## F0 环境与记录

学习：系统 Python 与 Conda、NVIDIA driver 与 CUDA runtime、PyTorch 与 PyG 版本匹配、Git 实验身份。

实操：

- 创建一个现代的 `retarget` 环境；
- 记录 Python、PyTorch、CUDA、GPU 和核心包版本；
- 运行 CPU/GPU tensor、NumPy/SciPy 优化和 PyBullet headless smoke test。

证据：环境 manifest 与 smoke-test 输出。

## F1 空间几何

学习：vector/frame、rotation matrix、quaternion、SO(3)、homogeneous transform、camera/world/robot frame。

实操：

- 组合与求逆 3D transform；
- 在不同 frame 中变换人体手腕和物体点；
- 比较 `xyzw` 与 `wxyz`、degree 与 radian 错误。

证据：数值测试和一张 frame 图。

## F2 运动学与重定向

学习：joint/link/DOF、FK、Jacobian、IK、冗余、奇异位形、joint limits、human-robot embodiment gap。

实操：

- 2-link 手算与 NumPy FK；
- 3-6 DoF 仿真机械臂 IK；
- 将归一化的肩-肘-腕目标映射为机器人末端与肘部约束。

证据：可达/不可达测试、轨迹可视化与误差表。

## F3 感知与表示

学习：2D/3D keypoints、skeleton graph、camera projection、depth/point cloud、object pose、contact event。

实操：

- 从短视频中导出肩、肘、腕轨迹；
- 绘制骨架图并说明 node/edge feature；
- 对深度点进行相机系到世界系变换。

证据：关键点序列、可视化和字段说明。

## F4 优化、轨迹与控制

学习：least squares、软/硬约束、正则化、时序平滑、position control、force feedback、MPC 的作用。

实操：

- 优化 task tracking + joint limits + smoothness；
- 比较单帧 IK 和整段 trajectory optimization；
- 对轨迹注入噪声，观察平滑项对速度/加速度的影响。

证据：loss 曲线、关节轨迹和消融表。

## F5 论文和实验方法

学习：research question、baseline、ablation、metric、trial unit、reproducibility。

实操：重写论文方法流程，自己实现四个误差指标，为小型实验预先填写 hypothesis 和 primary metric。

证据：一页方法图、指标测试和实验卡。

## 学习顺序

F0 后，F1-F2 是必修。F3-F5 可以跟随论文阅读交替进行。不必先学完 F5 才开始读论文。
