# 小型重定向实验

## 实验问题

在不使用双臂、灵巧手和力传感器的情况下，人体肩-肘-腕轨迹能否通过机器人运动学与软约束优化，转换成连续、不越界的仿真机械臂轨迹？

## 保留与删减

保留：

- human-to-robot embodiment gap；
- 人体轨迹归一化与坐标对齐；
- FK/IK 与 joint limits；
- task tracking、肘部/手臂平面约束和 trajectory smoothness；
- MPJPE/末端误差、姿态误差、VE、AE 和越界比例。

删减：

- 双臂协同；
- 多指 hand retargeting；
- RGB-D 物体点云与 polytope contact；
- VLM 目标力与 MPC 力控；
- 真机 task success benchmark。

## 系统

```text
short human video or prepared skeleton sequence
    -> shoulder/elbow/wrist keypoints
    -> temporal filtering and confidence mask
    -> scale + frame normalization
    -> initial frame-wise IK
    -> trajectory optimization
         task tracking
         joint limits
         temporal smoothness
         optional arm-plane prior
    -> PyBullet playback
    -> metrics + ablation
```

## 实施阶段

### E0 合成轨迹

用平滑曲线生成肩-肘-腕轨迹，不接入视频。先验证坐标、IK、joint order、limits 和指标。

Gate：同一 seed 结果一致，不可达帧有明确状态。

### E1 已提取的人体轨迹

使用一段 HDF5/NPZ skeleton sequence，比较：

- frame-wise IK；
- IK + smoothness；
- IK + smoothness + arm-plane prior。

Gate：三种方法使用同一输入、机器人模型和指标。

### E2 短视频

录制或选择 10-30 秒简单手臂动作，提取肩、肘、腕。开始时可以使用现代姿态模型，不必先修复 FrankMocap。

Gate：低置信度/丢帧不会被静默当作真实轨迹。

### E3 报告

固定输出：

- 人体和机器人轨迹可视化；
- 关节角、速度和加速度图；
- tracking/VE/AE/joint-limit 表；
- smoothness 和 arm-plane 消融；
- 至少三个失败片段及原因。

## 不过度承诺

这个实验不能复现 DexTele 的跨拓扑图学习结论，也不能复现 ObjRetarget 的多指接触成功率。它的价值是让论文中的坐标、运动学、轨迹优化和评估指标真正运行起来。
